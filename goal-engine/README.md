# Goal Engine

The goal engine transforms the workspace from a reactive tool system into a goal-driven autonomous system.

**Before:** You tell it what to do (run this script, edit this file).  
**After:** You give it an outcome (achieve X) → it breaks it into tasks → routes each task to the right agent → tracks progress.

## Quick start

```sh
# 1. Create a goal
goal-create "Improve NLU intent routing accuracy" --priority high --complexity medium

# 2. Plan tasks (auto-decomposes into task graph)
goal-plan G001

# 3. Preview what would execute next
goal-execute G001 --dry-run

# 4. Execute the next ready task (asks confirmation)
goal-execute G001

# 5. Check status
goal-status G001

# 6. If a task fails, adapt
goal-adapt G001

# 7. Close the goal when done
goal-complete G001 --result "NLU accuracy improved to 99%"
```

## How it works

```
goal-create "do X"
      ↓
goal-plan → task_graph.json
  (4–6 tasks in dependency order)
      ↓
goal-execute → orchestrator route-task
  (finds ready task → routes to Claude or Codex → you confirm → run)
      ↓
Outcome logged → task_graph updated
      ↓
goal-monitor (runs on maintenance) → detects failures/stuck tasks
      ↓
goal-adapt → retry / swap agent / split task
      ↓
goal-complete / goal-fail
```

## Goal structure

Every goal has:
- `description` — what you want to achieve
- `success_criteria` — what done looks like
- `priority` — low | medium | high | critical
- `complexity` — low | medium | high (controls task count)
- `status` — active | paused | completed | failed

## Task types

Goal tasks map to the orchestrator's 14 task types:
- Claude handles: planning, reasoning, analysis, debugging, documentation, memory_update, orchestration, system_design, logging
- Codex handles: code_edit, scripting, file_manipulation, workspace_repair, autolab_experiment

## File layout

| Path | Purpose |
|------|---------|
| `goals/active_goals.md` | Human-readable list of active goals |
| `goals/completed_goals.md` | Archive of completed goals |
| `goals/failed_goals.md` | Archive of failed goals |
| `graph/task_graph.json` | All tasks and their statuses |
| `graph/dependency_map.json` | Which tasks must complete before others |
| `execution/execution_log.md` | Every task execution event |
| `execution/current_run.json` | State of last/current run |
| `state/goal_state.json` | Counts, last timestamps |
| `state/current_goal.json` | Currently focused goal and ready tasks |
| `reports/goal_report.md` | Auto-generated goal summary |
| `reports/system_progress.md` | Auto-generated system progress |

## Adaptation strategies

When a task fails, `goal-adapt` offers:
- **retry** — reset to pending, try again (up to max_attempts)
- **swap_agent** — switch Claude↔Codex and retry
- **split** — replace with 2 simpler subtasks
- **skip** — skip the task, continue goal without it

## Safety

- Safety keywords in goal descriptions are rejected at creation (rm -rf, delete all, etc.)
- Tasks with `requires_confirmation: true` always prompt before execution
- goal-monitor runs automatically on maintenance (read-only, no agent launch)
- No autonomous agent launches — every execution requires explicit confirmation
- All files are plain JSON/Markdown, deletable without breaking anything else

## MCP tools

From Claude or Codex, use:
- `create_goal(description, priority, complexity)` — create a goal
- `plan_goal(goal_id)` — decompose into tasks
- `get_goal_status(goal_id)` — check progress
- `get_active_goals()` — list all active goals
- `execute_goal(goal_id, dry_run=True)` — preview or queue execution
- `get_execution_log(limit)` — recent execution events

## MCP resources

- `workspace://goals/active` — active goals markdown
- `workspace://goals/status` — goal engine state JSON
- `workspace://goals/graph` — task graph for active goals
- `workspace://goals/history` — execution log
