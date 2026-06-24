# Operator Guide

## Start Here

Open a new terminal and run:

```sh
swroot
swstatus
```

If aliases are not loaded yet:

```sh
cd ~/SuneelWorkSpace
~/SuneelWorkSpace/bin/agent-status
```

## Start An Agent

```sh
swcodex
```

or:

```sh
swclaude
```

The wrappers enter `~/SuneelWorkSpace`, run startup preflight, and then launch the tool.

## Check Health

```sh
swdoctor
```

## Repair Safe Issues

```sh
swrepair
```

## Finish A Session

Normal use does not require a manual finish command. `use-codex`, `use-claude`, shell exit hooks, and the next startup all run automatic closeout.

You can still force a human-written closeout when useful:

```sh
~/SuneelWorkSpace/bin/agent-finish "Short summary of what changed"
```

## What To Remember

- The main workspace is `~/SuneelWorkSpace`.
- The main instruction file is `agent-system/shared/AGENT_SYSTEM.md`.
- Memory lives in `agent-system/memory/`.
- If something looks wrong, run `agent-doctor` first and `agent-repair` second.
