# Backup Manifest

This file lists what is included and excluded from this GitHub backup.

## INCLUDED (committed to GitHub)
- adwi/ — all Python source and config files
- bin/ — helper scripts (no secrets)
- mcp-servers/adwi-sandbox/server.py
- mcp-servers/comfyui-bridge/server.py
- notes/ADWI-START-HERE.md, START-HERE-SUNEEL-LOCAL-AI.md, AI-NOTES-INDEX.md
- notes/adwi-learning-journal.md
- notes/adwi-mistakes-and-fixes.md
- notes/adwi-capability-roadmap.md
- notes/adwi-repair-logs/*.md (reports only, not backups/)
- notes/system-inspections/
- local-ai-stack/docker-compose.yml
- .gitignore, README.md, BACKUP_MANIFEST.md

## EXCLUDED (never committed)
- secrets/ — API keys, tokens, credentials
- **/.env, **/secrets.local.env — env files with secrets
- **/*token*, **/*secret*, **/*key* — credential files
- **/*.pem, *.p12, *.pfx, id_rsa — key files
- local-ai-stack/open-webui-data/ — runtime database (may contain secrets)
- local-ai-stack/n8n-data/ — n8n runtime database
- local-ai-stack/searxng-data/ — searxng runtime data
- mcp-servers/qdrant-data/ — Qdrant vector DB data
- notes/adwi-action-logs/ — high-volume action logs
- notes/adwi-repair-logs/backups/ — large file backups
- notes/clipboard-command-logs/ — clipboard history
- *.gguf, *.safetensors, *.bin — large model files
- __pycache__/, node_modules/, .venv/ — generated artifacts
