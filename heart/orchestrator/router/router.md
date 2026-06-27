# Task Router

## What it does

Given any task description, the router outputs:
- **Which agent** should handle it (Claude or Codex)
- **Task type** classification
- **Confidence score** (0–100%)
- **Reasoning** (which keywords matched, what history says)
- **Optional hybrid suggestion** (Claude plans → Codex executes)

## Quick use

```sh
# Just get a recommendation (no side effects)
route-task --dry-run "your task here"

# Get recommendation + log it
route-task "your task here"

# Get recommendation + log + launch agent (asks confirmation)
route-execute "your task here"

# Automatic launch without confirmation
route-execute --auto "your task here"
```

## How the decision is made

1. **Keywords** — task description is matched against ~14 task type keyword lists
2. **Profile lookup** — each task type has a preferred agent and base confidence
3. **History adjustment** — if past decisions for this (agent, task_type) show a track record, confidence is boosted or penalized
4. **Safety check** — destructive phrases (rm -rf, delete all, etc.) abort routing and require manual review

## Claude is preferred for

reasoning, planning, system design, analysis, documentation, debugging, orchestration, memory updates

## Codex is preferred for

code editing, scripting, file manipulation, workspace repair, autolab experiments, fast iteration

## Learning

After sessions, `route-learn` reads the routing history and autolab results to update:
- `routing_patterns.json` — observed success/failure per (agent, task_type)
- `agent_profiles.json` — observed success rates from autolab experiments

The more you use the system, the better its routing recommendations become.
