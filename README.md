# Overview

VLMs for Autonomous Battle Damage Assessment.

![Diagram](https://github.com/user-attachments/assets/5dbd6987-7653-4948-8f8a-f326d3ac6df3)

# Development Setup

1. [**Install uv**](https://docs.astral.sh/uv/getting-started/installation/)

2. **Clone the repository and install dependencies**
   ```bash
   git clone <repository-url>
   cd bda-svc
   uv sync --dev
   source .venv/bin/activate
   ```

3. **Install pre-commit hooks**
   ```bash
   uv run pre-commit install
   ```

# Usage

1. **For complete usage information**:
   ```bash
   uv run bda-svc -h
   ```

2. **Run the BDA service with a command-line image or folder path (override environment variable)**:
   ```bash
   uv run bda-svc -i /path/to/image.ext

   # or
   
   uv run bda-svc -i /path/to/folder
   ```

3. **Alternatively, run the BDA service with an environment variable**:
   ```bash
   BDA_INPUT="/path/to/images" uv run bda-svc
   ```

# Project Structure

```
├── .github/                   # CI/CD workflows
├── src/
│   └── bda_svc/
│       ├── __init__.py
│       ├── app.py             # Main application entrypoint
│       ├── cli.py             # Command-line argument parsing
│       ├── constants.py       # Shared constants
│       ├── export.py          # JSON export utilities
│       ├── inputs.py          # Input path validation/discovery
│       └── pipeline/
│           ├── __init__.py
│           ├── config.yaml    # VLM + prompt configuration
│           ├── doctrine.yaml  # Doctrinal definitions
│           ├── model.py       # BDAPipeline + VLMRunner + DetectorRunner
│           └── utilities.py   # Pipeline helper functions
├── tests/                     # Test suite
├── pyproject.toml
├── uv.lock
└── README.md
```

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

