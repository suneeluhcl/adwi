# Anticipation Strategy

Autolab may inspect anticipation quality and recommend improvements, but it must not auto-execute suggested actions.

## Inputs

- `anticipation/prediction_memory.json`
- `anticipation/behavior_patterns.json`
- `anticipation/action_suggestions.md`
- `anticipation/reports/anticipation_report.md`

## What Autolab Can Do

- Identify repeated workflow sequences.
- Recommend better suggestions.
- Detect low-value or noisy suggestions.
- Report whether suggestions remain safe and bounded.

## Limits

- Suggestions are not commands.
- Do not auto-send messages.
- Do not run destructive actions.
- Do not install tools or change accounts.
