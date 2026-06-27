#!/usr/bin/env python3
"""
Real-time README watcher — detects file changes and triggers README updates.
Uses watchdog when available; falls back to polling every 5s.
"""
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

WORKSPACE = Path(subprocess.check_output(
    ["git", "rev-parse", "--show-toplevel"], text=True,
    cwd=os.path.dirname(os.path.abspath(__file__))
).strip())

IGNORED_DIRS = {".git", "node_modules", ".venv", "__pycache__", "logs", "nerve_inbox", ".DS_Store"}
IGNORED_NAMES = {"README.md", ".DS_Store"}
IGNORED_EXTS = {".log", ".pyc", ".pyo", ".jsonl"}


def _get_organ(path: Path) -> str:
    try:
        rel = path.relative_to(WORKSPACE)
        return rel.parts[0] if rel.parts else "hands"
    except ValueError:
        return "hands"


def _should_ignore(path: Path) -> bool:
    if path.name in IGNORED_NAMES:
        return True
    if path.suffix in IGNORED_EXTS:
        return True
    for part in path.parts:
        if part in IGNORED_DIRS:
            return True
    return False


def _handle_change(changed_path: Path) -> None:
    if _should_ignore(changed_path):
        return

    ts = time.strftime("%H:%M:%S")
    try:
        rel = changed_path.relative_to(WORKSPACE)
    except ValueError:
        rel = changed_path

    print(f"[{ts}] 📝 Change: {rel}")

    # Use semantic impact engine to determine affected folders
    try:
        from hands.automation.readme.change_impact_engine import get_impacted_folders
        impacted = get_impacted_folders([str(rel)])
    except Exception as e:
        print(f"[{ts}]   ⚠️  Impact engine failed ({e}), using direct folder")
        folder = changed_path.parent if changed_path.is_file() else changed_path
        impacted = [folder] if folder.is_dir() else []

    if not impacted:
        return

    from hands.automation.readme.readme_generator import update_readme_for_folder
    from hands.automation.readme.root_synthesizer import synthesize_root

    updated_organs = set()
    for folder in impacted:
        organ = _get_organ(folder)
        try:
            update_readme_for_folder(str(folder), use_claude=False)
            print(f"[{ts}]   ✅ {folder.name}/README.md")
            updated_organs.add(organ)
        except Exception as e:
            print(f"[{ts}]   ❌ {folder.name}: {e}")

    # Rebuild root once after all impacted folders are updated
    try:
        synthesize_root()
        print(f"[{ts}]   ✅ Root README rebuilt")
    except Exception as e:
        print(f"[{ts}]   ⚠️  Root rebuild: {e}")

    # Notify nervous system per updated organ
    for organ in updated_organs:
        if organ and organ != "unknown":
            try:
                subprocess.run(
                    [sys.executable, str(WORKSPACE / "nervous/nerve_propagator.py"),
                     "notify", organ, "readme_updated"],
                    cwd=str(WORKSPACE),
                    capture_output=True,
                    timeout=5,
                )
            except Exception:
                pass

    # Trigger lab evolution for any newly low-health folders
    try:
        from hands.automation.readme.lab_bridge import trigger_evolution_for_low_health
        trigger_evolution_for_low_health(threshold=60, dry_run=False)
    except Exception:
        pass


def _watchdog_watch() -> None:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

    class ReadmeHandler(FileSystemEventHandler):
        def __init__(self):
            self._debounce: dict = {}

        def _debounced(self, path: str) -> bool:
            now = time.time()
            last = self._debounce.get(path, 0)
            if now - last < 2.0:
                return True
            self._debounce[path] = now
            return False

        def _dispatch_change(self, event_path: str) -> None:
            p = Path(event_path)
            if not self._debounced(event_path):
                _handle_change(p)

        def on_modified(self, event):
            if not event.is_directory:
                self._dispatch_change(event.src_path)

        def on_created(self, event):
            if not event.is_directory:
                self._dispatch_change(event.src_path)

        def on_moved(self, event):
            self._dispatch_change(event.dest_path)

    observer = Observer()
    handler = ReadmeHandler()
    observer.schedule(handler, str(WORKSPACE), recursive=True)
    observer.start()
    print(f"👁️  README Watcher active (watchdog) — watching {WORKSPACE}")
    print("    Press Ctrl-C to stop.\n")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        observer.stop()
        observer.join()
        print("\n👁️  Watcher stopped.")


def _poll_watch(interval: int = 5) -> None:
    print(f"👁️  README Watcher active (polling every {interval}s) — watching {WORKSPACE}")
    print("    Press Ctrl-C to stop.\n")

    def snapshot() -> dict:
        state = {}
        for dirpath, dirnames, filenames in os.walk(WORKSPACE):
            dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]
            for fname in filenames:
                if fname in IGNORED_NAMES or Path(fname).suffix in IGNORED_EXTS:
                    continue
                fp = Path(dirpath) / fname
                try:
                    state[str(fp)] = fp.stat().st_mtime
                except Exception:
                    pass
        return state

    state = snapshot()
    try:
        while True:
            time.sleep(interval)
            new_state = snapshot()
            changed = {
                p for p, mtime in new_state.items()
                if state.get(p, 0) != mtime
            }
            for path_str in changed:
                _handle_change(Path(path_str))
            state = new_state
    except KeyboardInterrupt:
        print("\n👁️  Watcher stopped.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Real-time README watcher")
    parser.add_argument("--poll", action="store_true", help="Force polling mode")
    parser.add_argument("--interval", type=int, default=5, help="Polling interval seconds")
    args = parser.parse_args()

    if args.poll:
        _poll_watch(interval=args.interval)
    else:
        try:
            from watchdog.observers import Observer
            _watchdog_watch()
        except ImportError:
            print("⚠️  watchdog not available — using polling fallback")
            _poll_watch(interval=args.interval)
