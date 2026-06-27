#!/usr/bin/env python3
"""Bulk README updater — generates READMEs for every non-trivial workspace folder."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from hands.automation.readme.intelligence_engine import analyze_workspace, WORKSPACE
from hands.automation.readme.readme_generator import update_readme_for_folder


def run_all(use_claude: bool = True, quiet: bool = False) -> bool:
    analyses = analyze_workspace()
    ok_count = 0
    fail_count = 0

    for analysis in analyses:
        folder = str(WORKSPACE / analysis["path"])
        try:
            update_readme_for_folder(folder, use_claude=use_claude)
            ok_count += 1
            if not quiet:
                print(f"  ✅ {analysis['path']}")
        except Exception as e:
            fail_count += 1
            if not quiet:
                print(f"  ❌ {analysis['path']}: {e}")

    print(f"\n{'✅' if fail_count == 0 else '⚠️'} {ok_count} updated, {fail_count} failed")
    return fail_count == 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update all workspace READMEs")
    parser.add_argument("--no-claude", action="store_true", help="Skip Claude CLI, use rule-based only")
    parser.add_argument("--quiet", action="store_true", help="Only show summary")
    args = parser.parse_args()

    ok = run_all(use_claude=not args.no_claude, quiet=args.quiet)
    sys.exit(0 if ok else 1)
