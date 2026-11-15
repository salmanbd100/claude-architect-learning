# Project Overview: WorkPilot

## What is this repository?

A learning project with two goals:

1. Prepare for the **Claude Certified Architect Foundations (CCAR-F)** exam.
2. Build a real, working Claude-powered application in Python.

The source of truth for the curriculum is <https://claudecertificationguide.com/learn>
(Exam Guide v1.0, July 2026): 5 domains, 30 lessons.

## The application

**WorkPilot** is a command-line work assistant for an individual engineer. By the end it can:

- Chat with you, and use tools to act on your behalf.
- Manage tasks (stored in SQLite).
- Search notes and documents in a local `knowledge/` folder.
- Turn meeting notes into structured action items.
- Produce research briefs that cite their sources.
- Submit expense claims, with claims over £500 gated and escalated to a manager.
- Generate a weekly report, reviewed by an independent Claude instance.
- Expose its tools over **MCP**, so Claude Code or Claude Desktop can use them.

## Why this app?

Each exam scenario has a natural home in WorkPilot:

| Exam pattern | WorkPilot equivalent |
|---|---|
| Refund threshold / compliance gate | Expense claims over £500 are blocked by a deterministic hook |
| Customer-support handoff | Structured escalation summary in an approvals queue |
| Ambiguous customer match | "Assign to Sam" when two Sams exist, so it asks rather than guessing |
| Multi-agent research system | `research` command: coordinator plus subagents over `knowledge/` |
| Invoice extraction | Meeting-notes and receipt extraction with validation and retry |
| Overnight batch job | Nightly digest via the Message Batches API |
| CI code review | GitHub Action running `claude -p` on this repo's PRs |

## How to read the docs

| File | Purpose |
|---|---|
| [01-architecture.md](01-architecture.md) | How the system is structured, and why |
| [02-learning-roadmap.md](02-learning-roadmap.md) | All 30 lessons mapped to implementation |
| [progress.md](progress.md) | What is done, in progress, or not started |
| [exam-vs-reality.md](exam-vs-reality.md) | Where the exam answer differs from current product behaviour |
| [glossary.md](glossary.md) | Terms, in plain English |
| `domain-0X-*/` | One short doc per lesson |
| `setup/` | Environment setup |
| `concepts/` | Extra explainers for difficult topics |
