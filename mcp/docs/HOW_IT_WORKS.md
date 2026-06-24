# How workspace-brain Works

## Architecture

```
Claude / Codex
     │
     │ starts subprocess (stdio)
     ▼
workspace-brain MCP server (main.py)
     │
     ├── Resources: read workspace files directly
     ├── Tools: read/write/exec with policy enforcement
     ├── Prompts: pre-built context assemblies
     │
     ├── SQLite FTS index (memory_index.db)
     │        └── rebuilt from authoritative files by mcp-reindex
     │
     └── Authoritative files (source of truth)
              ├── agent-system/memory/MEMORY.md
              ├── agent-system/memory/DECISIONS.md
              ├── agent-system/tasks/ACTIVE_TASKS.md
              ├── agent-system/state/CURRENT_STATE.json
              ├── agent-system/state/WORKSPACE_HEALTH.json
              ├── autolab/meta/insights.md
              └── ... (see resource_map.json)
```

## Lifecycle

1. **Client requests a tool or resource** — Claude or Codex starts `main.py` as a subprocess.
2. **Server starts** — loads config, checks if index is empty (builds it if needed), marks state.
3. **Request served** — resource reads file directly; tool may read index or file; mutating tool appends/updates within policy.
4. **Client done** — client kills the subprocess. Server logs the session.
5. **Maintenance** — `agent-maintain` calls `mcp-reindex` and `mcp-doctor` periodically.

## Index lifecycle

- **Source of truth**: markdown and JSON files in `agent-system/` and `autolab/`.
- **Index**: SQLite FTS5 table in `mcp/server/storage/memory_index.db`.
- **Reindex**: `mcp-reindex` deletes all index entries, re-parses source files, rebuilds.
- **Auto-reindex**: On server startup, if index is empty. On maintenance via `agent-maintain`.
- **Index is disposable**: delete `memory_index.db` and run `mcp-reindex` to recover cleanly.

## Server startup flow (main.py)

1. Load `server_config.json`
2. Ensure log/state/storage directories exist
3. Initialize SQLite schema (idempotent)
4. Check if index is empty → auto-reindex if empty
5. Update `mcp_state.json` with startup timestamp
6. Start FastMCP stdio loop

## Key files

| File | Purpose |
|------|---------|
| `server/main.py` | MCP server (resources, tools, prompts) |
| `server/config/server_config.json` | Paths, limits, flags |
| `server/config/tool_policies.json` | Which files each tool can touch |
| `server/config/resource_map.json` | URI → file mapping for resources |
| `server/storage/memory_index.db` | SQLite FTS index (disposable) |
| `server/state/mcp_state.json` | Server runtime state |
| `server/state/last_index.json` | Index build metadata |
| `server/state/capability_report.json` | What tools/resources are available |
| `server/logs/mcp_server.log` | Server log |
| `server/logs/mcp_access.log` | Per-tool access log (JSONL) |
