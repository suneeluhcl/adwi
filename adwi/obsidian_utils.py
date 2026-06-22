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


def append_under_heading(text: str, heading: str, entry: str) -> str:
    """Append *entry* under the first occurrence of *heading* in *text*.

    - heading: full heading line e.g. "## Ideas"
    - entry:   text to append  e.g. "- 14:32 — bought groceries"
    - Skips silently if the exact entry already exists under that heading.
    - Creates the heading at the end of *text* if it is absent.
    - Never inserts inside a <!-- ADWI:...: --> marker block.
    """
    h = heading.rstrip()
    entry_line = entry.rstrip("\n")

    # Match heading + all content until next ##-heading, ADWI marker, or EOF.
    pat = re.compile(
        r"^" + re.escape(h) + r"\n(.*?)(?=^##\s|^<!-- ADWI:|\Z)",
        re.DOTALL | re.MULTILINE,
    )
    m = pat.search(text)
    if m:
        body = m.group(1)
        if entry_line in body:
            return text
        body_stripped = body.rstrip("\n")
        new_body = (body_stripped + "\n\n") if body_stripped else "\n"
        new_body += entry_line + "\n"
        return text[: m.start(1)] + new_body + text[m.start(1) + len(body) :]
    else:
        return text.rstrip("\n") + f"\n\n{h}\n\n{entry_line}\n"


def append_to_daily_section(vault: Path, date: str, section: str, entry: str) -> tuple:
    """Read/create *date*'s daily note and append *entry* under *section*.

    Returns (success: bool, message: str).
    """
    try:
        note_path = vault / "daily-notes" / f"{date}.md"
        note_path.parent.mkdir(parents=True, exist_ok=True)
        existing = (
            note_path.read_text(encoding="utf-8")
            if note_path.exists()
            else daily_note_template(date)
        )
        note_path.write_text(append_under_heading(existing, section, entry), encoding="utf-8")
        return True, str(note_path)
    except Exception as exc:
        return False, str(exc)
