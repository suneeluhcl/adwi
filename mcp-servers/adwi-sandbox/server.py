"""
Adwi Sandbox MCP Server
Exposes workspace tools to any MCP-compatible client (Claude Code, n8n, etc.)
Safe read/execute operations only — no destructive or financial actions.
"""
import json
import os
import subprocess
import urllib.request
import urllib.error
from pathlib import Path

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    raise SystemExit("Run with: uv run --with mcp python3 server.py")

WORKSPACE = Path.home() / "SuneelWorkSpace"
SAFE_API  = "http://127.0.0.1:5055"

mcp = FastMCP("adwi-sandbox")


def _safe_api(route: str, body: dict | None = None) -> str:
    url = f"{SAFE_API}{route}"
    try:
        if body:
            data = json.dumps(body).encode()
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        else:
            req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=35) as r:
            return r.read().decode()
    except urllib.error.URLError:
        return "Safe Command API is not running. Start it with: cd ~/SuneelWorkSpace && python3 local-command-api/server.py"


@mcp.tool()
def run_python(code: str) -> str:
    """Execute Python code in Adwi's safe sandbox (30s timeout, no network)."""
    result = _safe_api("/run-python", {"code": code})
    return result or "No output"


@mcp.tool()
def run_bash(command: str) -> str:
    """Execute an allowed bash command via Adwi's safe command allowlist."""
    result = _safe_api("/run-bash", {"command": command})
    return result or "No output"


@mcp.tool()
def search_notes(query: str, max_results: int = 5) -> str:
    """Semantic search over Adwi's notes and documents using RAG."""
    script = f"""
import sys
sys.path.insert(0, '{WORKSPACE}/adwi')
try:
    from adwi_cli import cmd_rag
    cmd_rag('{query.replace("'", "")}', top_k={max_results})
except Exception as e:
    print(f'RAG error: {{e}}')
"""
    try:
        r = subprocess.run(
            ["python3", "-c", script],
            capture_output=True, text=True, timeout=20, cwd=str(WORKSPACE)
        )
        return (r.stdout or r.stderr or "No results").strip()
    except subprocess.TimeoutExpired:
        return "RAG search timed out"


@mcp.tool()
def git_status(repo_name: str = "") -> str:
    """Get git status for a workspace repository. Leave blank to list all repos."""
    if repo_name:
        repo = WORKSPACE / repo_name
        if not (repo / ".git").exists():
            return f"No git repo found at {repo}"
        r = subprocess.run(["git", "-C", str(repo), "status", "--short"], capture_output=True, text=True, timeout=10)
        log = subprocess.run(["git", "-C", str(repo), "log", "--oneline", "-5"], capture_output=True, text=True, timeout=10)
        return f"=== {repo_name} ===\n{r.stdout}\nRecent commits:\n{log.stdout}"
    else:
        repos = [d.name for d in sorted(WORKSPACE.iterdir()) if d.is_dir() and (d / ".git").exists()]
        return "Git repos in workspace:\n" + "\n".join(f"  • {r}" for r in repos) if repos else "No git repos found"


@mcp.tool()
def read_file(path: str) -> str:
    """Read a file from the workspace (workspace-relative or absolute under /Users/MAC)."""
    p = Path(path)
    if not p.is_absolute():
        p = WORKSPACE / path
    # Safety: block secrets and SSH keys
    blocked = [".ssh", "secrets/", ".env", "token.json", ".pem", ".key"]
    if any(b in str(p) for b in blocked):
        return "Access denied: this path contains sensitive files"
    if not p.exists():
        return f"File not found: {p}"
    if p.stat().st_size > 500_000:
        return f"File too large ({p.stat().st_size // 1024}KB). Read specific lines instead."
    return p.read_text(errors="replace")


@mcp.tool()
def list_files(directory: str = "", pattern: str = "*") -> str:
    """List files in a workspace directory."""
    p = Path(directory) if directory else WORKSPACE
    if not p.is_absolute():
        p = WORKSPACE / directory
    if not p.exists():
        return f"Directory not found: {p}"
    items = sorted(p.glob(pattern))[:100]
    return "\n".join(str(i.relative_to(WORKSPACE) if WORKSPACE in i.parents else i) for i in items)


@mcp.tool()
def adwi_status() -> str:
    """Check which Adwi services are running (Ollama, Open WebUI, n8n, SearXNG, Qdrant)."""
    services = {
        "Ollama":     "http://localhost:11434",
        "Open WebUI": "http://localhost:3000",
        "n8n":        "http://localhost:5678",
        "SearXNG":    "http://localhost:8888",
        "Qdrant":     "http://localhost:6333",
        "Safe API":   "http://localhost:5055",
    }
    lines = []
    for name, url in services.items():
        try:
            urllib.request.urlopen(url, timeout=2)
            lines.append(f"  ✓ {name} — {url}")
        except Exception:
            lines.append(f"  ✗ {name} — offline")
    return "\n".join(lines)


@mcp.tool()
def note_append(title: str, content: str) -> str:
    """Append a note to Adwi's notes folder."""
    notes = WORKSPACE / "notes"
    notes.mkdir(exist_ok=True)
    safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in title)[:60]
    path = notes / f"{safe_title}.md"
    with path.open("a") as f:
        f.write(f"\n{content}\n")
    return f"Note saved to {path.name}"


if __name__ == "__main__":
    mcp.run()
