# Planning Heuristics

These guide `goal-plan` when decomposing goals into tasks.

## By Goal Type

| Goal pattern | Typical tasks |
|---|---|
| "Add X to codebase" | plan → design → implement → test → document → verify |
| "Fix bug Y" | plan → diagnose → fix → verify → update memory |
| "Analyze Z" | plan → gather data → analyze → report → store findings |
| "Write docs for W" | plan → outline → draft → refine → save |
| "Repair workspace issue" | plan → diagnose → repair → verify health |
| "Run autolab experiment" | plan → design experiment → execute → evaluate → learn |
| "Improve routing/memory" | plan → analyze current state → design change → apply → verify |

## Complexity Estimation

**High complexity indicators:**
- Goal touches 3+ subsystems
- Goal requires new infrastructure
- Goal involves learning/adaptation
- Goal description has 3+ distinct requirements

**Medium complexity indicators:**
- Goal touches 1–2 subsystems
- Goal builds on existing infrastructure
- Goal has clear start/end state

**Low complexity indicators:**
- Goal is a single-file change
- Goal is read-only (analysis, reporting)
- Goal description is 1 sentence with single verb

## Task Granularity

Prefer tasks that:
- Produce a file/log/state change as output (verifiable)
- Can complete in 5–15 minutes of agent work
- Have a single clear question: "did this task succeed?"

Avoid tasks that:
- Span multiple agent sessions
- Have ambiguous success criteria
- Are purely internal (no output)

## Agent Assignment Per Task

- `planning`, `reasoning`, `system_design`, `analysis` → claude
- `code_edit`, `scripting`, `file_manipulation`, `workspace_repair` → codex
- `debugging` → claude (diagnosis) then codex (fix)
- `documentation`, `memory_update`, `logging` → claude
- `autolab_experiment` → codex
- `orchestration` → claude
