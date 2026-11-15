# Glossary

Plain-English definitions. Tags: **[Claude]** Claude/API concept · **[Python]** Python concept ·
**[Exam]** certification term · **[SWE]** general software engineering.

| Term | Tag | Meaning |
|---|---|---|
| Agent | [Claude] | A program where Claude decides which tools to call, in a loop, until the task is done |
| Agentic loop | [Claude] [Exam] | Call Claude → if it asks for a tool, run it and send the result back → repeat until `stop_reason` is `end_turn` |
| `stop_reason` | [Claude] | Field on every API response saying *why* Claude stopped: `end_turn`, `tool_use`, `max_tokens`, `pause_turn`, `refusal`, … |
| Tool use | [Claude] | Claude returns a structured request ("call `list_tasks` with these arguments"). **Your code** runs it |
| Token | [Claude] | The unit Claude reads and writes text in (roughly ¾ of a word). You pay per token |
| Context window | [Claude] | Everything Claude can see in one request: system prompt, tools, message history |
| Stateless API | [Claude] | The API remembers nothing between calls; you resend the whole conversation each time |
| MCP | [Claude] | Model Context Protocol: an open standard for exposing tools and data to AI apps (like USB-C for tools) |
| Subagent | [Claude] [Exam] | A separate Claude instance, started by a coordinator, with its own context and limited tools |
| Hook | [Claude] [Exam] | Code that runs before or after a tool call to allow, deny or modify it. Deterministic, unlike prompts |
| Virtual environment (venv) | [Python] | A per-project folder of installed packages, like `node_modules`, but it also pins the Python interpreter |
| `uv` | [Python] | A fast Python package and project manager (pnpm + nvm in one) |
| `pyproject.toml` | [Python] | Project metadata and dependencies, like `package.json` |
| Type hint | [Python] | Optional annotations like `name: str`. Checked by tools (mypy), not at runtime, much like TypeScript types |
| Separation of concerns | [SWE] | Each module has one job; business rules don't know about Claude or the database |
