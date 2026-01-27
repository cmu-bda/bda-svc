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

# Project Structure
```
├── .github/              # CI/CD development 
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
