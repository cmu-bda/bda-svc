"""Command-line functionality."""

import argparse

from bda_svc import constants


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
        help=f"path to input data. Overrides the "
        f"'{constants.ENV_INPUT_NAME}' environment variable",
    )

    return parser.parse_args()
