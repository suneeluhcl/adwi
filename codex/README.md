# Codex Workspace

This directory is the central local home for Codex-related setup that belongs
with `SuneelWorkSpace`.

- `codex-env.zsh` exports workspace paths and bridges the existing `gh` login
  token into `GITHUB_PAT_TOKEN`, which the GitHub MCP plugin requires.
- `set-launch-env.zsh` publishes the same token into the macOS launch
  environment for GUI-launched Codex sessions.
- User-global Codex config still lives in `/Users/MAC/.codex`, but workspace
  bootstrap files and notes should live here when possible.
