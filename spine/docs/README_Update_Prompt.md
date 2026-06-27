# 📋 SuneelWorkSpace — README Auto-Update Prompt
## REUSABLE PROMPT — Paste this to your agent after any enhancement session
## Save this file to: ~/SuneelWorkSpace/spine/docs/README_Update_Prompt.md
## Usage: Copy entire contents → paste to Claude/Codex/any agent → done

---

## WHAT THIS PROMPT DOES

This is a standing, reusable prompt. Every time you make enhancements to SuneelWorkSpace,
paste this prompt to your agent. It will:

1. Scan every organ to find what changed since the last README update
2. Read the actual code — not assumptions — to understand what was built
3. Update README.md and all 12 organ README.md files accurately
4. Update CLAUDE.md and AGENTS.md boot sequences if needed
5. Log the enhancement to the Enhancement Log section
6. Commit the documentation update

**Run this after every enhancement session. It takes ~5 minutes and keeps all docs current.**

---

## MANDATORY BOOT SEQUENCE

```
✅ Loading workspace shared brain
```

1. Read `skeleton/rules/AGENT_SYSTEM.md`
2. Read `skeleton/rules/IDENTITY.md`
3. Read `skeleton/rules/SAFETY_BOUNDARIES.md`
4. Read `dna/identity/prompts/identity_prompt.md`
5. Read `brain/memory/SESSION_HANDOFF.md`
6. Read `spine/state/CURRENT_STATE.json`
7. Read `nervous/nerve_registry.json`

Confirm: `✅ Context loaded — beginning README update`

---

## STEP 1 — DETECT WHAT CHANGED

Before writing anything, find out what actually changed since the last README update.

```sh
# What changed in git since last commit
git log --oneline -20 2>/dev/null
git diff HEAD~1 --name-only 2>/dev/null | sort

# What files were modified recently (last 24 hours)
find . -newer README.md -type f \
  -not -path "*/.git/*" \
  -not -path "*/spine/backups/*" \
  -not -path "*/__pycache__/*" \
  -not -path "*/.venv/*" \
  -not -path "*/chroma_store/*" \
  2>/dev/null | sort

# What's in the enhancement log already
python3 -c "
import re
try:
    content = open('README.md').read()
    match = re.search(r'## ENHANCEMENT LOG(.*?)(?=\n## |\Z)', content, re.DOTALL)
    if match:
        entries = re.findall(r'\[(\d{4}-\d{2}-\d{2})\] \[([A-Z]+)\] (.+)', match.group(1))
        print(f'Last {min(5, len(entries))} enhancement log entries:')
        for e in entries[-5:]:
            print(f'  [{e[0]}] [{e[1]}] {e[2]}')
    else:
        print('No enhancement log found')
except:
    print('Could not read README.md')
"

# Current workspace health
cat spine/state/WORKSPACE_HEALTH.json 2>/dev/null | python3 -m json.tool 2>/dev/null | head -10
```

---

## STEP 2 — SCAN CHANGED ORGANS

For each organ that had files changed, do a targeted scan:

```sh
# Identify which organs had changes
python3 -c "
import subprocess, os

organs = ['brain','heart','eyes','ears','nervous','skeleton','blood','hands','mouth','dna','lab','spine']
result = subprocess.run(['git','diff','HEAD~1','--name-only'], capture_output=True, text=True)
changed_files = result.stdout.strip().split('\n') if result.stdout.strip() else []

# Also check recently modified files
import time
recent = []
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['spine/backups','__pycache__','.venv']]
    for f in files:
        path = os.path.join(root, f)
        try:
            if time.time() - os.path.getmtime(path) < 86400:  # last 24h
                recent.append(path)
        except:
            pass

changed_organs = set()
for f in changed_files + recent:
    for organ in organs:
        if f.startswith(f'./{organ}/') or f.startswith(f'{organ}/'):
            changed_organs.add(organ)

print('Changed organs:', sorted(changed_organs) if changed_organs else 'none detected — scanning all')
"
```

For each changed organ, read its key files:

