# Safety Boundaries

## Purpose

These boundaries apply to Claude Code, Codex CLI, and any future local automation working in `~/SuneelWorkSpace`.

## Never Do

- Do not perform purchases, billing changes, paid upgrades, or account changes.
- Do not delete important files without explicit approval.
- Do not run destructive git or filesystem commands without explicit approval.
- Do not store secrets, passwords, tokens, private keys, or billing details in shared memory.
- Do not create hidden databases or opaque state systems for agent memory.

## Before Risky Changes

- Inspect the existing file or system.
- Create a timestamped backup.
- Prefer a reversible change.
- Explain the risk if user approval is required.

## Safe Defaults

- Plain markdown and JSON files.
- Symlinks or thin wrappers for tool discovery.
- Local scripts that can be opened and read.
- Lightweight launchd jobs that call workspace scripts and write logs.

## Repair Limits

Automatic repair may:

- Recreate missing required directories and files.
- Recreate known symlinks.
- Restore script executable permissions.
- Regenerate JSON index and health files.
- Back up and replace malformed generated JSON files.

Automatic repair must not:

- Delete human-authored content.
- Merge two workspaces blindly.
- Rewrite unrelated shell configuration.
- Change paid services or accounts.
