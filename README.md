# WorkPilot

A Claude-powered personal work assistant in Python, built lesson by lesson while studying for the
**Claude Certified Architect Foundations (CCAR-F)** exam.

> Status: environment setup complete. Next: Lesson 1.1, Agentic Loops. See [docs/progress.md](docs/progress.md).

## Prerequisites

- macOS or Linux
- [uv](https://docs.astral.sh/uv/) (`brew install uv`). It installs the right Python (3.13) for you
- An Anthropic API key from <https://platform.claude.com/settings/keys>

## Setup

```bash
git clone <repo-url> && cd claude-architect-learning
uv sync                     # creates .venv with Python 3.13 and all dependencies
cp .env.example .env        # then paste your ANTHROPIC_API_KEY into .env
```

## Run

```bash
uv run python scripts/hello_claude.py   # smoke test: one call to Claude
uv run workpilot                        # CLI entry point (grows with each lesson)
```

## Test and lint

```bash
uv run pytest                    # all tests
uv run pytest -m "not live"      # skip tests that call the real API
uv run ruff check . && uv run ruff format .
```

## Configuration

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | yes | none | Claude API key |
| `WORKPILOT_MODEL` | no | `claude-sonnet-5-5` | Model used by WorkPilot (`claude-opus-5-5` is more capable, `claude-haiku-5-5` is cheaper) |

## Documentation

- [Project overview](docs/00-project-overview.md)
- [Architecture](docs/01-architecture.md)
- [Learning roadmap: all 30 lessons](docs/02-learning-roadmap.md)
- [Progress tracker](docs/progress.md)
- [Environment setup explained](docs/setup/00-environment.md)