```sh
# For each changed organ, run this scan pattern:
# (Replace <organ> with the actual organ name)

find <organ>/ -type f -name "*.py" | head -20
find <organ>/ -type f -name "*.json" | head -10
find <organ>/ -type f -name "*.md" | head -10
find <organ>/ -type f -name "*.yaml" | head -10

# Read the organ's nerve.json
cat <organ>/nerve.json 2>/dev/null | python3 -m json.tool

# Read key Python files (first 60 lines each)
for f in $(find <organ>/ -name "*.py" -not -path "*/__pycache__/*" | head -5); do
  echo "=== $f ==="; head -60 "$f"; echo ""
done

# Check what CLI commands point into this organ
for cmd in hands/bin/*; do
  if [ -L "$cmd" ]; then
    target=$(readlink "$cmd")
    if echo "$target" | grep -q "<organ>/"; then
      echo "$(basename $cmd) → $target"
    fi
  fi
done
```

Also always scan these regardless of what changed:

```sh
# Always check hands/bin/ for new commands
ls -la hands/bin/ | sort

# Always check DAG pipelines
ls hands/automation/dag/pipelines/ 2>/dev/null

# Always check dashboard routes
grep -n "@app\." eyes/dashboard/server.py 2>/dev/null | head -40

# Always check intent map for new ws commands
cat mouth/dispatcher/intent_map.json 2>/dev/null | python3 -c "
import json, sys
data = json.load(sys.stdin)
intents = data.get('intents', data.get('patterns', []))
print(f'Total intents: {len(intents)}')
for i in intents[-5:]:
    print(f'  {i.get(\"intent\",\"?\")} → {i.get(\"commands\",[])}')
" 2>/dev/null

# Always check model registry
cat heart/model_router/model_registry.json 2>/dev/null | python3 -c "
import json, sys
data = json.load(sys.stdin)
for m in data.get('models', []):
    print(f'  P{m[\"priority\"]}: {m[\"id\"]} ({m[\"provider\"]})')
" 2>/dev/null
```

---

## STEP 3 — UPDATE README.md

After `integrity-guard README.md`, update only the sections that need changing.

**CRITICAL RULES:**
- Only update sections where something actually changed
- Only document what you verified exists in actual files
- Never remove existing accurate content
- Never add content you cannot verify
- Preserve the Enhancement Log — only append, never delete entries

### 3a — Update the Body Map Table (if organs changed)

If any organ's purpose, key files, or structure changed, update its row in the table.
Read the organ's `nerve.json` and actual files before updating.

Format for each row:
```markdown
| 🧠 **Brain** | brain/ | <actual purpose from nerve.json> | <verified key files> |
```

### 3b — Update the Control Center Section (if eyes/ changed)

If `eyes/dashboard/server.py` changed, re-read all routes:
```sh
grep -n "@app\." eyes/dashboard/server.py 2>/dev/null
```

If `eyes/dashboard/static/dashboard.js` changed, re-read quick actions:
```sh
grep -n "QUICK_ACTIONS\|quickAction" eyes/dashboard/static/dashboard.js 2>/dev/null | head -20
```

If `eyes/dashboard/execution/pipeline.py` changed, re-read stage names:
```sh
grep -n "stage\|Stage" eyes/dashboard/execution/pipeline.py 2>/dev/null | head -20
```

Update only the subsections that changed. Keep everything else as-is.

### 3c — Update the Health Repair Section (if health_repair_pipeline.py changed)

```sh
grep -n "async def stage_\|Stage [0-9]\|# Stage" eyes/dashboard/execution/health_repair_pipeline.py 2>/dev/null
grep -n "get_repair_depth\|depth" eyes/dashboard/execution/health_repair_pipeline.py 2>/dev/null | head -10
```

Update stage descriptions based on actual function names and logic found.

### 3d — Update the Evolution Engine Section (if lab/ changed)

```sh
cat lab/evolution/evolution_config.json 2>/dev/null | python3 -m json.tool
grep -n "def run_\|async def " lab/evolution/engine.py 2>/dev/null | head -20
```

### 3e — Update the Model Router Section (if heart/model_router/ changed)

```sh
cat heart/model_router/model_registry.json 2>/dev/null | python3 -m json.tool
```

Update the priority order table with actual model IDs from the registry.

### 3f — Update the Command Reference Section (if hands/bin/ changed)

```sh
# Get complete current command list
for cmd in hands/bin/*; do
  name=$(basename "$cmd")
  if [ -L "$cmd" ]; then
    target=$(readlink "$cmd")
    echo "$name → $target"
  fi
done | sort
```

Add any new commands. Remove any commands that no longer exist.
Group by organ. Format:
```markdown
| `command-name` | What it does | When to use |
```

### 3g — Update the NL Dispatcher Section (if mouth/ changed)

