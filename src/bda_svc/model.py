"""VLM model for BDA analysis."""

import ollama

from bda_svc.utilities import load_config, load_model


class VLM:
    """Vision-Language Model for BDA analysis."""

    def __init__(self):
        """Initialize VLM from config file."""
        config = load_config()
        self.model_name = config["model"]["vlm"]
        self.prompt = config["prompt"]
        load_model(self.model_name)

    def analyze_image(self, image_path: str) -> str:
        """Analyze an image and return BDA assessment.

        Args:
            image_path: Path to the image file.

        Returns:
            BDA assessment text from the model.
        """
        response = ollama.chat(
            model=self.model_name,
            messages=[{"role": "user", "content": self.prompt, "images": [image_path]}],
        )
        return response["message"]["content"]
