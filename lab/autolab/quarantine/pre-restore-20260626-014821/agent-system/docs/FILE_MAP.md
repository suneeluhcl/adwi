# File Map

## Root

- `AGENTS.md`: Codex-style workspace entrypoint. Should point to `agent-system/shared/AGENT_SYSTEM.md`.
- `CLAUDE.md`: Claude-style workspace entrypoint. Should point to `agent-system/shared/AGENT_SYSTEM.md`.
- `README.md`: Human-friendly overview of the workspace.
- `.gitignore`: Basic local ignore rules.
- `bin/`: Helper scripts.
- `automation/`: Doctor, repair, launchd, hooks, and generated reports.
- `autolab/`: Safe workspace autoresearch subsystem for iterative self-improvement.
- `projects/`: Place for individual projects.

## Shared Instructions

- `agent-system/shared/AGENT_SYSTEM.md`: Canonical shared instruction source.
- `agent-system/shared/IDENTITY.md`: User identity, preferences, and stable context.
- `agent-system/shared/WORKFLOW_RULES.md`: How agents should inspect, execute, verify, and close out work.
- `agent-system/shared/STARTUP_CHECKLIST.md`: Files to read at session start.
- `agent-system/shared/SESSION_CLOSEOUT_CHECKLIST.md`: Files to update before ending a session.
- `agent-system/shared/SAFETY_BOUNDARIES.md`: Non-negotiable safety limits.

## Memory

- `agent-system/memory/MEMORY.md`: Durable facts and stable context.
- `agent-system/memory/DECISIONS.md`: Important decisions and reasons.
- `agent-system/memory/SESSION_HANDOFF.md`: Latest handoff from the prior agent/session.
- `agent-system/memory/NOTES.md`: Temporary or low-stakes notes.

## Tasks

- `agent-system/tasks/ACTIVE_TASKS.md`: Current tasks and next steps.
- `agent-system/tasks/COMPLETED_TASKS.md`: Finished work.
- `agent-system/tasks/TASK_QUEUE.md`: Queued future work.

## Logs And State

- `agent-system/logs/SESSION_LOG.md`: Append-only work log.
- `agent-system/logs/MAINTENANCE_LOG.md`: Append-only maintenance log.
- `agent-system/logs/CHANGE_LOG.md`: Human-readable change history.
- `agent-system/state/CURRENT_STATE.json`: Machine-readable current state.
- `agent-system/state/WORKSPACE_HEALTH.json`: Latest doctor result.
- `agent-system/state/INDEX.json`: Generated index of shared files and scripts.
- `agent-system/state/ACTIVE_SESSION.json`: Current shell/wrapper session marker used by automatic closeout.
- `agent-system/state/LAST_KNOWN_GOOD.json`: Latest validation snapshot after a healthy maintenance pass.

## Templates

- `agent-system/templates/SESSION_SUMMARY_TEMPLATE.md`: Handoff summary template.
- `agent-system/templates/TASK_TEMPLATE.md`: Task entry template.
- `agent-system/templates/DECISION_TEMPLATE.md`: Decision entry template.
- `agent-system/templates/STATUS_REPORT_TEMPLATE.md`: Status report template.

## Docs

- `agent-system/docs/HOW_IT_WORKS.md`: Detailed system explanation.
- `agent-system/docs/FILE_MAP.md`: This file.
- `agent-system/docs/RECOVERY.md`: How to restore backups and repair symlinks.
- `agent-system/docs/AUTOMATION.md`: How maintenance automation works.
- `agent-system/docs/OPERATOR_GUIDE.md`: Short usage guide for Suneel.

## Scripts

- `bin/agent-start`: Runs startup preflight and prints context.
- `bin/agent-status`: Shows current state, health, handoff, and tasks.
- `bin/agent-finish`: Updates handoff, session log, state, index, and report.
- `bin/agent-autoclose`: Automatic idempotent closeout for wrapper exit, shell exit, inactivity, and startup recovery.
- `bin/agent-doctor`: Runs full health checks.
- `bin/agent-repair`: Safely repairs known issues.
- `bin/agent-maintain`: Runs recurring maintenance.
- `bin/use-codex`: Runs startup preflight, then launches Codex from the workspace.
- `bin/use-claude`: Runs startup preflight, then launches Claude from the workspace.
- `bin/workspace-context`: Prints the required startup files and compact context.
- `bin/workspace-backup`: Creates a timestamped core backup.
- `bin/workspace-index`: Regenerates `INDEX.json`.
- `bin/workspace-report`: Regenerates the latest markdown status report.
- `bin/workspace-changes`: Shows recent git or filesystem changes.

## Autolab

- `autolab/program.md`: Research organization instructions for improving the workspace.
- `autolab/evaluator.md`: Score and acceptance rules.
- `autolab/mutation_policy.md`: Allowlist and denylist for autonomous changes.
- `autolab/safeguards.md`: Safety and rollback rules.
- `autolab/results.tsv`: Append-only experiment history.
- `autolab/current_frontier.md`: Current best-known improvement state.
- `autolab/state/latest_eval.json`: Latest score breakdown.
- `autolab/meta/insights.md`: Human-readable learning summary.
- `autolab/meta/patterns.json`: Successful mutation and target-area patterns.
- `autolab/meta/failure_patterns.json`: Repeated failure patterns and avoidance guidance.
- `autolab/meta/strategy_versions/`: Snapshots of `program.md` before strategy evolution.
- `autolab/scripts/`: Autolab command suite.
