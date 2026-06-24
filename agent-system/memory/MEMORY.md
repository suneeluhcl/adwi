# Shared Memory

## Durable Facts

- Canonical workspace path: `~/SuneelWorkSpace`.
- This workspace is intended as a central library for both Claude Code and Codex CLI.
- This workspace is also intended as a shared control center for automation, maintenance, health checks, and handoff.
- Suneel may use either agent at any time.
- Both agents should read and write shared instructions, memory, task state, and handoff files.
- Suneel wants local automation and workflows.
- Suneel is new to development and prefers clear, precise, step-by-step behavior.
- Approved local setup actions should be performed directly by the agent when safe.
- Avoid money-related actions.
- Avoid destructive actions without explicit approval.
- Prefer clean organization, minimal duplication, and a single source of truth.
- Suneel prefers a final clearly labeled summary block that can be copied back into Copilot when requested.
- Suneel wants the workspace to feel alive, self-maintaining, self-repairing, and state of the art while staying simple and transparent.

## Environment Notes

- Prior workspace README noted: Suneel Bikkasani, Apple M4 Max, macOS 15.
- New projects should generally live under `~/SuneelWorkSpace/projects/`.
- Existing README noted Codex bootstrap files may live in `~/SuneelWorkSpace/codex/`.
- Existing README noted previous work: Adwi local AI OS archive at `https://github.com/sndboxTesting/adwi`.
- Background maintenance, if enabled, should be local, lightweight, and implemented with launchd calling scripts inside the workspace.

## Memory Rules

- Store only stable, useful facts here.
- Do not store secrets, tokens, passwords, private keys, billing data, or temporary noise.
- Prefer updating an existing bullet over adding duplicates.
