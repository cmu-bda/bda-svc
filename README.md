# Overview

VLMs for Autonomous Battle Damage Assessment.

![Diagram](https://github.com/user-attachments/assets/5dbd6987-7653-4948-8f8a-f326d3ac6df3)

# Development Setup

1. [**Install uv**](https://docs.astral.sh/uv/getting-started/installation/):

2. **Clone the repository and install dependencies**:
   ```bash
   git clone <repository-url>
   cd bda-svc
   uv sync --dev
   ```

3. **Install pre-commit hooks**:
   ```bash
   uv run pre-commit install
   ```

### Common Commands

#### Managing Dependencies

```bash
# Add a new package
uv add <package>

# Add a development dependency
uv add --dev <package>

# Sync dependencies from pyproject.toml
uv sync
```

#### Running the Application

```bash
# Run the main application
uv run bda-svc

# Run any Python script
uv run python src/bda_svc/script.py
```

#### Code Quality

```bash
# Format all files
uv run ruff format .

# Lint all files
uv run ruff check .

# Lint and auto-fix issues
uv run ruff check --fix .

# Run all pre-commit hooks manually
uv run pre-commit run --all-files
```

# Project Structure
```
├── src/
│   └── bda_svc/
│       ├── __init__.py
│       └── detection/      # Object detection models
│       └── vlm/            # VLM inference models
│       └── preprocessing/  # Image processing
│       └── postprocessing/ # BDA formatting
│       └── utils/          # Shared utilities
│   └── robot/
│       └── containers/     # Docker / containerization
│       └── api/            # If needed for robot communication
├── tests/
├── pyproject.toml
├── uv.lock
└── README.md
```
