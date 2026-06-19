"""
commands/gmail.py — Gmail listing and display commands (Phase 5A, read-only).

These commands fetch and display Gmail state without sending, modifying, or
deleting messages, drafts, or rules. Some cache results to _GMAIL_CTX (e.g.
draft_list, attachments) as in-memory state for subsequent commands — that is
their expected behavior, identical to the elif chain they replace.

Mutating Gmail commands (compose, send, archive, trash, mark, confirm, cancel,
forward, schedule, filter-apply, etc.) are deferred to Phase 6.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from adwi.command_registry import CommandRegistry


def _cli():
    import importlib.util
    from pathlib import Path
    if "adwi_cli" not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            "adwi_cli",
            Path(__file__).parent.parent / "adwi_cli.py",
        )
        mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
        sys.modules["adwi_cli"] = mod
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return sys.modules["adwi_cli"]


# ── Handlers ──────────────────────────────────────────────────────────────────


def _show_draft(args: str, ctx: dict) -> None:
    _cli().cmd_gmail_show_draft()


def _followups(args: str, ctx: dict) -> None:
    _cli().cmd_gmail_list_followups()


def _scheduled(args: str, ctx: dict) -> None:
    _cli().cmd_gmail_list_scheduled()


def _drafts(args: str, ctx: dict) -> None:
    _cli().cmd_gmail_list_drafts(args)


def _rules(args: str, ctx: dict) -> None:
    _cli().cmd_gmail_filter_list(args)


def _promos(args: str, ctx: dict) -> None:
    _cli().cmd_gmail_list_category("promotions")


def _spam(args: str, ctx: dict) -> None:
    _cli().cmd_gmail_list_category("spam")


def _social(args: str, ctx: dict) -> None:
    _cli().cmd_gmail_list_category("social")


def _attachments(args: str, ctx: dict) -> None:
    _cli().cmd_gmail_list_attachments(args)


# ── Registration ──────────────────────────────────────────────────────────────


def register(registry: "CommandRegistry") -> None:
    registry.register(
        "/gmail-show-draft",
        description="Show the current pending Gmail draft",
        category="gmail",
        intents=["gmail_show_draft"],
    )(_show_draft)

    registry.register(
        "/gmail-followups",
        description="List all Gmail follow-up reminders with live reply-detection",
        category="gmail",
        intents=["gmail_list_followups"],
    )(_followups)

    registry.register(
        "/gmail-scheduled",
        description="Show all Adwi-scheduled pending Gmail sends",
        category="gmail",
        intents=["gmail_list_scheduled"],
    )(_scheduled)

    registry.register(
        "/gmail-drafts",
        description="List all Gmail drafts with metadata",
        category="gmail",
        intents=["gmail_list_drafts"],
        args_schema={"filter": "str?"},
    )(_drafts)

    registry.register(
        "/gmail-rules",
        description="List locally saved Gmail filter rules",
        category="gmail",
        intents=["gmail_filter_list"],
        args_schema={"filter": "str?"},
    )(_rules)

    registry.register(
        "/gmail-promos",
        description="List Gmail Promotions category emails",
        category="gmail",
        intents=["gmail_list_category"],
    )(_promos)

    registry.register(
        "/gmail-spam",
        description="List Gmail Spam folder emails",
        category="gmail",
    )(_spam)

    registry.register(
        "/gmail-social",
        description="List Gmail Social category emails",
        category="gmail",
    )(_social)

    registry.register(
        "/gmail-attachments",
        description="List attachments on the current email or thread",
        category="gmail",
        intents=["gmail_list_attachments"],
        args_schema={"filter": "str?"},
    )(_attachments)
