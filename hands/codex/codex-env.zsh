# Shared Codex environment for SuneelWorkSpace.

export SUNEEL_WORKSPACE="/Users/MAC/SuneelWorkSpace"
export CODEX_WORKSPACE="$SUNEEL_WORKSPACE"

# The GitHub MCP plugin expects this exact variable. Reuse the GitHub CLI
# keychain token so no secret is stored in shell startup files.
if [ -z "${GITHUB_PAT_TOKEN:-}" ] && command -v gh >/dev/null 2>&1; then
  GITHUB_PAT_TOKEN="$(gh auth token 2>/dev/null)"
  if [ -n "$GITHUB_PAT_TOKEN" ]; then
    export GITHUB_PAT_TOKEN
  else
    unset GITHUB_PAT_TOKEN
  fi
fi
