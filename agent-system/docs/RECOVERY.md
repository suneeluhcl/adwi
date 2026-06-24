# Recovery

## Backups

Backups created by this setup live under:

`~/SuneelWorkSpace/.agent-backups/`

Each setup run uses a timestamped folder when replacing existing files.

## Restore A Backed Up File

Inspect backups first:

```sh
find ~/SuneelWorkSpace/.agent-backups -maxdepth 4 -type f | sort
```

Copy back the file you need:

```sh
cp ~/SuneelWorkSpace/.agent-backups/TIMESTAMP/path/to/file ~/path/to/file
```

## Recreate Workspace Symlinks

```sh
ln -sfn ~/SuneelWorkSpace/agent-system/shared/AGENT_SYSTEM.md ~/SuneelWorkSpace/AGENTS.md
ln -sfn ~/SuneelWorkSpace/agent-system/shared/AGENT_SYSTEM.md ~/SuneelWorkSpace/CLAUDE.md
```

## Recreate Global Symlinks

```sh
mkdir -p ~/.codex ~/.claude
ln -sfn ~/SuneelWorkSpace/agent-system/shared/AGENT_SYSTEM.md ~/.codex/AGENTS.md
ln -sfn ~/SuneelWorkSpace/agent-system/shared/AGENT_SYSTEM.md ~/.claude/CLAUDE.md
```

## Validate

```sh
~/SuneelWorkSpace/bin/agent-status
~/SuneelWorkSpace/bin/agent-doctor
python3 -m json.tool ~/SuneelWorkSpace/agent-system/state/CURRENT_STATE.json >/dev/null
python3 -m json.tool ~/SuneelWorkSpace/agent-system/state/WORKSPACE_HEALTH.json >/dev/null
python3 -m json.tool ~/SuneelWorkSpace/agent-system/state/INDEX.json >/dev/null
```

## Run Safe Repair

```sh
~/SuneelWorkSpace/bin/agent-repair
```

This can recreate known symlinks, missing directories, executable permissions, and generated JSON state. It backs up files before replacing malformed generated JSON.

## If Symlinks Do Not Work

Replace the symlink with a tiny loader file that says:

```md
# Shared Agent Instructions

Read and follow:

`~/SuneelWorkSpace/agent-system/shared/AGENT_SYSTEM.md`
```

Then run:

```sh
~/SuneelWorkSpace/bin/agent-doctor
```
