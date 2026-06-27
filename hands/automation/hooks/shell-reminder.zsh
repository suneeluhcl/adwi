# Optional shell reminder for SuneelWorkSpace.
# This file is sourced from ~/.zshrc when installed. It prints at most once per
# shell session, when the shell starts in the workspace or later cd's into it.

suneel_workspace_reminder() {
  case "$PWD" in
    "$HOME/SuneelWorkSpace"|"$HOME/SuneelWorkSpace"/*) ;;
    *) return 0 ;;
  esac
  if [ -z "${SUNEEL_WORKSPACE_SESSION_STARTED:-}" ] && [ -x "$HOME/SuneelWorkSpace/bin/agent-start" ]; then
    export SUNEEL_WORKSPACE_SESSION_STARTED=1
    "$HOME/SuneelWorkSpace/bin/agent-start" --quiet >/dev/null 2>&1 || true
  fi
  if [ -z "${SUNEEL_WORKSPACE_REMINDER_SHOWN:-}" ]; then
    export SUNEEL_WORKSPACE_REMINDER_SHOWN=1
    if [ -x "$HOME/SuneelWorkSpace/bin/agent-status" ]; then
      echo "SuneelWorkSpace ready. Run swstatus or agent-start for shared context."
    fi
  fi
}

suneel_workspace_exit_checkpoint() {
  case "$PWD" in
    "$HOME/SuneelWorkSpace"|"$HOME/SuneelWorkSpace"/*)
      if [ -x "$HOME/SuneelWorkSpace/bin/agent-autoclose" ]; then
        "$HOME/SuneelWorkSpace/bin/agent-autoclose" --shell-exit --quiet >/dev/null 2>&1 || true
      fi
      ;;
  esac
}

suneel_workspace_reminder

if [ -n "${ZSH_VERSION:-}" ]; then
  autoload -Uz add-zsh-hook 2>/dev/null || true
  if command -v add-zsh-hook >/dev/null 2>&1; then
    add-zsh-hook chpwd suneel_workspace_reminder
    add-zsh-hook zshexit suneel_workspace_exit_checkpoint
  fi
fi
