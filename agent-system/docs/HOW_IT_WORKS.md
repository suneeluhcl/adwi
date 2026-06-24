# How It Works

## Purpose

This workspace makes Claude Code and Codex CLI share the same local instructions, memory, task state, session log, health checks, maintenance reports, and handoff files.

## Core Design

The canonical instruction file is:

`~/SuneelWorkSpace/agent-system/shared/AGENT_SYSTEM.md`

The workspace root files `AGENTS.md` and `CLAUDE.md` point to that same file. Global files under `~/.codex` and `~/.claude` also point back to it.

This keeps one source of truth while still giving each tool the file name it expects.

## Startup Flow

At session start, an agent should read:

1. Shared behavior rules.
2. User identity and preferences.
3. Workflow rules.
4. Memory and decisions.
5. Active tasks and latest handoff.
6. Machine-readable current state.

Run:

```sh
~/SuneelWorkSpace/bin/agent-start
```

`agent-start` runs a safe preflight repair, refreshes the index, logs startup, and prints the context brief.

## Closeout Flow

At the end of useful work, an agent should update:

- Latest handoff.
- Active/completed tasks.
- Session log.
- Current state JSON.
- Durable memory or decisions, if needed.

Run:

```sh
~/SuneelWorkSpace/bin/agent-finish "Short summary"
```

## Maintenance Flow

The maintenance system is intentionally small:

- `agent-doctor` detects missing files, broken or drifting symlinks, malformed JSON, missing execute permissions, shell alias drift, launchd status, and duplicate instruction files.
- `agent-repair` safely recreates known symlinks, required directories, executable permissions, and generated JSON files.
- `agent-maintain` runs doctor, repair where safe, index generation, report generation, and a lightweight backup.
- `workspace-index` refreshes `agent-system/state/INDEX.json`.
- `workspace-report` writes `automation/reports/status-latest.md`.

All maintenance remains local and file-based.

## Why Files

Markdown and JSON files are easy to inspect, back up, sync, and repair. They also work across agents without a database, server, or vendor-specific memory feature.

## Autolab Learning Flow

Autolab is the workspace autoresearch system in `~/SuneelWorkSpace/autolab`.

Autolab v2 learns from results:

1. `autolab-analyze` reads `results.tsv`.
2. It updates successful patterns in `autolab/meta/patterns.json`.
3. It updates failures in `autolab/meta/failure_patterns.json`.
4. It appends lessons to `autolab/meta/insights.md`.
5. `autolab-once` uses those patterns to choose safer future experiments.

Autolab can evolve `program.md`, but only with strategy snapshots and safety checks.
