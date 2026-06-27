# workspace-brain MCP Server

A **local** MCP (Model Context Protocol) server that gives Claude and Codex structured access to this workspace's shared intelligence: memory, tasks, decisions, state, health, and autolab data.

## What it is

Think of it as a smart, safe interface over your workspace files. Instead of reading raw files, Claude and Codex can ask structured questions like:

- "What are my active tasks?" → `search_tasks`
- "What decisions have we made about X?" → `search_decisions`
- "What is the current workspace health?" → `get_workspace_health`
- "Add a memory note about Y" → `add_memory_note`

The file system (`agent-system/`, `autolab/`, etc.) remains the **source of truth**. This server is a structured access layer over those files, not a replacement.

## How it works

1. Claude or Codex starts the server automatically as a subprocess when needed (stdio mode).
2. The server reads from authoritative workspace files.
3. A local SQLite index enables fast keyword search across all workspace documents.
4. Mutating tools only touch pre-approved, safe files (see `docs/SAFETY_MODEL.md`).

## Quick reference

```sh
# Check status
~/SuneelWorkSpace/mcp/server/scripts/mcp-status

# Rebuild the search index (after big changes)
~/SuneelWorkSpace/mcp/server/scripts/mcp-reindex

# Health check
~/SuneelWorkSpace/mcp/server/scripts/mcp-doctor

# Run all tests
~/SuneelWorkSpace/mcp/server/scripts/mcp-test

# Auto-repair issues
~/SuneelWorkSpace/mcp/server/scripts/mcp-repair

# Print capability report
~/SuneelWorkSpace/mcp/server/scripts/mcp-report
```

## Key paths

| What | Where |
|------|-------|
| Server entrypoint | `mcp/server/main.py` |
| Config | `mcp/server/config/` |
| Search index | `mcp/server/storage/memory_index.db` |
| Logs | `mcp/server/logs/` |
| State | `mcp/server/state/` |
| Management scripts | `mcp/server/scripts/` |
| Documentation | `mcp/docs/` |

## Docs

- [HOW_IT_WORKS.md](docs/HOW_IT_WORKS.md) — architecture and lifecycle
- [TOOL_REFERENCE.md](docs/TOOL_REFERENCE.md) — all MCP tools
- [RESOURCE_REFERENCE.md](docs/RESOURCE_REFERENCE.md) — all MCP resources
- [SAFETY_MODEL.md](docs/SAFETY_MODEL.md) — mutation rules and boundaries
- [RECOVERY.md](docs/RECOVERY.md) — how to recover from problems
