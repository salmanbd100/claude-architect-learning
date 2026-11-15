# Learning Roadmap: 30 Lessons → WorkPilot

Lesson titles match <https://claudecertificationguide.com/learn> exactly.
Entries are listed in **study order** (dependency-driven); the docs folders keep the official numbering.
Each entry is a plan, and is refined when we reach the lesson. Fields:
Objective · Theory · Problem · Project connection · Implementation · Python · Claude · Files · Outcome · Testing · Exam.

---

## Stage 0: Environment setup

- **Objective:** a reproducible Python project that can call Claude.
- **Implementation:** install `uv`, `uv init --package`, pin Python 3.13, add `anthropic` + `pydantic-settings` + `pytest` + `ruff`, `.env.example`, `.gitignore`, `config.py`, `scripts/hello_claude.py`.
- **Python:** packages/modules, `src/` layout, virtual environments, `pyproject.toml`, type hints, f-strings.
- **Claude:** Messages API request/response shape, models, tokens, `usage`, the stateless API.
- **Files:** `pyproject.toml`, `uv.lock`, `.python-version`, `.env.example`, `.gitignore`, `src/workpilot/config.py`, `scripts/hello_claude.py`, `tests/unit/test_config.py`, `README.md`, `docs/setup/00-environment.md`.
- **Testing:** `uv run python scripts/hello_claude.py` prints a reply + `stop_reason` + token usage; `uv run pytest`.

---

## Stage A: Core loop, tools, prompting

### 1. Lesson 1.1: Agentic Loops (D1)
- **Objective:** control an agent loop correctly using `stop_reason`.
- **Theory:** Claude can't run code. It *asks* for a tool (`stop_reason: "tool_use"`). Your code runs the tool, appends the result to the history, and calls again. You stop when `stop_reason` is `"end_turn"`.
- **Problem:** without a loop, Claude can only talk. With a badly controlled loop, it stops early or never stops.
- **Project connection:** the heart of the WorkPilot chat REPL.
- **Implementation:** `run_agent_loop()` with a `match` on `stop_reason` (`tool_use`, `end_turn`, `max_tokens`, `pause_turn`, `refusal`). Two toy tools (`get_current_time`, `list_tasks` over an in-memory list). A safety cap as a backstop only. A minimal REPL.
- **Python:** `while`, `match`/`case`, dicts/lists, functions, `@dataclass`, `typing.Protocol` (an interface, so a fake client can be injected).
- **Claude:** `tools` param, `tool_use` / `tool_result` blocks, `tool_use_id`, appending the full `response.content`.
- **Files:** `src/workpilot/agent/loop.py`, `llm/client.py`, `cli.py`, `tests/fakes.py`, `tests/unit/test_loop.py`.
- **Outcome:** "What time is it and what tasks do I have?" triggers two tool calls and then a final answer.
- **Testing:** a fake client scripted `tool_use → end_turn`. Assert the tool ran, the result was appended, and the loop ended. One live run.
- **Exam:** the three anti-patterns (parsing text for "done", iteration cap as the primary stop, checking `content[0].type`).

### 2. Lesson 2.1: Tool Interface Design (D2)
- **Objective:** write tool definitions that Claude selects correctly.
- **Theory:** Claude chooses tools almost entirely from their **name + description + schema**. Vague or overlapping descriptions cause wrong picks.
- **Problem:** "search" tools that overlap mean Claude searches notes when you meant tasks.
- **Project connection:** real task tools backed by SQLite, plus a notes search.
- **Implementation:** a tool registry where a decorator registers a function with a Pydantic input model and generates the JSON schema. A `TaskService` over SQLite. Create a deliberately overlapping pair, observe the misrouting, then fix it by rewriting descriptions (purpose, inputs, example, edge cases, boundaries).
- **Python:** decorators (higher-order functions), classes, Pydantic `BaseModel`, `with` context managers, `sqlite3`.
- **Claude:** tool `input_schema`, the anatomy of a description, how system-prompt keywords can override descriptions.
- **Files:** `tools/registry.py`, `tools/tasks.py`, `tools/notes.py`, `services/task_service.py`, `storage/db.py`, `domain/models.py`, tests.
- **Outcome:** 5/5 routing prompts pick the right tool after the fix.
- **Testing:** unit test for schema generation; a live routing check script.
- **Exam:** fix descriptions *before* adding few-shot examples or a routing classifier.

