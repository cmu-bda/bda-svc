"""Main application entry point for BDA Service."""

import argparse
from os import environ
from pathlib import Path
from sys import exit

from bda_svc.model import VLM

# TODO: Establish config file
# Global variables
ENV_INPUT_NAME = "BDA_INPUT"
DEFAULT_INPUT_PATH = "./bda_input"


def get_args() -> argparse.Namespace:
    """Retrieve argparse arguments."""
    bda_svc_desc = "Automated BDA service powered by machine-learning"

    parser = argparse.ArgumentParser(description=bda_svc_desc)

    parser.add_argument(
        "-i",
        "--input",
        help=f"path to input data. Overrides the '{ENV_INPUT_NAME}' environment variable",
    )

    return parser.parse_args()


def get_input_path(cmdline_path: str) -> str:
    """Retrieve input path."""
    # Get command-line path argument (if provided)
    if cmdline_path:
        input_path = cmdline_path
    else:
        # Get input path from ENV variable (or select default folder)
        input_path = environ.get(ENV_INPUT_NAME, DEFAULT_INPUT_PATH)

    # TODO: implement better logging
    print("[*] Retrieving input from", input_path)

    # TODO: Create robot endpoint to avoid manually specifying path

    # Perform path validation
    if not Path(input_path).exists():
        # raise FileNotFoundError(f"Image not found at {input_path}\n")
        # Print to STDERR with exit code 1
        exit(f"\nThe input path {input_path} does not exist. Exiting.\n")

    return input_path


def main() -> None:
    """Run BDA analysis on an image."""
    # Get command-line arguments (if any)
    args = get_args()

    # Get path to input folder
    input_path = get_input_path(args.input)

    # Initialize model
    vlm = VLM()

    # Run analysis
    result = vlm.analyze_image(input_path)

    # Display result
    # TODO: Create JSON output file
    print(result)
