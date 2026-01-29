"""Main application entry point for BDA Service."""

import argparse
import sys
from os import environ
from pathlib import Path

from bda_svc.model import BDAPipeline

# Global variables
ENV_INPUT_NAME = "BDA_INPUT"
DEFAULT_INPUT_PATH = "./bda_input"


def get_args() -> argparse.Namespace:
    """Retrieve argparse arguments.

    Returns
    -------
        argparse arguments (Namespace object)
    """
    bda_svc_desc = "Automated BDA service powered by machine-learning."

    parser = argparse.ArgumentParser(description=bda_svc_desc)

    parser.add_argument(
        "-i",
        "--input",
        help=f"path to input data. Overrides the '{ENV_INPUT_NAME}' environment variable",
    )

    return parser.parse_args()


def get_input_folder(cmdline_path: str) -> Path:
    """Retrieve input path and perform validation.

    Args:
    ----
        cmdline_path: Path to the input folder.

    Returns:
    -------
        Path of validated input folder
    """
    # Get command-line path argument (if provided)
    if cmdline_path:
        input_folder_str = cmdline_path
    else:
        # Get input path from ENV variable (or select default folder)
        input_folder_str = environ.get(ENV_INPUT_NAME, DEFAULT_INPUT_PATH)

    input_folder = Path(input_folder_str)

    # TODO: implement better logging
    print(f"[*] Input source set to {input_folder.resolve()}")

    # TODO: Create robot endpoint to avoid manually specifying path

    # Perform path validation
    if not input_folder.exists():
        # raise FileNotFoundError(f"Image not found at {input_path}\n")
        # Print to STDERR with exit code 1
        sys.exit(f"\nThe input path {input_folder} does not exist. Exiting.\n")

    return input_folder


def get_input_paths(input_folder: Path) -> list:
    """Retrieve paths to all input files.

    Args:
    ----
        input_folder: Path of input folder

    Returns:
    -------
        List containing file paths
    """
    files = []
    valid_ext = (".png", ".jpg", ".jpeg", ".bmp", ".tiff")
    patterns = [f"**/*{ext}" for ext in valid_ext]

    # Perform recursive file search
    for pattern in patterns:
        # NOTE: Need extend because glob returns a generator
        files.extend(input_folder.glob(pattern))

    if not files:
        sys.exit(
            f"\nThe input path {input_folder} "
            f"does not contain valid input data. Exiting.\n"
        )

    return files


def main() -> None:
    """Run BDA analysis on an image."""
    # Get command-line arguments (if any)
    args = get_args()

    # Get path to input folder
    input_folder = get_input_folder(args.input)

    input_paths = get_input_paths(input_folder)

    # Initialize model
    model = BDAPipeline()

    # Run analysis
    # TODO: Add additional loop logic when parsing multiple files
    for input_path in input_paths:
        print(f"\nProcessing: {input_path}\n{'-' * 80}")

        result = model.analyze(input_path)

        # Display result
        # TODO: Create JSON output file
        print(f"{result}\n")
