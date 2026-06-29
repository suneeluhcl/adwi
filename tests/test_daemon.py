"""
tests/test_daemon.py
Real-time file watcher: monitors 12 organ directories, runs organ-specific tests
on file change, invokes one repair-loop iteration on failure, streams events to
the dashboard via POST /api/tests/event.

Usage:
    python3 tests/test_daemon.py [--poll]   # --poll forces polling fallback
"""

import json
import os
import subprocess
import sys
import threading
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(os.path.expanduser("~/SuneelWorkSpace"))
DASHBOARD_URL = "http://localhost:7777"
_VENV_PY = str(WORKSPACE / ".venv/bin/python3")
PYTHON = _VENV_PY if os.path.exists(_VENV_PY) else sys.executable
EVENTS_LOG = WORKSPACE / "blood/logs/test_daemon_events.jsonl"
DEBOUNCE = 0.5  # seconds — coalesce rapid saves

# Organ → test file mapping
ORGAN_TEST_MAP: dict[str, str | None] = {
    "brain":    "tests/organs/brain/test_brain.py",
    "heart":    "tests/organs/heart/test_heart.py",
    "eyes":     "tests/organs/eyes/test_eyes.py",
    "ears":     "tests/organs/ears/test_ears.py",
    "mouth":    "tests/organs/mouth/test_mouth.py",
    "hands":    "tests/organs/hands/test_hands.py",
    "blood":    "tests/organs/blood/test_blood.py",
    "dna":      "tests/organs/dna/test_dna.py",
    "spine":    "tests/organs/spine/test_spine.py",
    "nervous":  "tests/nerve_system/test_nervous.py",
    "lab":      "tests/ollama_engines/test_ollama_engines.py",
    "skeleton": None,  # rules only — no runnable test file
}

_IGNORED = (".git", "__pycache__", ".venv", "nerve_inbox", os.sep + "logs" + os.sep)


def _organ_from_path(path: str) -> str | None:
    for organ in ORGAN_TEST_MAP:
        prefix = str(WORKSPACE / organ) + os.sep
        if path.startswith(prefix):
            return organ
    return None


def _push_event(event: dict) -> None:
    """Write event to JSONL log + push to dashboard WebSocket relay."""
    EVENTS_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(EVENTS_LOG, "a") as f:
        f.write(json.dumps(event) + "\n")
    try:
        payload = json.dumps(event).encode()
        req = urllib.request.Request(
            f"{DASHBOARD_URL}/api/tests/event",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=2)
    except Exception:
        pass  # Dashboard not running — event still in log


def _run_organ_tests(organ: str) -> dict:
    test_file = ORGAN_TEST_MAP.get(organ)
    if not test_file:
        return {"organ": organ, "skipped": True, "reason": "no test file"}
    abs_path = str(WORKSPACE / test_file)
    if not os.path.exists(abs_path):
        return {"organ": organ, "skipped": True, "reason": f"missing: {test_file}"}
    proc = subprocess.run(
        [PYTHON, "-m", "pytest", abs_path, "-q", "--tb=short", "--no-header"],
        cwd=str(WORKSPACE),
        capture_output=True,
        text=True,
        timeout=60,
    )
    return {
        "organ": organ,
        "passed": proc.returncode == 0,
        "returncode": proc.returncode,
        "output": (proc.stdout + proc.stderr)[-800:],
        "test_file": test_file,
    }


def _run_one_repair_iteration(organ: str) -> dict:
    """Single iteration of the autonomous repair loop targeting one organ."""
    repair_script = str(WORKSPACE / "tests/autonomous_repair_loop.py")
    proc = subprocess.run(
        [PYTHON, repair_script, "--max-iterations", "1"],
        cwd=str(WORKSPACE),
        capture_output=True,
        text=True,
        timeout=120,
    )
    return {"organ": organ, "repair_exit": proc.returncode, "output": proc.stdout[-400:]}


class _ChangeHandler:
    """Debounced organ-file change handler."""

    def __init__(self) -> None:
        self._pending: dict[str, float] = {}
        self._lock = threading.Lock()
        self._timer: threading.Timer | None = None

    def on_change(self, path: str) -> None:
        if any(x in path for x in _IGNORED):
            return
        organ = _organ_from_path(path)
        if not organ:
            return
        with self._lock:
            self._pending[organ] = time.monotonic()
        if self._timer:
            self._timer.cancel()
        self._timer = threading.Timer(DEBOUNCE, self._flush)
        self._timer.daemon = True
        self._timer.start()

    def _flush(self) -> None:
        with self._lock:
            organs = list(self._pending)
            self._pending.clear()
        for organ in organs:
            threading.Thread(target=self._process, args=(organ,), daemon=True).start()

    def _process(self, organ: str) -> None:
        ts = datetime.now(timezone.utc).isoformat()
        _push_event({"ts": ts, "type": "test_start", "organ": organ})

        result = _run_organ_tests(organ)
        _push_event({"ts": ts, "type": "test_result", **result})

        if not result.get("passed") and not result.get("skipped"):
            _push_event({"ts": ts, "type": "repair_start", "organ": organ})
            repair = _run_one_repair_iteration(organ)
            _push_event({"ts": ts, "type": "repair_done", **repair})
            recheck = _run_organ_tests(organ)
            _push_event({"ts": ts, "type": "test_result", "after_repair": True, **recheck})


def _watch_watchdog(handler: _ChangeHandler) -> None:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

    class _WD(FileSystemEventHandler):
        def on_modified(self, e):
            if not e.is_directory:
                handler.on_change(e.src_path)
        def on_created(self, e):
            if not e.is_directory:
                handler.on_change(e.src_path)

    observer = Observer()
    watched = 0
    for organ in ORGAN_TEST_MAP:
        p = str(WORKSPACE / organ)
        if os.path.isdir(p):
            observer.schedule(_WD(), p, recursive=True)
            watched += 1
    observer.start()
    print(f"[test-daemon] watchdog active — watching {watched} organ directories")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        observer.stop()
        observer.join()


def _watch_polling(handler: _ChangeHandler, interval: float = 2.0) -> None:
    mtimes: dict[str, float] = {}

    def scan() -> None:
        for organ in ORGAN_TEST_MAP:
            organ_path = WORKSPACE / organ
            if not organ_path.is_dir():
                continue
            for f in organ_path.rglob("*.py"):
                key = str(f)
                try:
                    mt = f.stat().st_mtime
                except OSError:
                    continue
                if key in mtimes and mtimes[key] != mt:
                    handler.on_change(key)
                mtimes[key] = mt

    print(f"[test-daemon] polling fallback active — scanning every {interval}s")
    try:
        while True:
            try:
                scan()
            except Exception as e:
                print(f"[test-daemon] poll error: {e}", file=sys.stderr)
            time.sleep(interval)
    except KeyboardInterrupt:
        pass


def main() -> None:
    force_poll = "--poll" in sys.argv
    handler = _ChangeHandler()
    ts = datetime.now(timezone.utc).isoformat()
    print(f"[test-daemon] starting — workspace: {WORKSPACE}")
    _push_event({"ts": ts, "type": "daemon_start", "pid": os.getpid()})

    if not force_poll:
        try:
            import watchdog  # noqa: F401
            _watch_watchdog(handler)
            return
        except ImportError:
            print("[test-daemon] watchdog not installed — using polling fallback")
            print("  Install with: pip install watchdog")
    _watch_polling(handler)


if __name__ == "__main__":
    main()
