# Resource Reference

Resources are read-only views of authoritative workspace files. They are accessed by URI.

## Workspace Intelligence

| URI | Source file | Description |
|-----|-------------|-------------|
| `workspace://overview` | `agent-system/shared/AGENT_SYSTEM.md` | Canonical workspace instructions |
| `workspace://identity` | `agent-system/shared/IDENTITY.md` | Agent identity and context |
| `workspace://workflow-rules` | `agent-system/shared/WORKFLOW_RULES.md` | Workflow rules |
| `workspace://safety` | `agent-system/shared/SAFETY_BOUNDARIES.md` | Safety boundaries |
| `workspace://startup-checklist` | `agent-system/shared/STARTUP_CHECKLIST.md` | Startup checklist |

## Memory & Decisions

| URI | Source file | Description |
|-----|-------------|-------------|
| `workspace://memory` | `agent-system/memory/MEMORY.md` | Persistent memory |
| `workspace://decisions` | `agent-system/memory/DECISIONS.md` | Important decisions |
| `workspace://handoff` | `agent-system/memory/SESSION_HANDOFF.md` | Latest session handoff |
| `workspace://notes` | `agent-system/memory/NOTES.md` | Temporary notes |

## Tasks

| URI | Source file | Description |
|-----|-------------|-------------|
| `workspace://tasks/active` | `agent-system/tasks/ACTIVE_TASKS.md` | Active tasks |
| `workspace://tasks/queue` | `agent-system/tasks/TASK_QUEUE.md` | Task queue |
| `workspace://tasks/completed` | `agent-system/tasks/COMPLETED_TASKS.md` | Completed tasks |

## State & Health

| URI | Source file | Description |
|-----|-------------|-------------|
| `workspace://state` | `agent-system/state/CURRENT_STATE.json` | Current state JSON |
| `workspace://health` | `agent-system/state/WORKSPACE_HEALTH.json` | Workspace health JSON |

## Autolab

| URI | Source file | Description |
|-----|-------------|-------------|
| `workspace://autolab/frontier` | `autolab/current_frontier.md` | Current frontier score and strategy |
| `workspace://autolab/program` | `autolab/program.md` | Autolab program and mutation policy |
| `workspace://autolab/insights` | `autolab/meta/insights.md` | Learning insights |
| `workspace://autolab/patterns` | `autolab/meta/patterns.json` | Observed patterns |
| `workspace://autolab/failures` | `autolab/meta/failure_patterns.json` | Failure patterns |
| `workspace://autolab/learning` | `autolab/meta/learning_log.md` | Full learning log |

## Derived Views

| URI | Source | Description |
|-----|--------|-------------|
| `workspace://digest` | state + health + handoff + tasks | Compact one-page workspace summary |
| `workspace://logs/recent` | `agent-system/logs/SESSION_LOG.md` | Last 200 lines of session log |
| `workspace://mcp/state` | `mcp/server/state/mcp_state.json` | MCP subsystem state |

## Prompts (reusable context assembles)

| Name | Description |
|------|-------------|
| `startup_context` | State + health + handoff + tasks — use on session start |
| `closeout_context` | Checklist of what to update on session close |
| `workspace_status_brief` | One-page status summary |
| `autolab_summary` | Frontier + insights + failure patterns |
| `maintenance_summary` | State + health + last index metadata |
