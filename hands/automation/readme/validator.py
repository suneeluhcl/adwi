#!/usr/bin/env python3
"""
Pre-push README Validator — checks that all changed folders have updated READMEs.
Exits 1 (blocks push) if any condition fails.
"""
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

WORKSPACE = Path(subprocess.check_output(
    ["git", "rev-parse", "--show-toplevel"], text=True,
    cwd=os.path.dirname(os.path.abspath(__file__))
).strip())

IGNORED_DIRS = {
    ".git", "node_modules", ".venv", "__pycache__", "nerve_inbox",
    "logs", "state", "__init__", ".DS_Store",
}
REQUIRED_SECTIONS = ["Purpose", "Contents", "Change Log"]

ORGANS = [
    "brain", "heart", "eyes", "ears", "nervous", "skeleton",
    "blood", "hands", "mouth", "dna", "lab", "spine",
]


def _get_changed_files(base_ref: str = None) -> list:
    """Detect files changed since divergence from main/origin."""
    # Try comparing to remote main
    for ref in [base_ref, "origin/main", "origin/master", "main", "master"]:
        if ref is None:
            continue
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", f"HEAD...{ref}"],
                capture_output=True,
                text=True,
                cwd=str(WORKSPACE),
            )
            if result.returncode == 0 and result.stdout.strip():
                return [f.strip() for f in result.stdout.splitlines() if f.strip()]
        except Exception:
            pass

    # Fallback: staged + unstaged changes
    changed = set()
    for cmd in [["git", "diff", "--name-only", "--cached"],
                ["git", "diff", "--name-only"]]:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(WORKSPACE))
            if result.returncode == 0:
                for f in result.stdout.splitlines():
                    if f.strip():
                        changed.add(f.strip())
        except Exception:
            pass
    return sorted(changed)


def _files_to_folders(changed_files: list) -> set:
    folders = set()
    for f in changed_files:
        path = WORKSPACE / f
        folder = path.parent
        rel_parts = folder.relative_to(WORKSPACE).parts if folder.is_relative_to(WORKSPACE) else ()
        if not rel_parts:
            continue
        if any(p in IGNORED_DIRS for p in rel_parts):
            continue
        if folder.is_dir():
            folders.add(folder)
    return folders


def _readme_up_to_date(folder: Path) -> bool:
    readme = folder / "README.md"
    if not readme.exists():
        return False
    readme_mtime = readme.stat().st_mtime
    try:
        for item in folder.iterdir():
            if item.name in {"README.md", ".DS_Store"} or item.name.startswith("."):
                continue
            try:
                if item.stat().st_mtime > readme_mtime + 1:  # 1s grace period
                    return False
            except Exception:
                pass
    except Exception:
        pass
    return True


def _has_required_sections(folder: Path) -> bool:
    readme = folder / "README.md"
    if not readme.exists():
        return False
    try:
        content = readme.read_text(errors="ignore")
        return all(s.lower() in content.lower() for s in REQUIRED_SECTIONS)
    except Exception:
        return False


def _root_readme_newer_than_organs() -> bool:
    root_readme = WORKSPACE / "README.md"
    if not root_readme.exists():
        return False
    root_mtime = root_readme.stat().st_mtime
    for organ in ORGANS:
        organ_readme = WORKSPACE / organ / "README.md"
        if organ_readme.exists():
            try:
                if organ_readme.stat().st_mtime > root_mtime + 1:
                    return False
            except Exception:
                pass
    return True


def validate_pre_push(changed_files: list = None, strict: bool = False) -> bool:
    if changed_files is None:
        changed_files = _get_changed_files()

    if not changed_files:
        print("✅ No changed files detected — README validation skipped.")
        return True

    # Filter out README.md changes, logs, data files, and deeply nested paths
    code_files = [
        f for f in changed_files
        if not f.endswith("README.md")
        and not f.endswith(".log")
        and not f.endswith(".jsonl")
        and not f.endswith(".out.log")
        and len(Path(f).parts) <= 4  # max depth
    ]

    if not code_files:
        print("✅ Only README/log changes — validation skipped.")
        return True

    failures = []
    changed_folders = _files_to_folders(code_files)

    for folder in sorted(changed_folders):
        try:
            rel = folder.relative_to(WORKSPACE)
        except ValueError:
            continue

        if not (folder / "README.md").exists():
            failures.append(f"❌ {rel}: Missing README.md")
            continue

        if not _readme_up_to_date(folder):
            failures.append(f"❌ {rel}: README.md is older than folder contents")

        if strict and not _has_required_sections(folder):
            failures.append(f"❌ {rel}: README.md missing required sections (Purpose, Contents, Change Log)")

    if not _root_readme_newer_than_organs():
        failures.append("❌ Root README.md is stale (older than an organ README)")

    if failures:
        print("\n📛 README VALIDATION FAILED\n")
        for f in failures:
            print(f"  {f}")
        print("\n  Fix: run `readme-update-all && readme-root-build` then push again.\n")
        return False

    checked = len(changed_folders)
    print(f"✅ README validation passed ({checked} folder{'s' if checked != 1 else ''} checked)")
    return True


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Validate READMEs before push")
    parser.add_argument("--files", nargs="*", help="Specific changed files to validate against")
    parser.add_argument("--strict", action="store_true", help="Also check section structure")
    args = parser.parse_args()

    ok = validate_pre_push(args.files, strict=args.strict)
    sys.exit(0 if ok else 1)
