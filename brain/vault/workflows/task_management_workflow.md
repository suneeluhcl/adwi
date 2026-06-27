# Captured Workflow: Task Management

**Trigger Phrase:** "stay on top of tasks"
**Last Triggered:** 2026-06-26T08:50:07.437426-05:00
**Category:** Life Automation Layer

## Description
Retrieve overall agent status, active goals, and current active task lists to keep you on track.

## Execution Plan (Safe Subsystem Commands)
- `rtk bin/agent-status`
- `rtk bin/goal-status`

## Latest Trace Outputs
### Output of `bin/agent-status`:

```
Workspace: /Users/MAC/SuneelWorkSpace
Canonical instructions: /Users/MAC/SuneelWorkSpace/agent-system/shared/AGENT_SYSTEM.md

Entrypoints:
OK   /Users/MAC/SuneelWorkSpace/AGENTS.md -> /Users/MAC/SuneelWorkSpace/agent-system/shared/AGENT_SYSTEM.md
OK   /Users/MAC/SuneelWorkSpace/CLAUDE.md -> /Users/MAC/SuneelWorkSpace/agent-system/shared/AGENT_SYSTEM.md
OK   /Users/MAC/.codex/AGENTS.md -> /Users/MAC/SuneelWorkSpace/agent-system/shared/AGENT_SYSTEM.md
OK   /Users/MAC/.claude/CLAUDE.md -> /Users/MAC/SuneelWorkSpace/agent-system/shared/AGENT_SYSTEM.md

Health:
status: repairable
checked_at: 2026-06-26T08:50:05-0500
issue_count: 1
- warning: Regular files found in bin/ (expected symlinks only): daily-evolve

Current state:
status: maintained
active_session_detected: True
session_started_at: 2026-06-26T08:43:11-0500
last_activity_timestamp: 2026-06-26T08:43:11-0500
last_auto_closeout_timestamp: 2026-06-26T08:43:11-0500
last_summary: fix relative symlinks and run real-time end-to-end testing
state_updated_at: 2026-06-26T08:48:35-0500
active_agent: Codex CLI
maintenance_enabled: True

Recent handoff:
# Session Handoff

## Latest Handoff

Date: 2026-06-26

Summary: fix relative symlinks and run real-time end-to-end testing

Changed:

- See `agent-system/logs/SESSION_LOG.md` for the session entry.

Verification:

- Run `~/SuneelWorkSpace/bin/agent-status` or `~/SuneelWorkSpace/bin/agent-doctor`.

Open Items:

- Review `agent-system/tasks/ACTIVE_TASKS.md` and `agent-system/tasks/TASK_QUEUE.md`.

Active tasks:
# Active Tasks

## Current

- Keep the shared agent workspace handoff files current after each meaningful agent session.
- Use `agent-doctor` before repairing suspicious workspace issues.
- Use `agent-finish "summary"` at the end of meaningful Claude or Codex sessions.

## Next

- Add project-specific instructions inside individual project folders only when needed.

Goal Engine:
active_goals: 0
completed_goals: 0
tasks_executed: 0
last_execution: None

Orchestrator:
last_agent: claude
last_task_type: debugging
last_learn_at: never
routing_decisions: 10
last_decision: CLAUDE for debugging (78%)
learned_patterns: 0

MCP subsystem:
started: 2026-06-26T08:49:16.827728-05:00
last_reindex: 2026-06-26T08:50:05.892371-05:00
index entries: 483
indexed_at: 2026-06-26T08:50:05.892371-05:00

Autolab:
score: 100.0 / 100
gates_passed: True
loop_status: idle
report: autolab/reports/latest_report.md

System Intelligence:
  ready: True
  system_audit: True
  gap_analysis: True
  system_profile: True
  tool_inventory: True
  research_engine: True
  mcp_resource_coverage: True
```

### Output of `bin/goal-status`:

```
Goal Engine Status — 2026-06-26 08:50

  FAILED (1):
    G001  [░░░░░░░░░░░░░░░░░░░░] 0/4  Improve workspace documentation for new users

  System stats:
    Tasks executed : 0
    Tasks succeeded: 0
    Tasks failed   : 0
    Last execution : None

  Reports: goal-engine/reports/goal_report.md
```

