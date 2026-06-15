"""
Adwi Nightly Improvement Loop
Runs at 2:00 AM via LaunchAgent com.suneel.adwi-nightly.
Steps: services → log review → AI skill discovery → evals → capability sync → git commit → report
"""

import json, os, re, subprocess, sys, time, urllib.request
from datetime import datetime
from pathlib import Path

HOME      = Path.home()
WORKSPACE = HOME / "SuneelWorkSpace"
ADWI_DIR  = WORKSPACE / "adwi"
NOTES     = WORKSPACE / "notes"
NIGHTLY_LOG_DIR   = NOTES / "nightly-improvement-logs"
CLI_PY            = ADWI_DIR / "adwi_cli.py"
JOURNAL           = NOTES / "adwi-learning-journal.md"
MISTAKES          = NOTES / "adwi-mistakes-and-fixes.md"
CAPABILITIES      = ADWI_DIR / "capabilities.json"
PENDING_FILE      = NOTES / "adwi-pending-improvements.md"

NOW      = datetime.now()
DATE_STR = NOW.strftime("%Y-%m-%d")
TIME_STR = NOW.strftime("%H:%M")
LOG_PATH = NIGHTLY_LOG_DIR / f"nightly-{DATE_STR}.md"

_ANSI = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')


def _strip(text: str) -> str:
    return _ANSI.sub("", text)


def _pr(msg: str):
    print(msg, flush=True)


# ── Ollama ────────────────────────────────────────────────────────────────────

def _ollama_ok() -> bool:
    try:
        urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=5)
        return True
    except Exception:
        return False


def _ollama_ask(prompt: str, model: str = "adwi:latest", timeout: int = 180) -> str:
    payload = json.dumps({
        "model": model, "prompt": prompt, "stream": False,
        "options": {"temperature": 0.7, "num_predict": 1500}
    }).encode()
    try:
        req = urllib.request.Request(
            "http://127.0.0.1:11434/api/generate", data=payload, method="POST",
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())["response"].strip()
    except Exception as e:
        return f"[Ollama error: {e}]"


# ── Subprocess helpers ─────────────────────────────────────────────────────────

def _run(cmd: list, timeout: int = 60, cwd: Path = WORKSPACE) -> tuple[int, str, str]:
    env = {**os.environ,
           "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
           "HOME": str(HOME)}
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                       cwd=str(cwd), env=env)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def _run_adwi_cmd(command: str, timeout: int = 300) -> str:
    """Pipe a /command into adwi_cli.py and return stripped output."""
    env = {**os.environ,
           "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
           "HOME": str(HOME)}
    r = subprocess.run(
        ["python3", str(CLI_PY)],
        input=f"{command}\n/exit\n",
        capture_output=True, text=True, timeout=timeout,
        cwd=str(WORKSPACE), env=env
    )
    return _strip(r.stdout + r.stderr)


# ── Step 1: Services ──────────────────────────────────────────────────────────

def step_services() -> dict:
    status: dict = {}

    # Ollama
    if _ollama_ok():
        status["ollama"] = "running"
    else:
        _run(["/opt/homebrew/bin/brew", "services", "start", "ollama"], timeout=30)
        time.sleep(8)
        status["ollama"] = "started" if _ollama_ok() else "failed — manual start needed"

    # Docker
    _, out, _ = _run(["/opt/homebrew/bin/docker", "ps", "--format", "{{.Names}}"], timeout=10)
    running = set(out.splitlines())
    expected = {"suneel-open-webui", "suneel-n8n", "suneel-searxng", "suneel-qdrant"}
    missing = expected - running

    if missing:
        compose = WORKSPACE / "local-ai-stack/docker-compose.yml"
        if compose.exists():
            _run(["/opt/homebrew/bin/docker", "compose", "-f", str(compose), "up", "-d"],
                 timeout=90)
            time.sleep(6)

    _, out2, _ = _run(["/opt/homebrew/bin/docker", "ps", "--format", "{{.Names}}"], timeout=10)
    running2 = set(out2.splitlines())
    status["docker_up"]      = sorted(running2 & expected)
    status["docker_missing"] = sorted(expected - running2)
    return status


# ── Step 2: Log review ────────────────────────────────────────────────────────

