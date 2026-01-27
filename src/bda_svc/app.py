"""Main application entry point for BDA Service."""

from pathlib import Path

from bda_svc.model import VLM


def main() -> None:
    """Run BDA analysis on an image."""
    # Get image path from user
    # TODO: Create robot endpoint to avoid manually specifying path
    image_path = input("Enter image path: ").strip()
    if not Path(image_path).exists():
        raise FileNotFoundError(f"Image not found at {image_path}")
    print()

    # Initialize model
    vlm = VLM()

    # Run analysis
    result = vlm.analyze_image(image_path)

    # Display result
    # TODO: Create JSON output file
    print(result)

