# Task Decomposition Policy

## Principles

1. **Single responsibility** — each task does one thing and produces a verifiable output
2. **Smallest safe unit** — prefer tasks that complete in one agent session
3. **Explicit dependencies** — never assume an implicit ordering; state it in the dep map
4. **Conservative complexity** — when in doubt, estimate high and split further
5. **Agent fit** — decompose with the executing agent in mind (Claude for reasoning, Codex for code changes)

## Decomposition Heuristics

- If complexity = high → split into 3–6 subtasks
- If complexity = medium → split into 2–3 subtasks
- If complexity = low → may be a single task
- Planning tasks always precede execution tasks
- Verification tasks always follow execution tasks
- Memory/state update tasks come last

## Mandatory First Task

Every goal gets a mandatory first task: `T_XXX_00 — understand_and_plan` (task_type: planning, preferred_agent: claude)

This ensures the executing agent reads context before doing work.

## Task Types Available

Match task_type to the orchestrator's 14 types:
- reasoning, planning, code_edit, scripting, debugging, documentation
- analysis, workspace_repair, autolab_experiment, orchestration
- memory_update, file_manipulation, system_design, logging

## Dependency Rules

- T_00 (plan) → no dependencies
- Execution tasks → depend on T_00
- Tasks that modify the same file → must be sequential (A → B, not parallel)
- Verification tasks → depend on all execution tasks they verify
- Final memory_update → depends on all other tasks

## Safety Rules in Decomposition

- Never create a task with description containing: rm -rf, delete all, drop table, force push
- If a step would be destructive, add a `requires_confirmation: true` flag
- Always include a rollback/verify step after any workspace_repair task