def step_review_logs() -> dict:
    summary: dict = {}

    repair_dir = NOTES / "adwi-repair-logs"
    repairs = []
    if repair_dir.exists():
        for f in sorted(repair_dir.glob("*.md"))[-7:]:
            text = f.read_text(encoding="utf-8", errors="ignore")
            repairs.append({"file": f.name, "snippet": text[:400]})
    summary["repair_count"]   = len(repairs)
    summary["repair_snippets"] = repairs

    summary["journal_tail"] = (
        JOURNAL.read_text(encoding="utf-8", errors="ignore")[-2000:]
        if JOURNAL.exists() else ""
    )
    summary["mistakes_tail"] = (
        MISTAKES.read_text(encoding="utf-8", errors="ignore")[-1000:]
        if MISTAKES.exists() else ""
    )
    return summary


# ── Step 3: AI skill discovery ────────────────────────────────────────────────

def step_skill_discovery(logs: dict) -> str:
    caps = []
    if CAPABILITIES.exists():
        try:
            caps = json.loads(CAPABILITIES.read_text(encoding="utf-8"))
        except Exception:
            pass
    cap_names = [c.get("name", "") for c in caps] if isinstance(caps, list) else []

    prompt = f"""You are Adwi's nightly self-improvement engine. Today is {DATE_STR}.

Current state:
- {len(cap_names)} capabilities: {', '.join(cap_names[:30])}
- Hardware: Apple M4 Max 64GB — ONLY suggest models in 8B–35B range. NEVER 70B+.
- Stack: Ollama, Open WebUI, n8n, SearXNG, Qdrant, 10 MCP servers
- Local models: adwi:latest (18GB Qwen3 MoE 30B), llama3.1:8b, qwen3:0.6b, minicpm-v, nomic-embed-text

Recent journal:
{logs.get('journal_tail', '')[-1200:]}

Recent mistakes/fixes:
{logs.get('mistakes_tail', '')[-600:]}

Suggest exactly 5 concrete improvements to make Suneel's daily workflow better.
For each, output one JSON object per line (no extra text, no markdown):
{{"name":"slug","type":"command|model|mcp|workflow|fix","title":"Title","description":"One sentence user benefit","priority":"high|medium|low","effort":"minutes|hours|days","implementation_hint":"One paragraph technical note"}}

Focus on:
1. New /commands filling gaps in current capabilities
2. Ollama models in 8B–35B range (coding, reasoning, vision)
3. New MCP servers (filesystem extensions, calendar, browser, database)
4. n8n workflow automations saving Suneel time
5. Routing improvements or error recovery patterns

Output only the 5 JSON lines, nothing else."""

    return _ollama_ask(prompt, timeout=120)


def _save_pending(suggestions: str):
    header = "# Adwi Pending Improvements\n"
    existing = PENDING_FILE.read_text(encoding="utf-8") if PENDING_FILE.exists() else header
    entry = f"\n## {DATE_STR} {TIME_STR}\n```json\n{suggestions}\n```\n"
    PENDING_FILE.write_text(existing + entry, encoding="utf-8")


# ── Step 4: Evals ─────────────────────────────────────────────────────────────

def step_evals() -> dict:
    results: dict = {}

    # Syntax check
    rc, _, err = _run(["python3", "-m", "py_compile", str(CLI_PY)], timeout=30)
    results["syntax_ok"]    = rc == 0
    results["syntax_error"] = err if rc != 0 else ""

    # Routing eval (piped)
    try:
        out = _run_adwi_cmd("/eval-routing", timeout=180)
        results["routing_eval"] = out[-2000:]
    except Exception as e:
        results["routing_eval"] = f"Error: {e}"

    return results


# ── Step 5: Capability sync ───────────────────────────────────────────────────

def step_capability_sync() -> dict:
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("repair", str(ADWI_DIR / "repair.py"))
        mod  = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        cmds    = mod.scan_implemented_commands(CLI_PY)
        updated = mod.update_capabilities_json(CLI_PY, cmds)
        return {"commands_found": len(cmds), "capabilities_updated": updated}
    except Exception as e:
        return {"error": str(e)}


# ── Step 6: Git commit ────────────────────────────────────────────────────────

def step_git_commit() -> dict:
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("backup", str(ADWI_DIR / "backup.py"))
        mod  = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.do_backup(f"Nightly improvement — {DATE_STR} {TIME_STR}")
    except Exception as e:
        return {"success": False, "message": str(e)}


# ── Step 7: Write report ──────────────────────────────────────────────────────

