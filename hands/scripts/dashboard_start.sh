#!/bin/bash
# Start Control Center dashboard from new eyes/ location
W="$(cd "$(dirname "$0")/../.." && pwd)"
source "$W/.venv/bin/activate" 2>/dev/null || true
cd "$W"
exec uvicorn eyes.dashboard.server:app --host 0.0.0.0 --port 7777 --reload
