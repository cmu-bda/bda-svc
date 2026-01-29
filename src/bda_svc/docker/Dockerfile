# 1. Base Python Image
FROM python:3.12-alpine

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Install system build tools
RUN apk update && apk add gcc libc-dev g++

# 4. Copy specific files
COPY dist/llm_server-1.0.0-py2.py3-none-any.whl .
COPY tinyllama-1.1b-chat-v1.0.Q2_K.gguf .

# 5. Install the Python wheel
RUN pip install llm_server-1.0.0-py2.py3-none-any.whl

# 5. Copy the rest of Flask app
COPY . .

EXPOSE 8000

CMD ["bda-", "--listen=0.0.0.0:8000", "llm_server.main:app"]