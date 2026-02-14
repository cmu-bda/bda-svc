"""Object Detection and Vision-Language Model BDA pipeline."""

from dataclasses import dataclass
from pathlib import Path

import torch
from huggingface_hub import snapshot_download
from PIL import Image
from transformers import AutoModelForImageTextToText, AutoProcessor

from bda_svc.pipeline.utilities import (
    CONFIG_PATH,
    DOCTRINE_PATH,
    format_fda_doctrine,
    format_pda_doctrine,
    load_yaml,
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

    def __init__(self, model_id: str, model_kwargs: dict | None = None) -> None:
        """Initialize the VLM runner.

        Args:
            model_id: Hugging Face model identifier.
            model_kwargs: VLM configuration fields from config.yaml.

        Notes:
            Loads model artifacts from the`models/` directory.
            If local artifacts are missing or incomplete, downloads the
            snapshot into `models/` and retries local loading.
        """
        self.model_kwargs = model_kwargs or {}

        # Anchor model storage to repo root
        repo_root = Path(__file__).resolve().parents[3]
        local_model_dir = repo_root / "models" / model_id.replace("/", "--")
        local_model_dir.mkdir(parents=True, exist_ok=True)

        def _load_local() -> None:
            self.processor = AutoProcessor.from_pretrained(
                local_model_dir, local_files_only=True, use_fast=True
            )
            self.model = AutoModelForImageTextToText.from_pretrained(
                local_model_dir,
                device_map="auto",
                local_files_only=True,
            )

        try:
            # Load from local models directory
            _load_local()
        except Exception:
            # Download to local models directory, then load from there
            snapshot_download(model_id, local_dir=local_model_dir)
            _load_local()

        self.model.eval()

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
            output_ids = self.model.generate(**inputs, **self.model_kwargs)

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
        vlm_kwargs = {k: v for k, v in vlm_cfg.items() if k != "model-id"}
        self.vlm = VLMRunner(model_id=vlm_id, model_kwargs=vlm_kwargs)

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
