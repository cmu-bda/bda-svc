"""Object Detection and Vision-Language Model BDA pipeline."""

import warnings
from dataclasses import dataclass
from pathlib import Path

import torch
import transformers
from huggingface_hub import snapshot_download
from PIL import Image
from transformers import BitsAndBytesConfig, pipeline

from bda_svc.pipeline.utilities import (
    CONFIG_PATH,
    DOCTRINE_PATH,
    format_fda_doctrine,
    format_pda_doctrine,
    load_yaml,
)

transformers.utils.logging.set_verbosity_error()
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
        pipeline_kwargs: dict | None = None,
        quantization_kwargs: dict | None = None,
    ) -> None:
        """Initialize the VLM runner.

        Args:
            model_id: Hugging Face model identifier.
            pipeline_kwargs: VLM pipeline parameters.
            quantization_kwargs: VLM quantization parameters.

        Notes:
            Loads model artifacts from the `models/` directory.
            If local artifacts are missing or incomplete, downloads the
            snapshot into `models/` and retries local loading.
        """
        # Configuration blocks
        self.pipeline_kwargs = pipeline_kwargs or {}
        self.quantization_kwargs = quantization_kwargs or {}

        # Load model, download if missing
        repo_root = Path(__file__).resolve().parents[3]
        local_model_dir = repo_root / "models" / model_id.replace("/", "--")
        local_model_dir.mkdir(parents=True, exist_ok=True)

        def _load_local() -> None:
            model_kwargs = {}
            if quantization_kwargs.get("enabled", False):
                model_kwargs["quantization_config"] = BitsAndBytesConfig(
                    load_in_8bit=bool(quantization_kwargs.get("load_in_8bit", False)),
                    load_in_4bit=bool(quantization_kwargs.get("load_in_4bit", False)),
                )
            self.pipeline = pipeline(
                task="image-text-to-text",
                model=local_model_dir,
                model_kwargs=model_kwargs,
                **pipeline_kwargs,
            )

        try:
            # Load from local models directory
            _load_local()
        except OSError:
            # Download to local models directory, then load from there
            snapshot_download(model_id, local_dir=local_model_dir)
            _load_local()

        self.pipeline.model.eval()

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
        # Build a chat-style prompt
        messages = []
        if system_prompt:
            messages.append(
                {"role": "system", "content": [{"type": "text", "text": system_prompt}]}
            )
        messages.append(
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": prompt},
                ],
            }
        )

        # Return response
        with torch.inference_mode():
            response = self.pipeline(messages, return_full_text=False)

        return response[0]["generated_text"]


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
        pipeline_kwargs = vlm_cfg.get("pipeline-kwargs", {})
        quantization_kwargs = vlm_cfg.get("quantization-kwargs", {})
        self.vlm = VLMRunner(
            model_id=vlm_id,
            pipeline_kwargs=pipeline_kwargs,
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
            if label in self.categories:
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
                format_pda_doctrine(list(set(categories))),
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
