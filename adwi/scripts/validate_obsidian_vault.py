#!/usr/bin/env python3
"""
adwi/scripts/validate_obsidian_vault.py — Obsidian vault health check.

Checks vault structure, templates, .obsidian config, and marker hygiene.
stdlib-only, fast, safe to run at any time.

Exit 0: all checks pass.
Exit 1: one or more checks failed (failures listed above exit line).
"""

import json
import subprocess
import sys
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
_ADWI       = Path(__file__).resolve().parent.parent      # adwi/
_WORKSPACE  = _ADWI.parent                                # SuneelWorkSpace/
_VAULT      = _WORKSPACE / "obsidian-vault"
_OBSIDIAN   = _VAULT / ".obsidian"
_TEMPLATES  = _VAULT / "templates"
_KNOWLEDGE  = _VAULT / "knowledge"

# Section headings that every Daily Note must contain
# (mirrors _TEMPLATE in adwi/obsidian_utils.py — keep in sync).
_DAILY_NOTE_SECTIONS = [
    "## Current Focus",
    "## Decisions",
    "## Ideas",
    "## Bugs / Fixes",
    "## Pending Approval",
]

# Markers whose START tag must appear at most once per daily note.
_SINGLE_MARKERS = [
    "ADWI:DAILY-SUMMARY",
    "ADWI:DAILY-BRIEF",
    "ADWI:DAILY-PLAN",
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def _git_tracks(path: Path) -> bool:
    """Return True if git considers the file tracked."""
    try:
        out = subprocess.run(
            ["git", "ls-files", str(path)],
            capture_output=True, text=True,
            cwd=str(_WORKSPACE), timeout=5,
        )
        return bool(out.stdout.strip())
    except Exception:
        return False


def _load_json(path: Path):
    """Return parsed JSON or None on error."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


# ── Check functions ────────────────────────────────────────────────────────────

def check_vault_dirs(failures):
    required = [
        _VAULT / "daily-notes",
        _VAULT / "knowledge",
        _VAULT / "projects" / "ideas",
        _VAULT / "templates",
    ]
    for d in required:
        if not d.is_dir():
            failures.append(f"missing directory: {d.relative_to(_WORKSPACE)}")


def check_template_files(failures):
    names = [
        "Daily Note.md",
        "Idea Note.md",
        "Decision Record.md",
        "Bug Fix Note.md",
        "Project Note.md",
        "Weekly Review.md",
    ]
    for name in names:
        if not (_TEMPLATES / name).exists():
            failures.append(f"missing template: templates/{name}")


def check_obsidian_config(failures):
    tracked = {
        "core-plugins.json": None,
        "templates.json":    {"folder": "templates"},
        "daily-notes.json":  {
            "folder":   "daily-notes",
            "format":   "YYYY-MM-DD",
            "template": "templates/Daily Note",
        },
    }
    for fname, expected in tracked.items():
        path = _OBSIDIAN / fname
        if not path.exists():
            failures.append(f"missing .obsidian config: .obsidian/{fname}")
            continue
        data = _load_json(path)
        if data is None:
            failures.append(f"invalid JSON: .obsidian/{fname}")
            continue
        if expected:
            for key, val in expected.items():
                if data.get(key) != val:
                    failures.append(
                        f".obsidian/{fname}: expected {key}={val!r}, got {data.get(key)!r}"
                    )


def check_volatile_not_tracked(failures):
    volatile = [
        "workspace.json",
        "workspace-mobile.json",
        "graph.json",
        "app.json",
        "appearance.json",
    ]
    for fname in volatile:
        p = _OBSIDIAN / fname
        if _git_tracks(p):
            failures.append(
                f"volatile file is tracked by git: .obsidian/{fname} — add to .gitignore"
            )


def check_daily_note_template(failures):
    tmpl = _TEMPLATES / "Daily Note.md"
    if not tmpl.exists():
        return  # already caught by check_template_files
    text = tmpl.read_text(encoding="utf-8")
    for section in _DAILY_NOTE_SECTIONS:
        if section not in text:
            failures.append(
                f"templates/Daily Note.md missing section: {section!r}"
                " (out of sync with obsidian_utils._TEMPLATE)"
            )


def check_idea_note_template(failures):
    tmpl = _TEMPLATES / "Idea Note.md"
    if not tmpl.exists():
        return
    text = tmpl.read_text(encoding="utf-8")
    for required in ("{{title}}", "{{description}}", "## Captured Updates"):
        if required not in text:
            failures.append(
                f"templates/Idea Note.md missing required content: {required!r}"
            )


def check_knowledge_notes(failures):
    notes = [
        "Capture Workflow.md",
        "Review Workflow.md",
        "Planning Workflow.md",
        "Template Guide.md",
        "Obsidian Maintenance.md",
    ]
    for name in notes:
        if not (_KNOWLEDGE / name).exists():
            failures.append(f"missing knowledge note: knowledge/{name}")


def check_duplicate_markers(failures):
    dn_dir = _VAULT / "daily-notes"
    if not dn_dir.exists():
        return
    for note_path in sorted(dn_dir.glob("????-??-??.md")):
        try:
            text = note_path.read_text(encoding="utf-8")
        except Exception:
            continue
        for marker in _SINGLE_MARKERS:
            start_tag = f"<!-- {marker}:START -->"
            count = text.count(start_tag)
            if count > 1:
                failures.append(
                    f"duplicate marker ({count}×) in "
                    f"daily-notes/{note_path.name}: {start_tag}"
                )


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    failures: list[str] = []

    checks = [
        ("vault directories",        check_vault_dirs),
        ("template files",           check_template_files),
        (".obsidian config",         check_obsidian_config),
        ("volatile files untracked", check_volatile_not_tracked),
        ("daily note template sync", check_daily_note_template),
        ("idea note template",       check_idea_note_template),
        ("knowledge notes",          check_knowledge_notes),
        ("duplicate markers",        check_duplicate_markers),
    ]

    for label, fn in checks:
        before = len(failures)
        fn(failures)
        added = len(failures) - before
        status = "OK" if added == 0 else f"FAIL ({added} issue{'s' if added > 1 else ''})"
        print(f"  {'✓' if added == 0 else '✗'} {label:<30} {status}")

    if failures:
        print()
        for f in failures:
            print(f"  FAIL: {f}")
        print()
        print("obsidian vault validation FAILED")
        return 1

    print()
    print("obsidian vault validation OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