### 3. Lesson 2.2: Structured Error Responses (D2)
- **Objective:** return errors Claude can reason about.
- **Theory:** a tool can fail in different ways: transient (retry), validation (fix the input), business (rule says no), permission (not allowed). An empty result is **not** an error.
- **Problem:** returning `"error"` as a string leads Claude to retry pointlessly or report false "no results".
- **Project connection:** every WorkPilot tool returns structured errors.
- **Implementation:** a `ToolError` exception with `error_category`, `is_retryable`, `description`. The registry converts it into a `tool_result` with `is_error: true`. Empty searches return `resultCount: 0`.
- **Python:** exceptions, custom exception classes, `Enum` / `Literal`.
- **Claude:** `is_error` on `tool_result`; MCP's protocol errors vs `isError` tool errors.
- **Files:** `tools/errors.py`, `tools/registry.py`, tests.
- **Outcome:** a simulated DB outage gives Claude a retryable error, and an invalid date produces a corrected retry.
- **Testing:** unit tests per category; a loop test with a fake client.
- **Exam:** the 4 categories; "access failure ≠ valid empty result".

### 4. Lesson 2.3: Tool Distribution & Tool Choice (D2)
- **Objective:** give each agent the right, small set of tools, and control whether it must use one.
- **Theory:** too many tools degrades selection. Consolidate near-duplicates into parameterised tools; scope tools per role. `tool_choice` can be `auto`, `any`, or force a specific tool.
- **Problem:** an agent with 18 tools picks badly and wastes tokens.
- **Project connection:** chat agent vs extractor get different tool sets.
- **Implementation:** merge create/update/complete into `manage_task(action=…)`. Add `strict: true` + `additionalProperties: false`. Role-scoped tool lists. A live experiment with `tool_choice` on the configured model, recorded in `exam-vs-reality.md`.
- **Python:** `Literal` unions, `**kwargs`.
- **Claude:** `tool_choice`, `strict` tool use, per-model restrictions.
- **Files:** `tools/tasks.py`, `tools/registry.py`, `agent/roles.py`, tests.
- **Outcome:** fewer, clearer tools; a documented `tool_choice` behaviour.
- **Testing:** assert role tool lists; experiment script output.
- **Exam:** 4-5 tools per agent; `any` when a tool is required but unknown; forced for a specific tool.

### 5. Lesson 4.1: System Prompts with Explicit Criteria (D4)
- **Objective:** replace vague instructions with explicit, categorical criteria.
- **Theory:** "Be conservative" means different things each run. "Priority = high if due ≤ 2 days OR blocking someone" is consistent.
- **Problem:** inconsistent judgements; one noisy category destroys trust in all of them.
- **Project connection:** task prioritisation in WorkPilot.
- **Implementation:** a vague prompt vs a criteria prompt over 10 sample tasks, then count disagreements with the expected labels.
- **Python:** multiline strings, `textwrap.dedent`, constants modules.
- **Claude:** the `system` parameter; criteria with concrete examples.
- **Files:** `prompts/system.py`, `scripts/eval_priority.py`, `tests/data/tasks_labelled.json`.
- **Outcome:** a measurable drop in misclassifications.
- **Testing:** the eval script prints the error count before and after.
- **Exam:** temporarily disable the worst false-positive category; define severity with examples.

