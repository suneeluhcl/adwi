# Adaptive Identity Strategy

Autolab may analyze identity effectiveness, but it must not override identity automatically.

## Inputs

- `identity/adaptive/feedback_log.json`
- `identity/adaptive/signal_weights.json`
- `identity/adaptive/signal_memory.json`
- `identity/adaptive/pattern_updates.json`
- `identity/adaptive/drift_guardrails.json`
- `identity/adaptive/reports/adaptation_report.md`

## What Autolab Can Do

- Detect repeated rejection/edit patterns.
- Recommend small identity tweaks.
- Report degraded output trends.
- Compare active adjustments against drift guardrails.
- Check whether weighted signals indicate improving or degrading identity quality.

## What Autolab Must Not Do

- Override `identity/profile/identity_profile.md`.
- Remove explicit user preferences.
- Change safety boundaries.
- Make large tone shifts automatically.
- Send messages, install tools, or modify external services.