def step_write_report(data: dict) -> Path:
    NIGHTLY_LOG_DIR.mkdir(parents=True, exist_ok=True)

    svc = data.get("services", {})
    lr  = data.get("log_review", {})
    ev  = data.get("evals", {})
    cs  = data.get("cap_sync", {})
    gc  = data.get("git_commit", {})
    sk  = data.get("skill_suggestions", "[none]")

    lines = [
        f"# Adwi Nightly Improvement — {DATE_STR} {TIME_STR}",
        "",
        "## 1. Services",
        f"- Ollama: {svc.get('ollama', 'unknown')}",
        f"- Docker up: {', '.join(svc.get('docker_up', []))}",
    ]
    if svc.get("docker_missing"):
        lines.append(f"- Docker missing: {', '.join(svc['docker_missing'])}")

    lines += [
        "",
        "## 2. Log Review",
        f"- Repair logs reviewed: {lr.get('repair_count', 0)}",
    ]

    lines += [
        "",
        "## 3. AI Skill Discovery",
        "```json",
        sk,
        "```",
    ]

    lines += [
        "",
        "## 4. Evals",
        f"- Syntax: {'✓ OK' if ev.get('syntax_ok') else '✗ ' + ev.get('syntax_error', '')}",
        "- Routing eval output:",
        "```",
        ev.get("routing_eval", "")[-1500:],
        "```",
    ]

    lines += ["", "## 5. Capability Sync"]
    if "error" in cs:
        lines.append(f"- ✗ {cs['error']}")
    else:
        lines.append(f"- Commands found: {cs.get('commands_found', 0)}")
        lines.append(f"- Capabilities updated: {cs.get('capabilities_updated', 0)}")

    lines += ["", "## 6. Git Commit"]
    if gc.get("success"):
        lines.append(f"- ✓ {gc.get('commit_hash', '')} pushed: {gc.get('pushed', False)}")
    else:
        lines.append(f"- ⚠ {gc.get('message', 'no changes or error')}")

    LOG_PATH.write_text("\n".join(lines), encoding="utf-8")
    return LOG_PATH


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    NIGHTLY_LOG_DIR.mkdir(parents=True, exist_ok=True)
    _pr(f"\n{'='*60}")
    _pr(f"  ADWI NIGHTLY IMPROVEMENT — {DATE_STR} {TIME_STR}")
    _pr(f"{'='*60}\n")

    data: dict = {}

    _pr("[1/6] Services health check...")
    data["services"] = step_services()
    svc = data["services"]
    _pr(f"  ollama={svc.get('ollama')}  docker_up={svc.get('docker_up')}")

    _pr("[2/6] Reviewing logs...")
    data["log_review"] = step_review_logs()
    _pr(f"  {data['log_review'].get('repair_count', 0)} repair logs reviewed")

    _pr("[3/6] AI skill discovery...")
    if _ollama_ok():
        data["skill_suggestions"] = step_skill_discovery(data["log_review"])
        _save_pending(data["skill_suggestions"])
        _pr("  Suggestions saved → notes/adwi-pending-improvements.md")
    else:
        data["skill_suggestions"] = "[Ollama offline — skipped]"
        _pr("  ⚠ Ollama offline, skipping")

    _pr("[4/6] Running evals...")
    data["evals"] = step_evals()
    ev = data["evals"]
    _pr(f"  Syntax: {'OK' if ev.get('syntax_ok') else 'FAIL: ' + ev.get('syntax_error','')}")

    _pr("[5/6] Capability sync...")
    data["cap_sync"] = step_capability_sync()
    cs = data["cap_sync"]
    if "error" not in cs:
        _pr(f"  {cs.get('commands_found',0)} commands, {cs.get('capabilities_updated',0)} updated")
    else:
        _pr(f"  ⚠ {cs['error']}")

    _pr("[6/6] Git commit + push...")
    data["git_commit"] = step_git_commit()
    gc = data["git_commit"]
    if gc.get("success"):
        pushed = "→ pushed" if gc.get("pushed") else "→ local only"
        _pr(f"  ✓ {gc.get('commit_hash','')} {pushed}")
    else:
        _pr(f"  ⚠ {gc.get('message','no changes')}")

    report = step_write_report(data)
    _pr(f"\n✓ Report saved: {report}")
    _pr(f"{'='*60}\n")


if __name__ == "__main__":
    main()
