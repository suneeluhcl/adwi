#!/usr/bin/env python3
"""
Consistency Engine — compares README content against actual folder state.
Detects drift (stale files, missing sections, outdated references) and auto-fixes.
"""
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

WORKSPACE = Path(subprocess.check_output(
    ["git", "rev-parse", "--show-toplevel"], text=True,
    cwd=os.path.dirname(os.path.abspath(__file__))
).strip())

REQUIRED_SECTIONS = [
    "Purpose",
    "Responsibilities",
    "System Role",
    "Contents",
    "Dependencies",
    "Capabilities",
    "Gaps",
    "Change Log",
]

IGNORED_DIRS = {".git", "node_modules", ".venv", "__pycache__", "logs", "nerve_inbox"}


def _missing_sections(readme_content: str) -> list:
    missing = []
    for section in REQUIRED_SECTIONS:
        if section.lower() not in readme_content.lower():
            missing.append(section)
    return missing


def _find_stale_file_refs(readme_content: str, folder_path: Path) -> list:
    """Find filenames referenced in Contents section that no longer exist."""
    contents_match = re.search(
        r"## 📂 Contents(.*?)(?=\n## |\Z)",
        readme_content,
        re.DOTALL,
    )
    if not contents_match:
        return []

    section = contents_match.group(1)
    stale = []
    for m in re.finditer(r"`([^`/]+\.[a-zA-Z0-9]+)`", section):
        fname = m.group(1)
        if not (folder_path / fname).exists():
            stale.append(fname)
    return stale


def _readme_is_stale(readme_path: Path, folder_path: Path) -> bool:
    """Return True if any file in the folder is newer than README.md."""
    if not readme_path.exists():
        return True
    readme_mtime = readme_path.stat().st_mtime
    try:
        for item in folder_path.iterdir():
            if item.name in {"README.md", ".DS_Store"} or item.name.startswith("."):
                continue
            try:
                if item.stat().st_mtime > readme_mtime:
                    return True
            except Exception:
                pass
    except PermissionError:
        pass
    return False


def check_consistency(folder_path: str) -> dict:
    path = Path(folder_path).resolve()
    readme_path = path / "README.md"
    issues = []

    if not readme_path.exists():
        issues.append("README.md missing")
        return {
            "ok": False,
            "issues": issues,
            "fixed": False,
            "path": str(path.relative_to(WORKSPACE) if path.is_relative_to(WORKSPACE) else path),
        }

    try:
        content = readme_path.read_text(errors="ignore")
    except Exception as e:
        return {"ok": False, "issues": [f"Cannot read README: {e}"], "fixed": False, "path": str(path)}

    missing = _missing_sections(content)
    if missing:
        issues.append(f"Missing sections: {missing}")

    stale_refs = _find_stale_file_refs(content, path)
    if stale_refs:
        issues.append(f"Stale file references: {stale_refs}")

    if _readme_is_stale(readme_path, path):
        issues.append("README older than folder contents")

    try:
        rel = str(path.relative_to(WORKSPACE))
    except ValueError:
        rel = str(path)

    return {"ok": len(issues) == 0, "issues": issues, "fixed": False, "path": rel}


def fix_consistency(folder_path: str, use_claude: bool = False) -> dict:
    result = check_consistency(folder_path)
    if result["ok"]:
        return result

    try:
        from hands.automation.readme.readme_generator import update_readme_for_folder
        update_readme_for_folder(folder_path, use_claude=use_claude)

        # Notify nervous system
        try:
            path = Path(folder_path).resolve()
            rel_parts = path.relative_to(WORKSPACE).parts
            organ = rel_parts[0] if rel_parts else "hands"
            subprocess.run(
                [sys.executable, str(WORKSPACE / "nervous/nerve_propagator.py"),
                 "notify", organ, "readme_updated"],
                cwd=str(WORKSPACE),
                capture_output=True,
                timeout=5,
            )
        except Exception:
            pass

        result["fixed"] = True
        result["ok"] = True
    except Exception as e:
        result["fix_error"] = str(e)

    return result


def check_all_consistency(workspace_root: str = None, auto_fix: bool = False) -> list:
    root = Path(workspace_root) if workspace_root else WORKSPACE
    results = []

    for dirpath, dirnames, _ in os.walk(root):
        dirnames[:] = [d for d in sorted(dirnames) if d not in IGNORED_DIRS]
        path = Path(dirpath)
        try:
            rel = path.relative_to(root)
        except ValueError:
            continue
        if rel == Path(".") or len(rel.parts) > 3:
            continue

        if auto_fix:
            result = fix_consistency(str(path))
        else:
            result = check_consistency(str(path))
        results.append(result)

    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Check README consistency")
    parser.add_argument("folder", nargs="?", help="Folder to check (default: all)")
    parser.add_argument("--fix", action="store_true", help="Auto-fix issues")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    if args.folder:
        fn = fix_consistency if args.fix else check_consistency
        result = fn(args.folder)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            status = "✅ OK" if result["ok"] else f"❌ {result['issues']}"
            print(f"{result['path']}: {status}")
        sys.exit(0 if result["ok"] else 1)
    else:
        results = check_all_consistency(auto_fix=args.fix)
        ok_count = sum(1 for r in results if r["ok"])
        bad = [r for r in results if not r["ok"]]
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(f"✅ {ok_count} OK  ❌ {len(bad)} need attention")
            for r in bad:
                print(f"  {r['path']}: {r['issues']}")
        sys.exit(0 if not bad else 1)