```sh
cat mouth/dispatcher/intent_map.json 2>/dev/null | python3 -c "
import json, sys
data = json.load(sys.stdin)
intents = data.get('intents', data.get('patterns', []))
for i in intents:
    name = i.get('intent', '?')
    cmds = i.get('commands', [])
    kws = i.get('keywords', [])[:3]
    print(f'{name}: {cmds} (keywords: {kws})')
" 2>/dev/null
```

### 3h — Update the Limitations Section

After every enhancement session, re-run:
```sh
agent-doctor 2>/dev/null
python3 nervous/nerve_propagator.py 2>/dev/null
```

Update the Limitations section to reflect current known issues.
Remove issues that have been fixed. Add new issues found.

### 3i — Append to Enhancement Log

**Always append a new entry — never edit existing entries.**

Format:
```markdown
[YYYY-MM-DD] [ORGAN] Brief description of what was built or changed
```

Get today's date:
```sh
date +%Y-%m-%d
```

Determine the organ(s) affected from Step 1 scan.
Write a concise one-line description of what changed.

Example entries:
```
[2026-06-26] [EYES] Added 8-stage autonomous health repair pipeline with score-aware depth
[2026-06-26] [LAB] Built self-directed hypothesis generator with 14-day dedup window
[2026-06-26] [ALL] Human Body Architecture migration — 12 organs, nerve system connected
```

---

## STEP 4 — UPDATE ORGAN README.md FILES

For each organ that had changes, update its `<organ>/README.md`.

If the organ README doesn't exist, create it using this template:

```markdown
# <emoji> <Organ Name> — SuneelWorkSpace Organ

## Purpose
<One sentence from nerve.json>

## What's Inside
<List every subdirectory with one-line description — verified with ls>

## Key Files
<List 5-10 most important files — verified they exist>

## Provides (to other organs)
<From nerve.json provides section — only verified paths>

## Needs (from other organs)
<From nerve.json needs section — only verified paths>

## CLI Commands
<Every command in hands/bin/ that points into this organ>

## How To Add Something Here
<Specific instructions for this organ's structure>

## Recent Changes
<Last 3 enhancement log entries for this organ>
```

If the organ README exists, update only the sections that changed:
- Add new files to "What's Inside" and "Key Files"
- Add new commands to "CLI Commands"
- Update "Recent Changes" with new entry
- Update "Provides" if new capabilities were added

---

## STEP 5 — UPDATE CLAUDE.md AND AGENTS.md

Only update these if the boot sequence or key file paths changed.

```sh
# Check if boot sequence paths still exist
for path in \
  "skeleton/rules/AGENT_SYSTEM.md" \
  "skeleton/rules/IDENTITY.md" \
  "skeleton/rules/SAFETY_BOUNDARIES.md" \
  "dna/identity/prompts/identity_prompt.md" \
  "dna/identity/profile/tone_profile.md" \
  "dna/identity/profile/decision_profile.md" \
  "brain/memory/SESSION_HANDOFF.md" \
  "spine/state/CURRENT_STATE.json" \
  "nervous/mcp/server/config/resource_map.json"; do
  [ -f "$path" ] && echo "✅ $path" || echo "❌ MISSING: $path"
done
```

If any path is missing or moved, update CLAUDE.md and AGENTS.md accordingly.
After `integrity-guard CLAUDE.md` and `integrity-guard AGENTS.md`.

---

## STEP 6 — UPDATE NERVE REGISTRY

If any organ's files, capabilities, or dependencies changed:

```sh
cat nervous/nerve_registry.json | python3 -m json.tool
```

After `integrity-guard nervous/nerve_registry.json`:
- Update `provides` paths for changed organs (verify each path exists)
- Update `needs` paths if dependencies changed
- Update `last_updated` to today's date

```sh
# Verify all paths in nerve_registry.json actually exist
python3 -c "
import json, os
registry = json.load(open('nervous/nerve_registry.json'))
for organ, config in registry['organs'].items():
    for key, path in config.get('provides', {}).items():
        if not os.path.exists(path):
            print(f'❌ {organ}.provides.{key}: {path} MISSING')
    for key, path in config.get('needs', {}).items():
        if not os.path.exists(path):
            print(f'⚠️  {organ}.needs.{key}: {path} MISSING')
print('Nerve registry check complete')
"
```

---

## STEP 7 — VERIFY DOCUMENTATION ACCURACY

Run these checks before finishing:

