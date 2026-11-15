# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A learning project for the **Claude Certified Architect Foundations (CCAR-F)** exam. **WorkPilot** is a
Python CLI work assistant built one lesson at a time; every feature maps to one of the 30 lessons at
<https://claudecertificationguide.com/learn>. The owner is an experienced TypeScript/React engineer who
is new to Python and to the Claude SDKs.

Before any work, read `docs/progress.md` (current lesson and status) and `docs/02-learning-roadmap.md`
(what each lesson builds). Only build what the current lesson calls for. Do not implement later lessons
ahead of time.

## Commands

Package manager is **uv**. Python is pinned to 3.13 via `.python-version`. Do not use pip, poetry or a
global interpreter.

```bash
uv sync                          # create/refresh .venv from uv.lock
uv add <pkg> / uv add --dev <pkg>
uv run workpilot                 # CLI entry point (workpilot:main in pyproject.toml)
uv run pytest                    # all tests
uv run pytest tests/unit/test_loop.py::test_name   # one test
uv run pytest -m "not live"      # skip tests that call the real Claude API
uv run ruff check . && uv run ruff format .
```

pytest and ruff are added during Stage 0 setup. If they are missing from `pyproject.toml`, that step has
not happened yet.

## Architecture (target; check `docs/01-architecture.md` → "Implemented so far")

Code lives in `src/workpilot/` (src layout, installed into `.venv` as a package).

Layering, from outside in: `cli.py` / `mcp_server/` → `agent/` and `orchestration/` (the only places that
talk to Claude) → `policy/` (deterministic pre/post tool gates) → `tools/` (thin adapters: JSON in,
structured result or `ToolError` out) → `services/` (business rules) → `storage/` (SQLite and files).

- **`services/` must never import `anthropic`, `claude_agent_sdk` or `mcp`.** The local tool registry and
  the MCP server both call the same services.
- Two Claude surfaces, kept deliberately separate: the **Anthropic SDK** with a hand-written
  `stop_reason`-driven loop (`agent/loop.py`), and the **Claude Agent SDK** for subagents, hooks and
  sessions (`orchestration/`).
- The Claude client is injected via a `Protocol`, so unit tests use a fake client
  (`tests/fakes.py`). Tests that hit the real API are marked `live`.
- Model comes from `WORKPILOT_MODEL` (default `claude-sonnet-5-5`). Check SDK calls against current docs, not
  memory. Several APIs changed after the exam guide was written.

## Documentation is part of every change

- Each lesson has one doc in `docs/domain-0X-*/` named by lesson id (`1-1-agentic-loops.md`), using the
  10-section template: what / why / how / Mermaid flowchart / project connection / implementation
  walkthrough / Python concepts (with TS comparisons) / execution walkthrough / how to test / what to
  remember. Each doc also has an "Exam answer vs current reality" callout.
- When behaviour differs from Exam Guide v1.0, record it in `docs/exam-vs-reality.md` and mark the row
  verified only after testing it.
- Keep `docs/progress.md`, the domain `overview.md`, `docs/01-architecture.md` and `README.md` in sync with
  the code. A lesson is marked **Completed** only after the owner has run it, tests pass, and they have
  answered the check questions. Never mark it on code generation alone.

## Working style for this repo

This is a mentoring project. Explain new Python syntax before using it, and work in small steps that the
owner runs themselves. When something fails, explain the error before fixing it.