### 6. Lesson 4.2: Few-Shot Prompting (D4)
- **Objective:** use examples to fix inconsistent formatting, judgement and extraction.
- **Theory:** 2-4 examples, each with its reasoning, show Claude *how* to decide.
- **Problem:** meeting-note extraction varies wildly between notes with different structures.
- **Project connection:** meeting notes → action items.
- **Implementation:** a few-shot prompt built from `knowledge/meetings/` examples; compare consistency.
- **Python:** list comprehensions, `pathlib.Path`.
- **Claude:** few-shot in system vs user turns; example diversity.
- **Files:** `prompts/few_shot.py`, `knowledge/meetings/*.md`, `scripts/eval_extraction.py`.
- **Outcome:** consistent output format across varied notes.
- **Testing:** the eval script compares with and without examples.
- **Exam:** few-shot is the first fix for inconsistency (2-4 examples, with reasoning).

### 7. Lesson 4.3: Structured Output with Tool Use (D4)
- **Objective:** get reliably parseable, schema-valid output.
- **Theory:** a JSON schema (via a tool or structured outputs) guarantees shape, not truth. Nullable fields and `unclear` / `other` values stop Claude inventing data.
- **Problem:** free-text JSON breaks parsers, and required fields force fabrication.
- **Project connection:** action-item extraction returns typed `ActionItem` objects.
- **Implementation:** a Pydantic schema with nullable `due_date`, an `owner` that allows `"unclear"`, and `category` with `other` + `detail`. Compare the tool-schema approach with `output_config.format` / `messages.parse()`.
- **Python:** `Optional`, `Field`, `model_json_schema()`, `model_validate()`.
- **Claude:** tool-based extraction, `tool_choice`, structured outputs, `strict`.
- **Files:** `extraction/action_items.py`, `domain/models.py`, tests.
- **Outcome:** a note with no owner gives `owner: "unclear"`, not a made-up name.
- **Testing:** unit validation of fixtures; a live run on a tricky note.
- **Exam:** schema ≠ semantic correctness (for example, totals that don't add up).

### 8. Lesson 4.4: Validation, Retry, and Feedback Loops (D4)
- **Objective:** catch semantic errors and retry with specific feedback.
- **Theory:** validate in code. On failure, resend the *original document + the failed output + the exact error*. Retries can fix mistakes; they cannot invent missing information.
- **Problem:** receipt totals that don't add up; owners who don't exist.
- **Project connection:** receipt extraction for expenses; owner validation.
- **Implementation:** Pydantic validators; `extract_with_retry(max_attempts=…)`; `calculated_total` vs `stated_total` + `conflict_detected`.
- **Python:** `@field_validator`, `@model_validator`, `try/except ValidationError`.
- **Claude:** feedback-driven retries; self-check fields.
- **Files:** `extraction/receipts.py`, `extraction/retry.py`, tests.
- **Outcome:** bad output is corrected on retry; a missing field ends as `null`, not a loop.
- **Testing:** a fake client returns bad then good output; assert the error text appears in the retry prompt.
- **Exam:** which errors retries can and cannot fix.

---

## Stage B: Claude Code configuration (applied to this repo)

### 9. Lesson 3.1: CLAUDE.md Hierarchy, Scoping, and Modular Organisation (D3)
- **Objective:** know which CLAUDE.md applies where, and how they combine.
- **Theory:** user (`~/.claude/CLAUDE.md`), project (`./CLAUDE.md` or `.claude/CLAUDE.md`) and subdirectory files are **concatenated**. `@path` imports split them up. CLAUDE.md is guidance, not enforcement.
- **Problem:** a new teammate's Claude ignores conventions that only live in *your* user file.
- **Project connection:** WorkPilot's own CLAUDE.md files.
- **Implementation:** project `CLAUDE.md` (Python conventions, the layering rule) with `@docs/01-architecture.md`; `src/workpilot/mcp_server/CLAUDE.md`; git-ignored `CLAUDE.local.md`.
- **Claude:** `/memory`, `/context`, `.claude/rules/`, `settings.json` vs CLAUDE.md.
- **Files:** `CLAUDE.md`, `src/workpilot/mcp_server/CLAUDE.md`, `.gitignore`.
- **Outcome / Testing:** `/memory` lists all levels; a "new teammate" walkthrough.
- **Exam:** concatenation, not override; hard rules belong in settings or hooks.

### 10. Lesson 3.2: Custom Slash Commands and Skills (D3)
- **Objective:** package repeatable workflows as skills.
- **Theory:** `.claude/skills/<name>/SKILL.md` loads on demand; `.claude/commands/` is the alias. Project scope is shared via git; user scope is personal.
- **Implementation:** a `/new-tool` skill (scaffolds tool + service + test) and a `/lesson-doc` skill (writes a lesson doc from the template). Frontmatter: `argument-hint`, `allowed-tools`, `context: fork`.
- **Files:** `.claude/skills/new-tool/SKILL.md`, `.claude/skills/lesson-doc/SKILL.md`.
- **Outcome / Testing:** `/new-tool expenses` produces files that pass `ruff`.
- **Exam:** skills (on demand) vs CLAUDE.md (always loaded); project vs user scope.

### 11. Lesson 3.3: Path-Specific Rules for Conditional Convention Loading (D3)
- **Objective:** load conventions only when relevant files are touched.
- **Theory:** `.claude/rules/*.md` with `paths:` globs; `**` matches nested folders.
- **Implementation:** `.claude/rules/tests.md` (`tests/**/*.py`), `.claude/rules/prompts.md` (`src/workpilot/prompts/**`).
- **Outcome / Testing:** editing a test shows the rule in `/context`; editing other files doesn't.
- **Exam:** rules vs root CLAUDE.md vs per-directory CLAUDE.md (token efficiency).

### 12. Lesson 3.4: Plan Mode vs Direct Execution (D3)
- **Objective:** choose a mode by ambiguity, not difficulty.
- **Implementation:** plan mode to design the MCP server (ambiguous); direct execution for a clear one-file fix. Use the Explore subagent for discovery.
- **Files:** `docs/domain-03-claude-code-workflows/3-4-plan-mode-vs-direct-execution.md` (decision log).
- **Exam:** plan-then-execute hybrid; Explore keeps discovery out of the main context.

### 13. Lesson 3.5: Iterative Refinement Techniques (D3)
- **Objective:** steer Claude Code with examples, tests and interviews.
- **Implementation:** build `services/digest.py` test-first (red → green) with Claude Code; use the interview pattern to define the expense policy; compare batch vs sequential feedback.
- **Files:** `services/digest.py`, `tests/unit/test_digest.py`.
- **Exam:** 2-3 I/O examples; test-driven iteration; batch interacting fixes.

### 14. Lesson 2.5: Built-in Tools (D2)
- **Objective:** know what each Claude Code built-in tool is for.
- **Implementation:** exercise only. Find callers of `TaskService` and their tests (Grep, then Glob), trace through `tools/__init__.py`, handle a non-unique Edit. No new application code needed; the doc explains why.
- **Exam:** Grep = contents, Glob = paths; Edit, with Read + Write as the fallback; incremental discovery.

### 15. Lesson 3.6: CI/CD Integration (D3)
- **Objective:** run Claude non-interactively in CI with structured output.
- **Implementation:** `.github/workflows/claude-review.yml` using `claude -p --output-format json --json-schema … --max-turns … --allowedTools …`; `scripts/ci_review_gate.py` fails on high-severity findings; incremental review passes previous findings.
- **Files:** workflow, gate script, review JSON schema.
- **Testing:** run `claude -p` locally; optionally on a real PR.
- **Exam:** `-p` prevents hangs; independent review instance; `structured_output`.

---

## Stage C: MCP

### 16. Lesson 2.4: MCP Server Integration (D2)
- **Objective:** expose and consume tools over MCP.
- **Theory:** MCP servers offer **tools** (actions) and **resources** (readable content). Clients like Claude Code connect via `.mcp.json` (project, shared) or `~/.claude.json` (user, personal).
- **Problem:** you want the same task tools in Claude Code, Claude Desktop and WorkPilot without rewriting them.
- **Implementation:** FastMCP server reusing `services/`; `notes://` resources; `.mcp.json` with `${WORKPILOT_DB}`; consume a community server after a build-vs-use comparison.
- **Python:** `async def` / `await` (like JS Promises), stdio subprocesses.
- **Files:** `mcp_server/server.py`, `.mcp.json`, tests.
- **Testing:** MCP Inspector / `claude mcp list`; Claude Code calls `list_tasks` via MCP.
- **Exam:** project vs user config; env-var expansion; resources; detailed descriptions so MCP tools compete with built-ins.

---

## Stage D: Orchestration (Claude Agent SDK)

### 17. Lesson 1.6: Task Decomposition Strategies (D1)
- **Objective:** choose between a fixed pipeline and dynamic decomposition.
- **Implementation:** weekly report as a fixed pipeline (per-note local pass → cross-note integration pass); contrast with an open-ended "why did project X slip?" investigation.
- **Files:** `orchestration/weekly_report.py`, tests.
- **Testing:** single pass vs local+integration on 14 notes; compare what each misses.
- **Exam:** attention dilution; a bigger context window doesn't fix it.

### 18. Lesson 1.2: Multi-Agent Orchestration (D1)
- **Objective:** design a hub-and-spoke coordinator.
- **Implementation:** a `research` command; the coordinator partitions the question, dispatches subagents, checks coverage, and iterates.
- **Files:** `orchestration/coordinator.py`.
- **Testing:** a two-part question; the log shows both parts covered.
- **Exam:** all communication goes through the hub; narrow decomposition causes coverage gaps.

### 19. Lesson 1.3: Subagent Invocation and Context Passing (D1)
- **Objective:** spawn subagents correctly and give them complete context.
- **Implementation:** Agent SDK `AgentDefinition`s (`searcher`, `analyst`) with restricted tools; `allowedTools` includes the Agent tool; parallel spawning; structured findings with source metadata.
- **Files:** `orchestration/agents.py`.
- **Testing:** assert subagent prompts contain full findings and metadata.
- **Exam:** Task/Agent tool; goals not procedures; parallel calls in one response.

### 20. Lesson 1.4: Workflow Enforcement and Handoff (D1)
- **Objective:** enforce must-happen steps in code, and hand off cleanly to humans.
- **Implementation:** `verify_receipt` must succeed before `submit_expense` (code gate); over-threshold claims → structured handoff record in an approvals table; decomposition of multi-concern requests.
- **Files:** `services/expense_service.py`, `policy/gates.py`, `tools/expenses.py`.
- **Testing:** submit without verify → denied, whatever the prompt says.
- **Exam:** prompts are probabilistic, gates are deterministic; handoff fields.

### 21. Lesson 1.5: Agent SDK Hooks (D1)
- **Objective:** use PreToolUse / PostToolUse hooks for hard rules.
- **Implementation:** PreToolUse denies (or `ask`s on) expenses over £500 and redacts card numbers via `updatedInput`; PostToolUse trims output. Mirror this in `policy/hooks.py` for our own loop.
- **Files:** `orchestration/hooks.py`, `policy/hooks.py`.
- **Testing:** hook functions unit-tested; a jailbreak-style prompt is still blocked.
- **Exam:** hooks for 100% requirements, prompts for preferences.

### 22. Lesson 1.7: Session State and Resumption (D1)
- **Objective:** resume, fork, or restart sessions appropriately.
- **Implementation:** named research sessions; resume; fork for an alternative angle; detect changed `knowledge/` files (hashes) → fresh start + summary.
- **Files:** `orchestration/sessions.py`.
- **Testing:** change a file, resume → stale-context path taken.
- **Exam:** `--resume`, `fork_session`, fresh start + summary for stale context.

---

## Stage E: Reliability, context and scale

### 23. Lesson 5.1: Context Window Management (D5)
- **Implementation:** a persistent case-facts block outside the summarised history; tool-result trimming; key findings first; `cache_control` on static prompt + tools.
- **Files:** `context/case_facts.py`, `context/trimming.py`, `agent/loop.py`.
- **Testing:** the amount survives summarisation; `cache_read_input_tokens > 0` on the second call.
- **Exam:** summaries lose numbers, dates and IDs; lost-in-the-middle.

### 24. Lesson 5.2: Escalation & Ambiguity Resolution (D5)
- **Implementation:** escalation criteria + few-shot in the system prompt; clarifying question on an ambiguous person match.
- **Files:** `prompts/escalation.py`, `services/people_service.py`, `scripts/eval_escalation.py`.
- **Testing:** an 8-conversation eval set.
- **Exam:** valid triggers (explicit request, policy gap, no progress) vs unreliable ones (sentiment, self-confidence).

### 25. Lesson 5.3: Error Propagation in Multi-Agent Systems (D5)
- **Implementation:** structured subagent failure context; the coordinator continues and annotates coverage gaps.
- **Files:** `orchestration/coordinator.py`, `orchestration/errors.py`.
- **Testing:** an injected failing subagent → the brief completes and lists the gap.
- **Exam:** don't silently suppress errors, and don't abort the whole workflow.

### 26. Lesson 5.4: Codebase Exploration & Context Degradation (D5)
- **Implementation:** scratchpad + `state-manifest.json` for long research jobs; phase summaries; a Claude Code `/compact` + Explore exercise.
- **Files:** `orchestration/manifest.py`.
- **Testing:** kill mid-run, resume from the manifest.
- **Exam:** degradation = attention drift, not running out of tokens.

### 27. Lesson 5.5: Human Review & Confidence Calibration (D5)
- **Implementation:** field-level confidence; ~30 labelled notes; per-type/per-field accuracy report; a stratified review queue.
- **Files:** `review/calibration.py`, `review/sampling.py`, `tests/data/labelled/`.
- **Testing:** the report shows segment accuracy; the sample includes high-confidence items.
- **Exam:** the aggregate-metrics trap; calibrate on labelled sets.

### 28. Lesson 5.6: Information Provenance & Multi-Source Synthesis (D5)
- **Implementation:** claim→source mapping (doc, excerpt, date) in research briefs; conflicts shown side by side; format matched to content.
- **Files:** `domain/models.py`, `orchestration/synthesis.py`.
- **Testing:** two conflicting docs → both values shown, attributed.
- **Exam:** attribution is lost unless preserved at every stage.

### 29. Lesson 4.5: Batch Processing Strategies (D4)
- **Implementation:** nightly digest via the Message Batches API; `custom_id`; poll; handle `errored`/`expired`; resubmit only failures.
- **Files:** `batch/nightly_digest.py`, tests.
- **Testing:** a fake batch client; one small live batch.
- **Exam:** 50% cost, ≤24h, no SLA; blocking work stays synchronous; SLA arithmetic.

### 30. Lesson 4.6: Multi-Instance and Multi-Pass Review (D4)
- **Implementation:** an independent reviewer instance for the weekly report; per-section + integration passes; confidence routing calibrated on the 5.5 set.
- **Files:** `review/reviewer.py`.
- **Testing:** planted errors; compare self-review vs independent catch rates.
- **Exam:** self-review shares the generator's blind spots; self-reported confidence is uncalibrated.

---

## Stage F: Consolidation
README polish, diagram refresh, glossary completion, the 5 mock exams, and revising lessons marked *Needs revision*.

**Estimated duration:** ~44-54 study days at 2-3 h/day (≈ 9-11 weeks at 5 days/week).
