"""Object Detection and Vision-Language Model BDA pipeline."""

import warnings
from dataclasses import dataclass
from pathlib import Path

import torch
from huggingface_hub import snapshot_download
from PIL import Image
from transformers import AutoModelForImageTextToText, AutoProcessor, BitsAndBytesConfig

from bda_svc.pipeline.utilities import (
    CONFIG_PATH,
    DOCTRINE_PATH,
    format_fda_doctrine,
    format_pda_doctrine,
    load_yaml,
)

warnings.filterwarnings(
    "ignore",
    message=r"MatMul8bitLt: inputs will be cast from .* to float16 during quantization",
    category=UserWarning,
)


@dataclass(frozen=True)
class Detection:
    """Lightweight record for detection output."""

    label: str
    score: float | None = None
    box: tuple[int, int, int, int] | None = None
    crop: Image.Image | None = None


class DetectorRunner:
    """Default detector that returns no detections."""

    def detect(self, image: Image.Image) -> list[Detection]:
        """Return an empty detection list."""
        return []


class VLMRunner:
    """Wrapper around a Hugging Face VLM."""

    def __init__(
        self,
        model_id: str,
        load_kwargs: dict | None = None,
        generate_kwargs: dict | None = None,
        quantization_kwargs: dict | None = None,
    ) -> None:
        """Initialize the VLM runner.

        Args:
            model_id: Hugging Face model identifier.
            load_kwargs: VLM loading from config.yaml.
            generate_kwargs: VLM generation from config.yaml.
            quantization_kwargs: VLM quantization from config.yaml.

        Notes:
            Loads model artifacts from the `models/` directory.
            If local artifacts are missing or incomplete, downloads the
            snapshot into `models/` and retries local loading.

        Raises:
            RuntimeError: If model loading succeeds but any modules are
                offloaded to CPU.
        """
        # Configuration blocks
        self.load_kwargs = load_kwargs or {}
        self.generate_kwargs = generate_kwargs or {}
        self.quantization_kwargs = quantization_kwargs or {}

        # Quantization configuration
        def _build_quantization_config() -> BitsAndBytesConfig | None:
            if not self.quantization_kwargs.get("enabled", True):
                return None
            load_in_4bit = bool(self.quantization_kwargs.get("load_in_4bit", False))
            load_in_8bit = bool(self.quantization_kwargs.get("load_in_8bit", False))
            return BitsAndBytesConfig(
                load_in_4bit=load_in_4bit,
                load_in_8bit=load_in_8bit,
            )

        quantization_config = _build_quantization_config()
        if quantization_config is not None:
            self.load_kwargs.pop("dtype", None)

        # Anchor model storage to repo root
        repo_root = Path(__file__).resolve().parents[3]
        local_model_dir = repo_root / "models" / model_id.replace("/", "--")
        local_model_dir.mkdir(parents=True, exist_ok=True)

        def _load_local() -> None:
            self.processor = AutoProcessor.from_pretrained(
                local_model_dir,
                local_files_only=True,
                use_fast=True,
                min_pixels=256 * 28 * 28,
                max_pixels=1280 * 28 * 28,
            )
            model_kwargs = dict(self.load_kwargs)
            if quantization_config is not None:
                model_kwargs["quantization_config"] = quantization_config
            self.model = AutoModelForImageTextToText.from_pretrained(
                local_model_dir,
                local_files_only=True,
                **model_kwargs,
            )

        try:
            # Load from local models directory
            _load_local()
        except OSError:
            # Download to local models directory, then load from there
            snapshot_download(model_id, local_dir=local_model_dir)
            _load_local()

        self.model.eval()

        # Fail fast if any module is offloaded to CPU
        device_map = getattr(self.model, "hf_device_map", None)
        if device_map:
            off_gpu_modules = [
                name
                for name, dev in device_map.items()
                if not str(dev).isdigit() and not str(dev).startswith("cuda:")
            ]
            if off_gpu_modules:
                raise RuntimeError(
                    "Model did not fully fit on GPU; CPU offload detected. "
                    "Adjust dtype/quantization/model size before running inference."
                )

    def generate(
        self, image: Image.Image, prompt: str, system_prompt: str | None
    ) -> str:
        """Generate a response from the VLM.

        Args:
            image: PIL image to analyze.
            prompt: User prompt text.
            system_prompt: Optional system prompt.

        Returns:
            Model response text.
        """
        # Build a chat-style prompt when the processor supports it
        if hasattr(self.processor, "apply_chat_template"):
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {"type": "image"},
                        {"type": "text", "text": prompt},
                    ],
                }
            )
            text = self.processor.apply_chat_template(
                messages, add_generation_prompt=True
            )
        else:
            text = "\n\n".join(part for part in [system_prompt, prompt] if part)

        # Tokenize inputs and move them to the model's device
        inputs = self.processor(images=image, text=text, return_tensors="pt")
        device = next(self.model.parameters()).device
        inputs = inputs.to(device)
        input_ids = inputs.get("input_ids")

        # Keep only newly generated tokens (drop the prompt)
        with torch.inference_mode():
            output_ids = self.model.generate(**inputs, **self.generate_kwargs)

        if input_ids is not None:
            output_ids = output_ids[:, input_ids.shape[-1] :]

        generated_text = self.processor.decode(output_ids[0], skip_special_tokens=True)

        return generated_text


