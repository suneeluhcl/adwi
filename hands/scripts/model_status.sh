#!/bin/bash
W="$(cd "$(dirname "$0")/../.." && pwd)"
source "$W/.venv/bin/activate" 2>/dev/null || true
cd "$W"
python3 -c "
import sys; sys.path.insert(0,'.')
from heart.model_router.quota_tracker import get_status
import json; print(json.dumps(get_status(), indent=2))
"
