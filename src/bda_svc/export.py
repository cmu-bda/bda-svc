"""Export utilities."""

import datetime
import json
from pathlib import Path

from bda_svc import constants


def to_dict(bda: str) -> dict:
    """Converts BDA string to dictionary.

    Args:
    ----
        bda: BDA analysis text

    Returns:
    -------
        Dictionary form of BDA
    """
    bda_dict = {}
    key = "unset"

    for line in bda.splitlines():
        line = line.strip()

        match line:
            case "PHYSICAL DAMAGE ASSESSMENT:":
                key = "physical"

            case "FUNCTIONAL DAMAGE ASSESSMENT:":
                key = "functional"

            case "TASK ASSESSMENT:":
                key = "assessment"

            case "THREAT LEVEL RECOMMENDATION:":
                key = "recommendation"

            case _:
                if line.startswith("- "):
                    # Insert key with a value set to inner dict
                    bda_dict.setdefault(key, {})

                    try:
                        # Split on (only the first) colon
                        label, analysis = line[2:].split(": ", 1)

                        bda_dict[key][label.lower()] = analysis
                    except Exception:
                        return {}

    return bda_dict


def save_json(bda: str, image_path: Path, output_path_str: str) -> None:
    """Saves BDA as a JSON file.

    Args:
    ----
        bda: Battle Damage Assessment.
        image_path: Path of the original image
        output_path_str: Path of output folder

    Returns:
    -------
        None
    """
    # NOTE: Manually check output_path_str (bug setting default)
    if not output_path_str:
        output_path_str = constants.DEFAULT_OUTPUT_PATH

    # Create the directory if necessary (as well as missing subdirectories)
    output_path = Path(output_path_str)
    output_path.mkdir(parents=True, exist_ok=True)

    # Generate full JSON filename
    dt = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d_%H%M%SZ")
    json_path = f"{output_path}/{image_path.stem}_{dt}.json"

    # Convert BDA string to dict
    bda_dict = to_dict(bda)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(bda_dict, f, indent=4)

    print(f"[*] Exported: {json_path}")
