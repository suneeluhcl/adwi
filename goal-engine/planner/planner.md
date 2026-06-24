# Goal Planner

The planner converts a goal into an ordered task graph.

## How it works

1. `goal-plan GOAL_ID` is called
2. Planner reads the goal from `task_graph.json`
3. Generates tasks using heuristics + decomposition policy
4. Writes tasks to `task_graph.json`
5. Writes dependency map to `dependency_map.json`
6. Updates `current_goal.json` with ready tasks
7. Updates `active_goals.md` with task count

## Planning Modes

- **Auto** (default): planner generates tasks based on heuristics
- **Guided**: agent prompts you for each task before adding (use `--guided`)

## Task status lifecycle

```
pending → ready → running → succeeded
                          → failed → retrying → ready (or aborted)
```

A task is `ready` when all its dependencies are `succeeded`.

## Execution order

Tasks are ordered topologically (dependencies first). Tasks with no remaining
dependencies that are still `pending` become `ready`. goal-execute picks the
first ready task from the list.

## Re-planning (via goal-adapt)

If a task fails repeatedly, goal-adapt can:
- Split the task into smaller parts
- Swap the agent (Claude → Codex or vice versa)
- Add a pre-task (gather more context first)
- Mark the task as `aborted` and continue goal without it
