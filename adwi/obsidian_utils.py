"""
adwi/obsidian_utils.py — shared Obsidian vault helpers (stdlib-only, no adwi imports).

Used by: adwi_cli.py, nightly.py, services/mcp/obsidian-bridge/server.py
"""

import re
from datetime import datetime
from pathlib import Path

_TEMPLATE = (
    "# {date}\n\n"
    "## Current Focus\n\n\n"
    "## Decisions\n\n\n"
    "## Ideas\n\n\n"
    "## Bugs / Fixes\n\n\n"
    "## Pending Approval\n\n\n"
)


def replace_marker_block(text: str, marker: str, block_body: str) -> str:
    """Replace or append a <!-- MARKER:START/END -->-delimited block.

    - Both START and END tags present: replaces the block in-place.
    - Tags absent: appends a new block at the end of the text.
    - Content outside the markers is never modified.
    """
    start_tag = f"<!-- {marker}:START -->"
    end_tag   = f"<!-- {marker}:END -->"
    new_block = f"{start_tag}\n{block_body}\n{end_tag}"
    if start_tag in text and end_tag in text:
        return re.sub(
            re.escape(start_tag) + r".*?" + re.escape(end_tag),
            new_block, text, flags=re.DOTALL,
        )
    return text.rstrip("\n") + "\n\n" + new_block + "\n"


def daily_note_template(date: str) -> str:
    """Return the default empty daily-note template for *date* (YYYY-MM-DD)."""
    return _TEMPLATE.format(date=date)


def today_note_path(vault: Path) -> Path:
    """Return the path for today's daily note (does not create the file)."""
    return vault / "daily-notes" / f"{datetime.now().strftime('%Y-%m-%d')}.md"
