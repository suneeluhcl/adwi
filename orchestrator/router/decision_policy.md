# Routing Decision Policy

This document describes how the orchestrator decides which agent to use for a task.

## Overview

The router uses a three-layer decision process:

1. **Keyword classification** — classify the task into one or more task types
2. **Profile lookup** — check preferred_agent and confidence_weight from task_types.json
3. **History adjustment** — apply learned boosts/penalties from routing_patterns.json

The output is a routing decision: `{agent, task_type, confidence, reasoning}`.

## Decision Rules

### Layer 1: Keyword Classification

- Tokenize the task description (lowercase, strip punctuation)
- Match against keywords in each task type
- Score each task type by number of keyword hits
- Select the top-scoring task type(s); break ties by confidence_weight

### Layer 2: Profile Lookup

- Read `task_types.json` → get `preferred_agent` and `confidence_weight`
- If the task type has no clear preferred agent, fall back to Claude (safer default)

### Layer 3: History Adjustment

- Read `routing_patterns.json` → per (task_type, agent) pair, check:
  - `success_count`: number of tracked successes
  - `failure_count`: number of tracked failures
  - `avg_score_delta`: average autolab score change when this agent ran this type
- Apply history boost formula:
  ```
  adjusted_confidence = base_confidence × (1 + 0.1 × log1p(success_count - failure_count))
  ```
- If adjusted_confidence drops below 0.5 for preferred_agent, recommend secondary_agent instead

### Layer 4: Hybrid Suggestion (Optional)

Some tasks benefit from both agents. The router may suggest a hybrid:
- Claude plans or designs → Codex executes the code changes

Hybrid is suggested when:
- task_type is in: {system_design, planning, orchestration} AND the task also has code_edit keywords

## Safety Rules

1. **Never auto-execute** — route-execute asks for confirmation before launching an agent unless `--auto` is passed explicitly
2. **Never override safety_boundaries** — workspace repair and autolab tasks inherit all existing safety guards
3. **Claude is default fallback** — when confidence is low or task is ambiguous, prefer Claude (more careful)
4. **No routing for destructive tasks** — tasks that match keywords like "delete all", "force push", "rm -rf" are flagged as MANUAL_REVIEW and not auto-routed

## Confidence Scale

| Score | Meaning |
|-------|---------|
| ≥ 0.85 | High — route confidently |
| 0.70–0.84 | Medium — route but note uncertainty |
| 0.50–0.69 | Low — suggest but recommend human confirmation |
| < 0.50 | Very low — present both options, let user decide |

## Logging

Every routing decision is appended to `routing_logs.md` and `history.json` for auditability and learning.
