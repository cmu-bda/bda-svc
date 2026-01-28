# Overview

VLMs for Autonomous Battle Damage Assessment.

![Diagram](https://github.com/user-attachments/assets/5dbd6987-7653-4948-8f8a-f326d3ac6df3)

# Development Setup

1. [**Install Ollama**](https://ollama.com/download)

2. [**Install uv**](https://docs.astral.sh/uv/getting-started/installation/)

3. **Clone the repository and install dependencies**:
   ```bash
   git clone <repository-url>
   cd bda-svc
   uv sync --dev
   ```

4. **Install pre-commit hooks**:
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
   
> [!NOTE]
> If the image folder path is not specified, bda-svc will default to using `./bda_input`.
<br />

# Project Structure
```
├── .github/              # CI/CD development folder
├── src/
│   └── bda_svc/
│       ├── __init__.py
│       └── app.py         # Main analysis script
│       └── config.yaml    # Model / Prompt selection
│       └── model.py       # Machine learning models
│       └── utilities.py   # Shared utilities
│   └── robot/
│       └── containers/     # Docker / containerization
│       └── api/            # If needed for robot communication
├── tests/
├── pyproject.toml
├── uv.lock
└── README.md
```
