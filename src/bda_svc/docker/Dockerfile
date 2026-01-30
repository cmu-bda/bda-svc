# --- Stage 1: The "Donor" Image ---
FROM ollama/ollama:latest AS ollama-donor

# --- Stage 2: Your App Image ---
FROM python:3.12-slim

WORKDIR /app

# 1. SETUP UV & DEPENDENCIES
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
COPY pyproject.toml .
RUN uv pip install --system -r pyproject.toml

# 2. INSTALL OLLAMA & UTILS
RUN apt-get update && apt-get install -y procps

# Copy the binary from the official image
COPY --from=ollama-donor /bin/ollama /usr/bin/ollama

# Create the config directory
RUN mkdir -p /root/.ollama

# 3. DOWNLOAD MODELS (Bake into image)
RUN ollama serve & \
    sleep 5 && \
    ollama pull qwen3-vl:8b && \
    pkill ollama

# 4. DOWNLOAD HUGGING FACE MODEL (Bake into image)
RUN python -c "from transformers import AutoModel, AutoProcessor; \
    model_id = 'IDEA-Research/grounding-dino-base'; \
    AutoModel.from_pretrained(model_id); \
    AutoProcessor.from_pretrained(model_id)"

# 5. STARTUP
COPY . .

CMD ollama serve & sleep 5 && python app.py