```sh
echo "=== README UPDATE VERIFICATION ==="

# Check README has all required sections
python3 -c "
required = [
    '## EXECUTIVE SUMMARY',
    '## HUMAN BODY ARCHITECTURE',
    '## FOR AI AGENTS',
    '## CONTROL CENTER',
    '## AUTONOMOUS HEALTH REPAIR',
    '## ENHANCEMENT LOG',
]
content = open('README.md').read()
for section in required:
    status = '✅' if section in content else '❌'
    print(f'{status} {section}')
wc = len(content.split())
print(f'Word count: {wc}')
"

# Check enhancement log has today's entry
python3 -c "
from datetime import date
import re
today = date.today().isoformat()
content = open('README.md').read()
if today in content:
    print(f'✅ Enhancement log has today entry ({today})')
else:
    print(f'⚠️  No entry for today ({today}) in enhancement log')
"

# Check all organ READMEs exist
for organ in brain heart eyes ears nervous skeleton blood hands mouth dna lab spine; do
  [ -f "$organ/README.md" ] && echo "✅ $organ/README.md" || echo "❌ $organ/README.md MISSING"
done

# Check no broken symlinks
broken=0
for cmd in hands/bin/*; do
  if [ -L "$cmd" ] && [ ! -e "$cmd" ]; then
    echo "❌ BROKEN SYMLINK: $(basename $cmd)"
    broken=$((broken+1))
  fi
done
[ $broken -eq 0 ] && echo "✅ All symlinks valid" || echo "❌ $broken broken symlinks found"

echo "=== VERIFICATION COMPLETE ==="
```

---

## STEP 8 — SAVE THIS PROMPT TO WORKSPACE

Make sure this prompt file is saved in the workspace for future use:

```sh
# Ensure the prompt is saved at the canonical location
ls spine/docs/README_Update_Prompt.md 2>/dev/null && echo "✅ Prompt saved" || \
  echo "⚠️  Copy this file to: spine/docs/README_Update_Prompt.md"
```

If not saved yet:
```sh
mkdir -p spine/docs/
cp SuneelWorkSpace_README_Update_Prompt.md spine/docs/README_Update_Prompt.md
echo "✅ Prompt saved to spine/docs/README_Update_Prompt.md"
```

---

## STEP 9 — FINAL CLOSEOUT

```sh
# Notify nervous system
python3 -c "
from nervous.nerve_propagator import notify_change
notify_change('spine', 'documentation_update', 'README.md', 'README and organ docs updated after enhancement session')
" 2>/dev/null || echo "Nerve notification logged"

# Log the documentation update itself
python3 spine/enhancement_logger.py spine "README.md and organ docs updated — all sections current" 2>/dev/null || \
  echo "Enhancement logged"

# Run agent-doctor
agent-doctor 2>/dev/null

# Final agent finish
agent-finish "README update complete — all changed sections updated, enhancement log appended, organ READMEs current"
```

---

## HOW TO USE THIS PROMPT

### Every time you finish an enhancement session:

1. **Copy** the entire contents of this file
2. **Paste** it to Claude, Codex, or any agent in your workspace
3. The agent will automatically detect what changed and update only what needs updating
4. Takes ~5 minutes. Keeps all docs permanently current.

### Where this prompt lives:
```
spine/docs/README_Update_Prompt.md
```

### Quick paste shortcut (add to ~/.zshrc):
```sh
alias readme-update='cat ~/SuneelWorkSpace/spine/docs/README_Update_Prompt.md | pbcopy && echo "✅ README update prompt copied to clipboard — paste to your agent"'
```

Then just run `readme-update` after any enhancement session and paste to your agent.

---

## WHAT THIS PROMPT NEVER DOES

- ❌ Never deletes existing accurate content
- ❌ Never documents features it cannot verify exist
- ❌ Never removes enhancement log entries
- ❌ Never rewrites sections that didn't change
- ❌ Never assumes — always reads actual files first
- ❌ Never touches safety files or identity files

---

## WHAT TRIGGERS A README UPDATE

Run this prompt after any of these:
- New CLI command added to `hands/bin/`
- New API route added to `eyes/dashboard/server.py`
- New organ file or subsystem created
- New DAG pipeline added
- New ws intent added to `mouth/dispatcher/intent_map.json`
- New model added to `heart/model_router/model_registry.json`
- Any organ migrated or restructured
- Health repair pipeline stages changed
- Evolution engine config changed
- Any enhancement session completed by an agent

---

*SuneelWorkSpace README Auto-Update Prompt v1.0*
*Save to: spine/docs/README_Update_Prompt.md*
*Paste to any agent after any enhancement session.*
*Last updated: 2026-06-26*