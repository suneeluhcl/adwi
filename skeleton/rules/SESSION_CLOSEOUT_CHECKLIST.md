# Session Closeout Checklist

## Update

- `agent-system/memory/SESSION_HANDOFF.md`
- `agent-system/tasks/ACTIVE_TASKS.md`
- `agent-system/tasks/COMPLETED_TASKS.md`
- `agent-system/logs/SESSION_LOG.md`
- `agent-system/state/CURRENT_STATE.json`
- `agent-system/state/WORKSPACE_HEALTH.json` if health changed

## Automatic Safety Net

- `agent-autoclose` runs from `use-codex`, `use-claude`, shell exit hooks, and startup recovery.
- Manual `agent-finish` is optional during normal use, but intentional agent-authored closeout is still preferred when possible.

## Consider Updating

- `agent-system/memory/MEMORY.md` for durable facts.
- `agent-system/memory/DECISIONS.md` for important decisions and reasons.

## Verify

- Important files exist.
- Scripts still run.
- JSON remains valid.
- Any backups are noted.
- The next agent can continue from `SESSION_HANDOFF.md`.

## Final Response

Tell Suneel:

- What changed.
- Important file paths.
- How to use it.
- Any limitations or follow-up recommendations.
