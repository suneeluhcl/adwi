# Workspace Orchestrator

A local, file-based orchestration layer that routes tasks to the right agent (Claude or Codex) based on task type, learned history, and agent strengths.

## The problem it solves

Before: You had to manually decide whether to open Claude Code or Codex for each task.

After: Describe your task and the system tells you (or even launches) the best agent for it.

## How it works

```
You describe a task
       ↓
route-task classifies it (14 task types, keyword matching)
       ↓
Checks agent_profiles.json (Claude vs Codex strengths)
       ↓
Adjusts with routing_patterns.json (learned from past outcomes)
       ↓
Outputs: agent + task_type + confidence + reasoning
       ↓
route-execute (optional) launches use-claude or use-codex
       ↓
Outcome logged to history.json
       ↓
route-learn updates patterns (runs automatically on maintenance)
```

## Quick start

```sh
# Just classify a task (no side effects, no agent launched)
route-task "debug the NLU intent routing failure"

# Show routing decision + ask before launching
route-execute "write a bash script to monitor disk usage"

# Launch without confirmation
route-execute --auto "analyze workspace health trends"

# Preview only (dry run)
route-execute --dry-run "refactor the autolab evaluator"
```

## Key files

| File | Purpose |
|------|---------|
| `router/agent_profiles.json` | Claude/Codex strengths and observed stats |
| `router/task_types.json` | 14 task types with preferred agents |
| `router/decision_policy.md` | How routing decisions are made |
| `router/history.json` | Every routing decision ever made |
| `router/routing_logs.md` | Human-readable decision log |
| `models/routing_patterns.json` | Learned success/failure per (agent, task_type) |
| `models/scoring.json` | Confidence calculation weights |
| `reports/agent_performance.md` | Agent success rates |
| `reports/routing_report.md` | Pattern summary |
| `state/current_routing_state.json` | Last decision metadata |

## Agent assignment logic

**Claude** is preferred for:
- Reasoning, analysis, debugging, planning, architecture
- Documentation, writing, orchestration
- Memory/decision updates
- Anything requiring careful multi-step thought

**Codex** is preferred for:
- Code edits, scripting, file manipulation
- Autolab experiments, workspace repair
- Fast iteration, batch changes

## Learning

The system gets smarter over time:
1. Every routed+executed task is logged with outcome (success/failure)
2. `route-learn` (runs on maintenance) reads history + autolab results
3. Updates `routing_patterns.json` and `agent_profiles.json`
4. Future routing decisions factor in the learned track record

## MCP tools (use from Claude/Codex)

- `route_task(task)` — classify and recommend
- `get_agent_recommendation(task)` — human-readable recommendation
- `get_agent_performance()` — performance report
- `get_routing_history(limit)` — recent decisions
- `run_routing_learn()` — trigger learning update

## Safety

- Destructive tasks (rm -rf, delete all, etc.) are flagged MANUAL_REVIEW and never auto-routed
- Agents are launched via the existing safe wrappers (use-claude, use-codex)
- All safety boundaries from agent-system remain in force
- No dangerous operations are added — this layer only selects which safe wrapper to call
