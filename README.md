# bda-svc

`bda-svc` is an automated Battle Damage Assessment (BDA) service for imagery. It uses vision-language models to detect targets, assess visible physical damage, and produce structured JSON reports.

![Diagram](https://github.com/user-attachments/assets/5dbd6987-7653-4948-8f8a-f326d3ac6df3)

## Quick Start

1. [Install uv](https://docs.astral.sh/uv/getting-started/installation/)

2. Start an OpenAI-compatible vision-language model server such as [vLLM](https://docs.vllm.ai/en/latest/getting_started/installation/) or [Ollama](https://ollama.com/download).

```bash
   # vLLM server
   vllm serve Qwen/Qwen3-VL-8B-Instruct

   # Ollama server
   ollama serve
   ollama pull qwen3-vl:8b-instruct
```

3. Set the server URL:

```bash
   # Set one of the following depending on your server
   export OPENAI_BASE_URL=http://localhost:8000/v1   # vLLM default
   export OPENAI_BASE_URL=http://localhost:11434/v1  # Ollama default
```

4. Clone the repository and install dependencies:

```bash
   git clone <repository-url>
   cd bda-svc
   uv sync
```

5. Run the service:

```bash
   uv run bda-svc
```

## Usage

Show command-line help:

```bash
uv run bda-svc -h
```

Run using the default input folder:

```bash
uv run bda-svc
```

Run on a single image:

```bash
uv run bda-svc -i /path/to/image.ext
```

Run on a folder of images:

```bash
uv run bda-svc -i /path/to/folder
```

If no input path is provided, `bda-svc` defaults to `./bda_input`.

## Configuration

The model and pipeline settings are configured in [`src/bda_svc/pipeline/config.yaml`](src/bda_svc/pipeline/config.yaml).

The following environment variables control the backend connection:

| Variable | Default | Description |
|---|---|---|
| `OPENAI_BASE_URL` | `http://localhost:8000/v1` | OpenAI-compatible server URL |
| `OPENAI_API_KEY` | `no-auth` | API key if required by the server |
| `BDA_DETECTION_MODEL` | config.yaml value | Override the detection model |
| `BDA_ASSESSMENT_MODEL` | config.yaml value | Override the assessment model |

## Output

Reports are written to `bda_output/` as JSON files.

Each report includes:

- `metadata`
- `physical_damage`
- `summary`

At a high level, `physical_damage` contains one entry per assessed target, including:

- `target_type`
- `damage_category`
- `confidence_level`
- `brief_supporting_logic`
- `bounding_box`

## Container

A container image can be built from `docker/Dockerfile` for running `bda-svc` in a containerized environment. The container connects to an external model server via `OPENAI_BASE_URL`.

## Documentation

Full documentation is published at [cmu-bda.github.io/bda-svc](https://cmu-bda.github.io/bda-svc/) and lives in the [`docs/`](docs/) directory.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for contribution guidelines.

## License

This project is licensed under the Apache License 2.0. See [`LICENSE`](LICENSE) for details.