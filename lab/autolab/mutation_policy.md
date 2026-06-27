# Mutation Policy

## Purpose

This policy defines what Autolab may change automatically.

## Allowed Mutable Surface

Autolab may change:

- `autolab/program.md`
- `autolab/evaluator.md`
- `autolab/current_frontier.md`
- `autolab/experiment_queue.md`
- `autolab/reports/`
- `autolab/state/`
- `autolab/templates/`
- `autolab/scripts/`
- Selected workspace scripts in `bin/` when explicitly queued or agent-approved.
- Selected docs in `agent-system/docs/`.
- Selected shared prompt/rule files in `agent-system/shared/`, except safety-critical boundaries.
- Selected maintenance logic in `automation/maintenance/` and `automation/hooks/` when explicitly queued or agent-approved.

## Denylist

Autolab must not autonomously mutate:

- `.agent-backups/`
- `.git/`
- `.env`, secrets, credentials, keys, tokens, or private config.
- `secrets/`
- Financial, billing, account, or purchase-related files.
- Unrelated personal documents.
- `agent-system/shared/SAFETY_BOUNDARIES.md` without explicit human approval.
- `autolab/safeguards.md` without explicit human approval.
- Canonical path declarations that point away from `~/SuneelWorkSpace`.
- Global shell configuration rewrites outside the existing small marked helper block.
- Anything outside `~/SuneelWorkSpace` except launchd symlinks/plists that point back into the workspace.

## Snapshot Rule

Before a mutating experiment, Autolab must snapshot the allowed mutable surface into `autolab/snapshots/`.

## Revert Rule

If an experiment fails safety gates or does not improve score, Autolab must restore the snapshot and write a rollback note.
