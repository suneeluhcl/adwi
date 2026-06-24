# SuneelWorkSpace

This is the shared local workspace and control center for Suneel Bikkasani. It is centered at:

`~/SuneelWorkSpace`

The purpose of this workspace is to give Claude Code and Codex CLI the same project instructions, user context, memory, task state, health checks, logs, maintenance, and session handoff files.

## How To Use It

Start agents from this workspace when possible:

```sh
cd ~/SuneelWorkSpace
```

Helpful commands:

```sh
~/SuneelWorkSpace/bin/agent-start
~/SuneelWorkSpace/bin/agent-status
~/SuneelWorkSpace/bin/agent-doctor
~/SuneelWorkSpace/bin/agent-repair
~/SuneelWorkSpace/bin/agent-maintain
~/SuneelWorkSpace/bin/agent-autoclose
~/SuneelWorkSpace/bin/agent-finish "Short summary of what changed"
~/SuneelWorkSpace/bin/use-codex
~/SuneelWorkSpace/bin/use-claude
```

If shell aliases were installed, these shorter commands are also available in new terminals:

```sh
swroot
swstatus
swdoctor
swrepair
swcodex
swclaude
```

## Main Idea

The canonical instruction file is:

`~/SuneelWorkSpace/agent-system/shared/AGENT_SYSTEM.md`

The root files `AGENTS.md` and `CLAUDE.md` point to that same canonical file. Global tool files under `~/.codex` and `~/.claude` also point back here, so both tools discover the same defaults.

## Shared Memory

Shared memory, health, logs, and handoff files live under:

`~/SuneelWorkSpace/agent-system/`

Agents should read the startup files at the beginning of a session and update the handoff, task, log, health, and state files at closeout.

## Self-Maintenance

The workspace includes local maintenance commands:

- `agent-doctor`: checks health.
- `agent-repair`: safely repairs known small issues.
- `agent-maintain`: runs doctor, repair, index refresh, backup, and report generation.
- `agent-autoclose`: automatically checkpoints session handoff, logs, and state on wrapper exit, shell exit, or startup recovery.
- `workspace-context`: prints the exact files an agent should load first.
- `workspace-report`: writes `automation/reports/status-latest.md`.

If launchd is configured, a user-level background job runs lightweight maintenance periodically. The actual logic still lives in `~/SuneelWorkSpace/bin`.

Manual `agent-finish` is optional during normal use because automatic closeout is wired into the wrappers and shell hook.

## Autolab Self-Improvement

Autolab is the workspace autoresearch subsystem:

`~/SuneelWorkSpace/autolab/`

It evaluates workspace fitness, runs bounded experiments, snapshots allowed files, keeps changes only when the score improves and safety gates pass, and otherwise reverts automatically.

Useful commands:

```sh
~/SuneelWorkSpace/autolab/scripts/autolab-eval
~/SuneelWorkSpace/autolab/scripts/autolab-once
~/SuneelWorkSpace/autolab/scripts/autolab-report
~/SuneelWorkSpace/autolab/scripts/autolab-frontier
```

## Projects

New projects should go in:

`~/SuneelWorkSpace/projects/`

Each project can still have its own repository and local instructions. Workspace-level instructions remain the default source of truth unless a project-specific file gives more specific guidance.

## Existing Context Preserved

- Personal engineering workspace for Suneel Bikkasani.
- Mac environment: Apple M4 Max, macOS 15 noted in the previous README.
- Codex-related bootstrap files may also exist in `codex/`.
- Previous work: Adwi local AI OS archive at `https://github.com/sndboxTesting/adwi`.

## More Documentation

- `agent-system/docs/HOW_IT_WORKS.md`
- `agent-system/docs/FILE_MAP.md`
- `agent-system/docs/RECOVERY.md`
- `agent-system/docs/AUTOMATION.md`
- `agent-system/docs/OPERATOR_GUIDE.md`