class BDAPipeline:
    """BDA pipeline combining object detection and VLM inference."""

    def __init__(self, detector: DetectorRunner | None = None) -> None:
        """Initialize configuration, doctrine, prompts, and models.

        Args:
            detector: Optional detector with a .detect(image) method.
        """
        # Load config / doctrine yamls
        config = load_yaml(CONFIG_PATH)
        doctrine = load_yaml(DOCTRINE_PATH)

        # Load all prompts
        self.system_prompt = config["prompts"]["system"]

        self.classify_prompt = config["prompts"]["classify"]
        reserved = {"functional_damage_definitions"}
        self.categories = [k for k in doctrine.keys() if k not in reserved]
        self.classify_prompt = self.classify_prompt.replace(
            "{categories}", ", ".join(self.categories)
        )

        self.report_prompt = config["prompts"]["report"]

        # Load models
        vlm_cfg = config.get("vlm")
        vlm_id = vlm_cfg.get("model-id")
        load_kwargs = vlm_cfg.get("load", {})
        generate_kwargs = vlm_cfg.get("generate", {})
        quantization_kwargs = vlm_cfg.get("quantization", {})
        self.vlm = VLMRunner(
            model_id=vlm_id,
            load_kwargs=load_kwargs,
            generate_kwargs=generate_kwargs,
            quantization_kwargs=quantization_kwargs,
        )

        self.detector = detector

    def detect_objects(self, image: Image.Image) -> list[Detection]:
        """Return detected objects from detector or VLM.

        Args:
            image: PIL image to analyze.

        Returns:
            List of detections with category labels.
        """
        # Use object detector if provided
        if self.detector is not None:
            return self.detector.detect(image)

        # Else use VLM with the classify prompt
        response = self.vlm.generate(
            image=image,
            prompt=self.classify_prompt,
            system_prompt=self.system_prompt,
        )

        # Normalize and keep only valid doctrine categories
        if not response or not response.strip():
            return []

        labels = []
        for raw in response.replace("\n", ",").split(","):
            label = raw.strip().strip('"').strip("'").lower()
            if label in self.categories and label not in labels:
                labels.append(label)

        return [Detection(label=label) for label in labels]

    def format_report_prompt(self, detections: list[Detection]) -> str:
        """Format report prompt with doctrine for detected labels.

        Args:
            detections: List of detections with category labels.

        Returns:
            Report prompt with `categories` and `doctrine` populated.
        """
        categories = [det.label for det in detections if det.label]

        doctrine = "\n\n".join(
            part
            for part in [
                format_pda_doctrine(categories),
                format_fda_doctrine(),
            ]
            if part
        ).strip()

        categories_text = ", ".join(categories) if categories else "NONE"
        output = self.report_prompt.replace("{categories}", categories_text)
        output = output.replace("{doctrine}", doctrine)
        return output

    def analyze(self, image_path: str | Path) -> str:
        """Run the full BDA pipeline and return a scene-wide assessment.

        Args:
            image_path: Path to the image file to analyze.

        Returns:
            Model-generated BDA assessment text for the full scene.
        """
        with Image.open(Path(image_path)) as image:
            image = image.convert("RGB")
            detections = self.detect_objects(image)
            prompt = self.format_report_prompt(detections)
            return self.vlm.generate(
                image=image,
                prompt=prompt,
                system_prompt=self.system_prompt,
            )
