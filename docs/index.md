# bda-svc

`bda-svc` is an automated Battle Damage Assessment (BDA) service. It analyzes post-strike imagery using vision-language models, identifies doctrinally relevant targets, assesses visible damage, and produces structured JSON reports.

The system runs locally against any OpenAI-compatible model server (such as vLLM or Ollama) with no external cloud calls at inference time.

## Documentation

- **[User Guide](101-user-guide.md)** — install, run, configure environment variables, edit `config.yaml` and `doctrine.yaml`, interpret reports.
- **[Container](102-container.md)** — build, pull, and run `bda-svc` as a container.

## Project links

- [Source on GitHub](https://github.com/cmu-bda/bda-svc)
- [Contributing guide](https://github.com/cmu-bda/bda-svc/blob/main/CONTRIBUTING.md)
- [License (Apache 2.0)](https://github.com/cmu-bda/bda-svc/blob/main/LICENSE)
