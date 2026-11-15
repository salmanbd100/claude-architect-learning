# Exam Answer vs Current Reality

The exam is based on **Exam Guide v1.0 (July 2026)**. The products have moved on since then.
**In the exam, pick the exam answer.** In real code, use current behaviour.
Each row is confirmed (or corrected) when we reach the lesson. "Verified" means we tested it ourselves.

| Lesson | Exam answer | Current reality (as of Nov 2026) | Verified? |
|---|---|---|---|
| 1.3 | Subagents are spawned via the **Task** tool; `allowedTools` must include `"Task"` | Renamed to **Agent** in Claude Code v2.1.63 | No |
| 1.2 | Subagents are fully isolated from the coordinator's context | Claude Code "fork" subagents inherit context (exception) | No |
| 2.3 / 4.3 | `tool_choice: {"type": "any"}` or a forced tool guarantees a tool call | Opus 5.5, Sonnet 5.5 and Fable 5.1/5.2 **reject** forced `any`/`tool` with a 400. Use `auto` + `strict: true`, or `output_config.format` | No |
| 4.3 | Use tool use with a JSON schema for reliable structured output | Also available: structured outputs via `output_config.format` / `messages.parse()` | No |
| 4.2 | 2-4 few-shot examples | Current docs suggest 3-5 | No |
| 2.5 | Non-unique Edit match → fall back to Read + Write | In practice: widen `old_string` or use `replace_all` | No |
| 2.5 | Grep and Glob are built-in tools | On macOS/Linux, current Claude Code may omit them from the default tool set | No |
| 3.3 | Path rules load when editing matching files | They load when Claude reads *or* writes a matching file | No |
