# Contributing to `bda-svc`

Thanks for taking the time to contribute. This repo is an automated Battle Damage Assessment (BDA) service built around a CLI-driven pipeline and supporting modules.

## Table of Contents
- [Ways to Contribute](#ways-to-contribute)
- [Project Structure](#project-structure)
- [Development Setup](#development-setup)
- [Branching and Pull Requests (GitHub Flow)](#branching-and-pull-requests-github-flow)
- [Commit and PR Standards](#commit-and-pr-standards)
- [Code Style and Quality Gates](#code-style-and-quality-gates)
- [Testing](#testing)
- [Configuration and Prompts](#configuration-and-prompts)
- [Project Tracking](#project-tracking)
- [Security and Sensitive Data](#security-and-sensitive-data)
- [License](#license)

---

## Ways to Contribute
- Fix bugs, improve reliability, or harden error handling
- Add/expand tests
- Improve docs, CLI help text, and examples
- Improve model/prompt configuration ergonomics
- Add small, well-scoped features tied to an issue/task

If you’re not sure where to start, pick an open issue or ask in the relevant project channel.

---

## Project Structure
High-level layout (see `README.md` for the authoritative version)

- `.github/` — CI/CD configuration
- `src/bda_svc/` — core package
  - `app.py` — main analysis workflow
  - `cli.py` — command-line interface
  - `config.yaml` — model/prompt selection
  - `export.py` — exporting BDA outputs
  - `inputs.py` — input retrieval/validation
  - `model.py` — model integrations
  - `utilities.py`, `constants.py`, etc.
- `tests/` — automated tests 

---

## Development Setup
This repository uses `uv` for Python environment/dependency management, and uses `pre-commit` hooks for local quality checks. 

Typical setup:
1. Install `uv`
2. Create/sync the dev environment
3. Activate the virtual environment
4. Install pre-commit hooks

Reference (from repo README):

---

## Branching and Pull Requests (GitHub Flow)
We use **GitHub Flow**:

1. `main` is always in a releasable state.
2. Create a short-lived feature branch from `main`.
3. Make small commits as you work.
4. Open a Pull Request (PR) early (draft is fine).
5. Address review comments and keep PR scope tight.
6. Merge when checks pass and review is approved.
7. Delete the branch after merge.

### Branch naming
Use one of:
- `feature/<short-topic>`
- `fix/<short-topic>`
- `docs/<short-topic>`
- `chore/<short-topic>`

Examples:
- `feature/cli-batch-input`
- `fix/invalid-image-handling`
- `docs/usage-examples`

---

## Commit and PR Standards
### Commits
- Prefer small, logical commits.
- Use descriptive commit messages.
- Avoid mixing unrelated changes (e.g., formatting + feature + refactor in one commit).

### PRs
A PR should include:
- **What changed** (1–3 bullets)
- **Why** (problem/requirement/issue)
- **How to test** (exact commands + expected result)
- Screenshots/log snippets if relevant
- Any known limitations or follow-on work

Suggested PR title style:
- `feat: ...`
- `fix: ...`
- `docs: ...`
- `chore: ...`

---

## Code Style and Quality Gates
- Run formatting/lint checks locally before requesting review.
- Install and use pre-commit hooks (this repo includes `.pre-commit-config.yaml`). 

**Minimum expectation before merge:**
- Lint/format passes
- Tests pass
- No new warnings introduced (or justify them explicitly)

---

## Testing
General expectations:
- Every code change must be accompanied by testing appropriate to the change.
- **Developers must write tests for the functions and modules they create or modify.**
- Tests should be deterministic and runnable offline (no external network calls as part of the default test suite).
- Prefer unit tests for pure logic and small behaviors; use integration tests when validating end-to-end workflow behavior.

What to test (guidance):
- **Input validation:** supported formats (JPG/PNG/GIF/TIFF), missing/empty directories, corrupt/invalid files.
- **Preprocessing/object extraction:** handling of extraction failures and logging behavior without terminating the batch.
- **VLM analysis integration:** correct routing of prompts/templates based on detected object category; correct handling of low-confidence outputs (flagging/manual review signals).
- **Output generation:** JSON schema/content (date, model name, damage levels, confidence scores, observations, supporting imagery references), unique output behavior (no overwrite).
- **Retrieval mode:** CLI path that retrieves one or multiple completed assessments.

Test organization (suggested):
- `tests/unit/` — fast tests for individual functions/classes
- `tests/integration/` — tests for multi-step pipeline flows using small fixtures
- `tests/data/` — small, versioned sample inputs/fixtures

PR checklist (testing-related):
- [ ] Added/updated tests for all new or changed functions
- [ ] Verified key CLI paths relevant to the change
- [ ] Verified error-handling paths if the change affects inputs or pipeline stability

Baseline expectations:
- Add or update tests for bug fixes and new functionality.
- Prefer fast unit tests for logic; use integration tests for workflow-level behavior.
- Keep tests deterministic (avoid network calls; avoid depending on local machine state).

Suggested structure (adjust as your repo evolves):
- `tests/unit/` for pure logic
- `tests/integration/` for multi-module workflow checks
- `tests/data/` for small, versioned fixtures

Recommended PR checklist:
- [ ] Added/updated tests for changes
- [ ] Verified CLI behavior for common paths
- [ ] Verified error handling for invalid/corrupt inputs (where applicable)
- [ ] Verified outputs conform to expected JSON structure (where applicable)

---

## Configuration and Prompts
The repo uses a text-based configuration file (`config.yaml`) to select models and prompts. 

Guidelines:
- Keep prompt templates versioned and reviewed like code.
- Avoid breaking prompt/config schemas without a clear migration plan.
- If adding config keys, document them in `README.md`.

---

## Project Tracking
Primary work tracking:
- GitHub Issues: https://github.com/cmu-bda/bda-svc/issues 

Project board:
- GitHub Projects: https://github.com/orgs/cmu-bda/projects/1/views/2

---

## Security and Sensitive Data
- Do not commit secrets, tokens, or credentials.
- Do not commit sensitive imagery or data unless explicitly authorized and properly handled.
- Prefer sample/synthetic data for tests and docs.
- If you discover a security issue, report it privately to maintainers (do not open a public issue).

---

## License
By contributing, you agree that your contributions will be licensed under the repository’s license.
