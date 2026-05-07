# Containers

This document describes how to build, pull, and run the `bda-svc` container across different environments.

---

## Prerequisites

Before building or running the container, ensure the following are installed:

- Docker Engine or Docker Desktop
- Docker Buildx (for multi-architecture builds)
- Git
- Access to GitHub Container Registry (GHCR), if pulling images
- A running OpenAI-compatible model server such as vLLM or Ollama
- A local directory containing input images

---

## Quick Start (First-Time Users)

Create directories and pull container:

```bash
# create local folders for input/output
mkdir -p images outputs

# pull the latest image
docker pull ghcr.io/cmu-bda/bda-svc:latest
```

Run the container:

```bash
docker run --rm \
  -e OPENAI_BASE_URL=http://<MODEL_SERVER_IP>:8000/v1 \
  -v $(pwd)/images:/input \
  -v $(pwd)/outputs:/output \
  ghcr.io/cmu-bda/bda-svc:latest \
  -i /input \
  -o /output
```
Set `OPENAI_BASE_URL` based on the model server being used:

* vLLM: http://<MODEL_SERVER_IP>:8000/v1
* Ollama: http://<MODEL_SERVER_IP>:11434/v1
* WSL/Docker Desktop with Ollama on the host: http://host.docker.internal:11434/v1
* WSL/Docker Desktop with vLLM on the host: http://host.docker.internal:8000/v1



---

## Container Build (Local Development)

### ARM64 (Jetson / ARM systems)

```bash
docker buildx build \
  --platform linux/arm64 \
  -f <DOCKERFILE_PATH> \
  -t <IMAGE_NAME> \
  <BUILD_CONTEXT> \
  --load
```

### x86 (Standard desktop/laptop)

```bash
docker build \
  -f <DOCKERFILE_PATH> \
  -t <IMAGE_NAME> \
  <BUILD_CONTEXT>
```

---

## Pulling Container from GitHub Container Registry

Images are published here:
[https://github.com/cmu-bda/bda-svc/pkgs/container/bda-svc](https://github.com/cmu-bda/bda-svc/pkgs/container/bda-svc)

```bash
docker pull --platform linux/arm64 ghcr.io/cmu-bda/bda-svc:latest
```

---

## Running the Container

### Mounting Input / Output Directories

The container requires two mounted directories:

* `/input` → images to process
* `/output` → generated results

Example (host vs container path labeling):

```bash
# Format: -v <HOST_PATH>:<CONTAINER_PATH>

-v $(pwd)/images:/input   # HOST: ./images  -> CONTAINER: /input
-v $(pwd)/outputs:/output # HOST: ./outputs -> CONTAINER: /output
```

**Format:**

* syntax: `<host path>:<container path>`
* Left side = your machine
* Right side = inside the container

Example:

* `$(pwd)/images` → your files live here
* `/input` → container reads from here

If using absolute paths:

```bash
-v /home/user/data/images:/input
-v /home/user/data/outputs:/output
```

---

### Local Container Testing

#### Linux (Model server on localhost)

```bash
docker run --rm --network host \
  -e OPENAI_BASE_URL=http://localhost:8000/v1 \
  -v <HOST_INPUT_DIR>:/input \
  -v <HOST_OUTPUT_DIR>:/output \
  <IMAGE_NAME> \
  -i /input \
  -o /output
```

---

#### WSL / Docker Desktop (Model server on localhost)

```bash
docker run --rm \
  -e OPENAI_BASE_URL=http://host.docker.internal:8000/v1 \
  -v <HOST_INPUT_DIR>:/input \
  -v <HOST_OUTPUT_DIR>:/output \
  <IMAGE_NAME> \
  -i /input \
  -o /output
```

---

#### Remote Model Server

```bash
docker run --rm \
  -e OPENAI_BASE_URL=http://<REMOTE_SERVER_IP>:<PORT>/v1 \
  -v <HOST_INPUT_DIR>:/input \
  -v <HOST_OUTPUT_DIR>:/output \
  <IMAGE_NAME> \
  -i /input \
  -o /output
```

---

## Environment Variables

| Variable               | Required | Example                          | Description                                                  |
|-----------------------|----------|----------------------------------|--------------------------------------------------------------|
| OPENAI_BASE_URL       | Yes      | http://localhost:8000/v1        | OpenAI-compatible API endpoint                               |
| OPENAI_API_KEY        | No       | sk-xxxx                         | Required only if server enforces authentication              |
| BDA_DETECTION_MODEL   | No       | Qwen/Qwen3-VL-2B-Instruct       | Override detection model (falls back to config.yaml if unset)|
| BDA_ASSESSMENT_MODEL  | No       | Qwen/Qwen3-VL-2B-Instruct       | Override assessment model (falls back to config.yaml if unset)|

---

## Troubleshooting

### Container Cannot Reach Model Server

```bash
curl http://<MODEL_SERVER_IP>:8000/v1/models
```

Common fixes:

* Use `host.docker.internal` (WSL/Docker Desktop)
* Use `--network host` (Linux)
* Verify correct port


### Architecture Mismatch (x86 vs ARM64)

```bash
requested image's platform (linux/arm64) does not match the detected host platform (linux/amd64)
exec format error
```
Common fixes:

* Add --platform linux/arm64 to your docker run command
* Install emulation support
* Use an image built for your system (x86 vs ARM64)

---

## Summary

* Use **x86 build** for local development
* Use **ARM64 build** for Jetson deployment
* Ensure:

  * Model server is running
  * Input/output volumes are mounted
  * Correct networking is configured
