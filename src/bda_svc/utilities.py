"""A collection of utilities functions."""

import subprocess
from pathlib import Path

import yaml


def load_config() -> dict:
    """Load configuration file from config.yaml.

    Returns:
        A dictionary containing configuration settings.
    """
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config


def load_model(model_name: str) -> None:
    """Ensure Ollama model is available, pull if missing.

    Args:
        model_name: Name of the Ollama model to check/pull.
    """
    result = subprocess.run(["ollama", "list"], capture_output=True, text=True)

    if model_name not in result.stdout:
        print(f"Pulling model: '{model_name}'")
        subprocess.run(["ollama", "pull", model_name], check=True)
