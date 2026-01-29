"""Object Detection and Vision-Language Model implementation."""

import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile

import ollama
import torch
import yaml
from PIL import Image
from transformers import AutoImageProcessor, pipeline

# TODO:
#   - Suppress Hugging Face loading?
#   - Links to 'acceptable' models?
#   - Hyperparameter tuning for object detection confidence
#   - Delete temporary images
#   - Evaluate value of full image vs text-only object detection


class BDAPipeline:
    """BDA pipeline combining object detection and VLM."""

    def __init__(self):
        """Initialize pipeline from config file."""
        # Load config
        config_path = Path(__file__).parent / "config.yaml"
        with open(config_path, encoding="utf-8") as f:
            config = yaml.safe_load(f)

        # Load models
        self.detector = ObjectDetector(
            model_id=config["object-detector"]["model-id"],
            text_labels=config["object-detector"]["text-labels"],
        )
        self.vlm = VLM(
            model_id=config["vlm"]["model-id"],
            system_prompt=config["vlm"]["system-prompt"],
        )

    def analyze(self, image_path: str) -> str:
        """Run full analysis pipeline on image file.

        Args:
        ----
            image_path: Path to image file.

        Returns:
        -------
            Model analysis text.
        """
        image = Image.open(image_path)
        detection_results = self.detector.detect(image)
        vlm_results = self.vlm.analyze_image(image, detection_results)
        return vlm_results


class ObjectDetector:
    """A zero-shot object detection model."""

    def __init__(
        self,
        model_id: str,
        text_labels: list[str],
        detection_threshold: float = 0.4,
    ) -> None:
        """Initializes the object detector with a pre-trained model.

        Args:
        ----
            model_id: Hugging Face model identifier.
            text_labels: What the model should recognize in the image.
            detection_threshold: Minimum confidence for detections.
        """
        # Class attributes
        self.device = 0 if torch.cuda.is_available() else -1
        self.model_id = model_id
        self.text_labels = text_labels
        self.detection_threshold = detection_threshold

        # Load pipeline
        try:
            self.processor = AutoImageProcessor.from_pretrained(
                self.model_id, use_fast=True
            )
            self.model = pipeline(
                model=self.model_id,
                task="zero-shot-object-detection",
                image_processor=self.processor,
                device=self.device,
            )
        except Exception:
            print(
                f"{self.model_id} is not a local folder and is not a valid model "
                "identifier listed on 'https://huggingface.co/models'"
            )

    def detect(self, image: Image.Image) -> list[dict]:
        """Detect objects in an image.

        Extract labels, confidence, and cropped bounding boxes.

        Args:
        ----
            image: PIL Image to analyze.

        Returns:
        -------
            A list of dictionaries containing the label, confidence,
            and cropped image for each detected bounding box.
        """
        detection_results = self.model(
            image, candidate_labels=self.text_labels, threshold=self.detection_threshold
        )

        output = []
        for detection in detection_results:
            label = detection["label"]
            confidence = detection["score"]
            xmin, ymin, xmax, ymax = detection["box"].values()
            crop = image.crop((xmin, ymin, xmax, ymax))
            output.append({"label": label, "confidence": confidence, "crop": crop})

        return output


class VLM:
    """A Vision-Language Model using object detection input."""

    def __init__(self, model_id: str, system_prompt: str):
        """Initializes the VLM with a pre-trained model.

        Args:
        ----
            model_id: Ollama model identifier.
            system_prompt: Global model prompt.
        """
        # Ensure Ollama model is available, pull if missing
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if model_id not in result.stdout:
            try:
                print(f"Pulling model: '{model_id}'")
                subprocess.run(["ollama", "pull", model_id], check=True)
            except subprocess.CalledProcessError:
                return

        self.model_id = model_id
        self.system_prompt = system_prompt

    @staticmethod
    def _save_temp_image(image: Image.Image) -> str:
        """Save PIL image to a temporary file and return its path.

        Args:
        ----
            image: PIL Image to save.

        Returns:
        -------
            A path to the temporary image.
        """
        tmp = NamedTemporaryFile(suffix=".png", delete=False)
        image.save(tmp.name)
        return tmp.name

    def analyze_image(self, image: Image.Image, detection_results: list[dict]) -> str:
        """Analyze image with object detection results.

        Args:
        ----
            image: PIL Image to analyze.
            detection_results: Object detection results.

        Returns:
        -------
            Model's text response.
        """
        # Start with system prompt and full scene
        messages = [
            {
                "role": "system",
                "content": self.system_prompt,
            },
            {
                "role": "user",
                "content": "This is the image of the full scene to analyze.",
                "images": [self._save_temp_image(image)],
            },
        ]

        # Add each detected object as a separate message
        if detection_results:
            for i, detection in enumerate(detection_results):
                messages.append(
                    {
                        "role": "user",
                        "content": (
                            "This is a cropped object detection of the same scene. "
                            f"Possible Detection {i + 1}: {detection['label']}. "
                        ),
                        "images": [self._save_temp_image(detection["crop"])],
                    }
                )

        # Final prompt requesting comprehensive analysis
        messages.append(
            {
                "role": "user",
                "content": "REPORT BDA",
            }
        )

        response = ollama.chat(model=self.model_id, messages=messages)
        return response["message"]["content"]
