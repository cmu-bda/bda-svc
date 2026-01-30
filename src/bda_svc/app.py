"""Main application entry point for BDA Service."""

from bda_svc import cli, export, inputs
from bda_svc.model import BDAPipeline


def main() -> None:
    """Run BDA analysis on an image."""
    # Get command-line arguments (if any)
    args = cli.get_args()

    # Get input data
    input_folder = inputs.get_input_folder(args.input)

    input_paths = inputs.get_input_paths(input_folder)

    # Initialize model
    model = BDAPipeline()

    # Run analysis
    for input_path in input_paths:
        print(f"\nProcessing: {input_path}\n{'-' * 80}")

        result = model.analyze(input_path)

        # Display result
        print(f"{result}\n")

        # Export to JSON file
        export.save_json(result, input_path, args.output)
