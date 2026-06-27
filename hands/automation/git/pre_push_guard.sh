#!/usr/bin/env bash
# Git pre-push hook — validates READMEs and blocks push if documentation is stale.
# Install: ln -sf ~/SuneelWorkSpace/hands/automation/git/pre_push_guard.sh .git/hooks/pre-push
#
# Flow:
#   1. Detect changed files vs remote
#   2. Update READMEs for affected folders (rule-based, fast)
#   3. Rebuild root README
#   4. Run validator — exit 1 to block push if failed
set -uo pipefail

WORKSPACE="$(git rev-parse --show-toplevel 2>/dev/null || echo "$HOME/SuneelWorkSpace")"
VENV_PY="$WORKSPACE/.venv/bin/python3"
LOG="$WORKSPACE/blood/logs/readme_intelligence.log"
TIMESTAMP="$(date '+%Y-%m-%d %H:%M:%S')"

log() { echo "[$TIMESTAMP] [pre-push] $*" | tee -a "$LOG"; }

# Sanity: Python available?
if [[ ! -x "$VENV_PY" ]]; then
  echo "⚠️  README guard: .venv/bin/python3 not found — skipping (non-blocking)"
  exit 0
fi

echo ""
echo "🔍 README pre-push validation..."

# Read push info from stdin (git provides: local_ref local_sha remote_ref remote_sha)
BLOCKED=0

while read local_ref local_sha remote_ref remote_sha; do
  # Determine changed files
  if [[ "$remote_sha" == "0000000000000000000000000000000000000000" ]]; then
    # New branch — compare to HEAD~1
    CHANGED="$(git diff --name-only HEAD~1 HEAD 2>/dev/null || echo "")"
  else
    CHANGED="$(git diff --name-only "${remote_sha}..${local_sha}" 2>/dev/null || echo "")"
  fi

  if [[ -z "$CHANGED" ]]; then
    echo "  ✅ No file changes — README check skipped."
    continue
  fi

  CHANGED_COUNT=$(echo "$CHANGED" | wc -l | tr -d ' ')
  echo "  📂 $CHANGED_COUNT changed file(s) detected."

  # Step 1: Update READMEs for changed folders (non-fatal)
  echo "  Step 1/3: Updating READMEs for changed folders..."
  UPDATED_FOLDERS=()
  while IFS= read -r f; do
    [[ -z "$f" ]] && continue
    FOLDER="$(dirname "$WORKSPACE/$f")"
    [[ "$FOLDER" == "$WORKSPACE" ]] && continue
    [[ ! -d "$FOLDER" ]] && continue
    # Skip ignored dirs
    case "$FOLDER" in
      */.git*|*/node_modules*|*/.venv*|*/__pycache__*|*/logs/*|*/nerve_inbox*) continue ;;
    esac
    # Avoid updating same folder twice
    ALREADY=0
    for prev in "${UPDATED_FOLDERS[@]:-}"; do
      [[ "$prev" == "$FOLDER" ]] && ALREADY=1 && break
    done
    [[ "$ALREADY" == "1" ]] && continue

    "$VENV_PY" "$WORKSPACE/hands/automation/readme/readme_generator.py" \
      "$FOLDER" --no-claude >> "$LOG" 2>&1 || true
    UPDATED_FOLDERS+=("$FOLDER")
  done <<< "$CHANGED"

  # Step 2: Rebuild root README (non-fatal)
  echo "  Step 2/3: Rebuilding root README..."
  "$VENV_PY" "$WORKSPACE/hands/automation/readme/root_synthesizer.py" >> "$LOG" 2>&1 || \
    log "Root rebuild failed (non-fatal)"

  # Step 3: Validate — THIS IS THE GATE
  echo "  Step 3/3: Validating documentation..."
  if ! "$VENV_PY" "$WORKSPACE/hands/automation/readme/validator.py" 2>&1; then
    echo ""
    echo "❌ README validation FAILED. Push blocked."
    echo "   Run: readme-update-all && readme-root-build"
    echo "   Then retry: git push"
    echo ""
    BLOCKED=1
  fi
done

if [[ "$BLOCKED" == "1" ]]; then
  exit 1
fi

echo "✅ README validation passed. Proceeding with push."
exit 0
