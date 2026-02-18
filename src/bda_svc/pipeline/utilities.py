"""A collection of model utility functions."""

from pathlib import Path

import torch
import transformers
import yaml

CONFIG_PATH = Path(__file__).parent / "config.yaml"
DOCTRINE_PATH = Path(__file__).parent / "doctrine.yaml"


def test_gpu() -> None:
    """Verify hardware acceleration and library versions."""
    print(f"Transformers Version: {transformers.__version__}")
    print(f"PyTorch Version: {torch.__version__}")

    cuda_available = torch.cuda.is_available()
    if cuda_available:
        print(f"CUDA Version: {torch.version.cuda}")
        print(f"Device: {torch.cuda.get_device_name()}")
    else:
        print("WARNING: CUDA not found.")


def load_yaml(path: Path) -> dict:
    """Load file from YAML.

    Args:
        path: Path to YAML file.

    Returns:
        A dictionary with loaded YAML.
    """
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data


def format_pda_doctrine(categories: list[str]) -> str:
    """Format PDA doctrine for selected target categories.

    Args:
        categories: A list of doctrinal BDA target categories.

    Returns:
        A doctrinal PDA string in the format:
            - Target Category
            - Physical Damage Definitions
            - Physical Damage Considerations
    """
    doctrine = load_yaml(DOCTRINE_PATH)
    output = []

    for key in categories:
        entry = doctrine.get(key)
        if not isinstance(entry, dict):
            continue
        title = key.replace("_", " ").upper()
        output.append(f"TARGET CATEGORY: {title}")

        for section_key in [
            "physical_damage_definitions",
            "physical_damage_considerations",
        ]:
            section_entry = entry.get(section_key)
            if section_entry is None:
                continue
            section_title = section_key.replace("_", " ").upper()
            output.append(f"{title} {section_title}")
            output.append(str(section_entry).strip())

    return "\n".join(output).strip() if output else "NO TARGET DOCTRINE AVAILABLE."
