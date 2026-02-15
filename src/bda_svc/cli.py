"""Command-line functionality."""

import argparse


def get_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed command-line arguments.
    """
    bda_svc_desc = "Automated BDA service powered by machine learning."

    parser = argparse.ArgumentParser(description=bda_svc_desc)

    parser.add_argument(
        "-i",
        "--input",
        type=str,
        help=("Path to input image file or folder."),
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help=("Path to output folder."),
    )

    return parser.parse_args()
