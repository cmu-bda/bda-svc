"""Export utilities."""

import datetime
import json
from pathlib import Path

from json_repair import repair_json

from bda_svc import constants


def to_dict(bda: str) -> dict:
    """Convert BDA string to dictionary.

    Args:
        bda: BDA analysis text.

    Returns:
        Dictionary form of BDA.

    Raises:
        ValueError: If BDA text cannot be parsed into a JSON dictionary.
    """
    # Preferred path: model already returned JSON text
    try:
        parsed = json.loads(repair_json(bda))
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass

    # TODO: Legacy fallback: parse old sectioned plaintext format.
    raise ValueError("Unable to parse BDA output into a JSON dictionary.")


def save_json(bda: str, image_path: str | Path, output_path: str | Path | None) -> None:
    """Save BDA as a JSON file.

    Args:
        bda: BDA analysis text.
        image_path: Path of the original image.
        output_path: Path of output folder. Uses default if None/empty.
    """
    image_path = Path(image_path)
    output_path = Path(output_path or constants.DEFAULT_OUTPUT_PATH)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d_%H%M%SZ")
    json_path = output_path / f"{image_path.stem}_{timestamp}.json"

    # Preserve raw model output if parse fails
    try:
        bda_dict = to_dict(bda)
    except ValueError as e:
        bda_dict = {
            "parse_error": str(e),
            "raw_output": bda,
        }

    with json_path.open("w", encoding="utf-8") as f:
        json.dump(bda_dict, f, indent=4)

    print(f"[*] Exported: {json_path}")
