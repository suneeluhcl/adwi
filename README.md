# Suneel's Local AI Operating System — Adwi

> Automated backup of my local AI workspace. No secrets, credentials, or runtime data included.

## What's in here

- `adwi/` — Adwi CLI brain (adwi_cli.py, repair.py, backup.py, etc.)
- `bin/` — local helper scripts
- `mcp-servers/` — MCP server implementations (sandbox, comfyui bridge)
- `notes/` — AI learning journal, capability roadmap, mistake log, system inspections
- `local-ai-stack/docker-compose.yml` — Docker services config

## Stack

- **adwi** — local AI operating assistant (M4 Max Mac, 64GB RAM)
- **adwi:latest** — Qwen3 MoE 30.5B local reasoning model (131K context)
- **Open WebUI** — browser UI + Gemini cloud routing
- **Ollama** — local model runtime
- **n8n** — automation engine
- **SearXNG** — local web search
- **Qdrant** — vector memory database
- **10 MCP servers** — Playwright, GitHub, SQLite, Memory, Sequential Thinking, Qdrant, ComfyUI, Adwi sandbox, Fetch, Filesystem

## Setup

See `notes/ADWI-START-HERE.md` for local setup instructions.

## Security

Secrets, API keys, credentials, tokens, Docker runtime databases, and model files are excluded via `.gitignore`.

---
*Auto-backed up by `adwi /backup-now`*
