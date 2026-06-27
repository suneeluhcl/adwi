# Workspace Prompts Index

Master index of all reusable agent prompts across organs.
Agents should check this file when looking for a prompt to drive a task.

## How Prompts Are Used

| Load Timing | Directory | Purpose |
|-------------|-----------|---------|
| **Auto — every session startup** | `skeleton/rules/` | Agent behavior, safety, identity rules |
| **Auto — identity capture** | `dna/identity/prompts/` | Suneel's voice, tone, communication style |
| **On-demand — maintenance** | `spine/docs/` | README updates, workspace health, docs |
| **On-demand — repair** | `hands/prompts/` | Self-repair scripts, fix pipelines |
| **On-demand — training/eval** | `lab/prompts/` | Evolution cycles, eval harnesses, experiments |

---

## spine/docs/ — Operational & Maintenance Prompts

| File | Description | Trigger |
|------|-------------|---------|
| `spine/docs/README_Update_Prompt.md` | Full end-to-end README auto-update for all 12 organs | Manual or nightly cron |

---

## skeleton/rules/ — Agent Behavior Rules (Auto-Loaded at Startup)

| File | Description |
|------|-------------|
| `skeleton/rules/AGENT_SYSTEM.md` | Canonical agent operating rules |
| `skeleton/rules/IDENTITY.md` | Agent identity binding |
| `skeleton/rules/WORKFLOW_RULES.md` | Task and workflow rules |
| `skeleton/rules/SAFETY_BOUNDARIES.md` | Safety gates |
| `skeleton/rules/STARTUP_CHECKLIST.md` | Session boot checklist |

---

## dna/identity/prompts/ — Identity Prompts (Auto-Loaded for Drafting/Comms)

| File | Description |
|------|-------------|
| `dna/identity/prompts/identity_prompt.md` | Full identity system prompt |
| `dna/identity/prompts/communication_prompt.md` | Tone and communication style |

---

## hands/prompts/ — Repair & Fix Prompts

*(drop prompts here for self-repair agents and health-fix pipelines)*

---

## lab/prompts/ — Training, Eval & Evolution Prompts

*(drop prompts here for autolab experiments, eval harnesses, and evolution cycles)*

---

## Adding a New Prompt

1. Drop the `.md` file in the correct organ directory above.
2. Add a row to this index.
3. If it should run automatically, add a cron entry via `hands/bin/` or LaunchAgent plist.

---

*Last updated: 2026-06-26*
