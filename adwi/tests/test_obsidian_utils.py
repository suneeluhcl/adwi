"""Tests for adwi/obsidian_utils.py — marker-block helpers."""

import importlib.util
import sys
import unittest
from pathlib import Path

# Load obsidian_utils from its known path without requiring adwi to be a package.
_spec = importlib.util.spec_from_file_location(
    "obsidian_utils",
    Path(__file__).resolve().parents[1] / "obsidian_utils.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
replace_marker_block    = _mod.replace_marker_block
daily_note_template     = _mod.daily_note_template
today_note_path         = _mod.today_note_path
append_under_heading    = _mod.append_under_heading
append_to_daily_section = _mod.append_to_daily_section


class TestReplaceMarkerBlock(unittest.TestCase):

    def _make_note(self, manual="manual content here"):
        return f"# 2026-01-01\n\n## Notes\n\n{manual}\n"

    # ── append when absent ────────────────────────────────────────────────────

    def test_appends_block_when_absent(self):
        note = self._make_note()
        result = replace_marker_block(note, "ADWI:TEST", "generated body")
        self.assertIn("<!-- ADWI:TEST:START -->", result)
        self.assertIn("<!-- ADWI:TEST:END -->", result)
        self.assertIn("generated body", result)

    def test_appends_after_existing_content(self):
        note = self._make_note("my manual notes")
        result = replace_marker_block(note, "ADWI:TEST", "new body")
        self.assertTrue(result.index("my manual notes") < result.index("<!-- ADWI:TEST:START -->"))

    # ── replace when present ─────────────────────────────────────────────────

    def test_replaces_existing_block(self):
        note = (
            "# 2026-01-01\n\n"
            "<!-- ADWI:TEST:START -->\nold body\n<!-- ADWI:TEST:END -->\n"
        )
        result = replace_marker_block(note, "ADWI:TEST", "new body")
        self.assertIn("new body", result)
        self.assertNotIn("old body", result)

    def test_replace_keeps_exactly_one_block(self):
        note = (
            "before\n"
            "<!-- ADWI:TEST:START -->\nold\n<!-- ADWI:TEST:END -->\n"
            "after\n"
        )
        result = replace_marker_block(note, "ADWI:TEST", "replaced")
        self.assertEqual(result.count("<!-- ADWI:TEST:START -->"), 1)
        self.assertEqual(result.count("<!-- ADWI:TEST:END -->"), 1)

    # ── preserves manual content ─────────────────────────────────────────────

    def test_preserves_content_before_marker(self):
        note = "## Manual\n\nmy handwritten note\n\n<!-- ADWI:TEST:START -->\nold\n<!-- ADWI:TEST:END -->\n"
        result = replace_marker_block(note, "ADWI:TEST", "auto")
        self.assertIn("my handwritten note", result)

    def test_preserves_content_after_marker(self):
        note = "<!-- ADWI:TEST:START -->\nold\n<!-- ADWI:TEST:END -->\n\n## After\n\nstill here\n"
        result = replace_marker_block(note, "ADWI:TEST", "auto")
        self.assertIn("still here", result)

    def test_preserves_other_marker_blocks(self):
        note = (
            "<!-- ADWI:A:START -->\nbody-a\n<!-- ADWI:A:END -->\n"
            "<!-- ADWI:B:START -->\nbody-b\n<!-- ADWI:B:END -->\n"
        )
        result = replace_marker_block(note, "ADWI:A", "new-a")
        self.assertIn("new-a", result)
        self.assertIn("body-b", result)

    # ── idempotency ──────────────────────────────────────────────────────────

    def test_multiple_updates_idempotent(self):
        note = self._make_note()
        r1 = replace_marker_block(note, "ADWI:TEST", "body v1")
        r2 = replace_marker_block(r1,   "ADWI:TEST", "body v2")
        r3 = replace_marker_block(r2,   "ADWI:TEST", "body v2")
        self.assertEqual(r2, r3)
        self.assertIn("body v2", r3)
        self.assertNotIn("body v1", r3)

    def test_block_count_stable_across_multiple_writes(self):
        note = self._make_note()
        for i in range(5):
            note = replace_marker_block(note, "ADWI:TEST", f"iteration {i}")
        self.assertEqual(note.count("<!-- ADWI:TEST:START -->"), 1)

    # ── block body with special characters ──────────────────────────────────

    def test_handles_multiline_block_body(self):
        body = "line 1\nline 2\n```json\n{}\n```"
        note = self._make_note()
        result = replace_marker_block(note, "ADWI:TEST", body)
        self.assertIn("line 1\nline 2", result)

    def test_handles_empty_block_body(self):
        note = self._make_note()
        result = replace_marker_block(note, "ADWI:TEST", "")
        self.assertIn("<!-- ADWI:TEST:START -->", result)
        self.assertIn("<!-- ADWI:TEST:END -->", result)


class TestDailyNoteTemplate(unittest.TestCase):

    def test_contains_date(self):
        t = daily_note_template("2026-06-21")
        self.assertIn("# 2026-06-21", t)

    def test_contains_standard_sections(self):
        t = daily_note_template("2026-06-21")
        for section in ("Current Focus", "Decisions", "Ideas", "Bugs / Fixes", "Pending Approval"):
            self.assertIn(section, t)

    def test_no_marker_blocks_in_fresh_template(self):
        t = daily_note_template("2026-06-21")
        self.assertNotIn("<!-- ADWI:", t)


class TestTodayNotePath(unittest.TestCase):

    def test_returns_path_in_daily_notes(self):
        from pathlib import Path
        vault = Path("/tmp/fake-vault")
        p = today_note_path(vault)
        self.assertEqual(p.parent, vault / "daily-notes")
        self.assertTrue(p.name.endswith(".md"))

    def test_filename_matches_iso_date(self):
        import re
        from pathlib import Path
        p = today_note_path(Path("/tmp/v"))
        self.assertRegex(p.name, r"^\d{4}-\d{2}-\d{2}\.md$")


class TestAppendUnderHeading(unittest.TestCase):

    _SAMPLE = (
        "# 2026-01-01\n\n"
        "## Current Focus\n\nfocus item\n\n"
        "## Ideas\n\n\n"
        "## Bugs / Fixes\n\n"
    )

    def test_appends_to_existing_nonempty_section(self):
        result = append_under_heading(self._SAMPLE, "## Current Focus", "- new task")
        self.assertIn("focus item", result)
        self.assertIn("- new task", result)
        # new entry must be after the existing content
        self.assertGreater(result.index("- new task"), result.index("focus item"))

    def test_appends_to_existing_empty_section(self):
        result = append_under_heading(self._SAMPLE, "## Ideas", "- my idea")
        self.assertIn("- my idea", result)

    def test_creates_section_if_absent(self):
        result = append_under_heading(self._SAMPLE, "## Notes", "- new note")
        self.assertIn("## Notes", result)
        self.assertIn("- new note", result)

    def test_no_duplicate_on_second_call(self):
        r1 = append_under_heading(self._SAMPLE, "## Ideas", "- dedup me")
        r2 = append_under_heading(r1, "## Ideas", "- dedup me")
        self.assertEqual(r1, r2)

    def test_preserves_content_outside_section(self):
        result = append_under_heading(self._SAMPLE, "## Ideas", "- x")
        self.assertIn("focus item", result)
        self.assertIn("## Bugs / Fixes", result)

    def test_stops_before_adwi_marker(self):
        text = (
            "## Ideas\n\n"
            "<!-- ADWI:DAILY-SUMMARY:START -->\ngenerated\n<!-- ADWI:DAILY-SUMMARY:END -->\n"
        )
        result = append_under_heading(text, "## Ideas", "- captured")
        # Entry must appear before the marker, not inside it
        self.assertLess(result.index("- captured"), result.index("<!-- ADWI:DAILY-SUMMARY:START -->"))

    def test_entry_placed_before_next_heading(self):
        result = append_under_heading(self._SAMPLE, "## Current Focus", "- after existing")
        focus_end = result.index("## Ideas")
        entry_pos = result.index("- after existing")
        self.assertLess(entry_pos, focus_end)

    def test_idempotent_multiple_writes(self):
        text = self._SAMPLE
        for _ in range(5):
            text = append_under_heading(text, "## Ideas", "- repeated")
        self.assertEqual(text.count("- repeated"), 1)


class TestAppendToDailySection(unittest.TestCase):

    def setUp(self):
        import tempfile
        self._tmp = Path(tempfile.mkdtemp())
        self._vault = self._tmp / "vault"
        self._vault.mkdir()

    def tearDown(self):
        import shutil
        shutil.rmtree(self._tmp, ignore_errors=True)

    def test_creates_note_if_absent(self):
        ok, msg = append_to_daily_section(self._vault, "2026-01-01", "## Ideas", "- fresh idea")
        self.assertTrue(ok)
        note = (self._vault / "daily-notes" / "2026-01-01.md").read_text()
        self.assertIn("- fresh idea", note)

    def test_appends_to_existing_note(self):
        note_path = self._vault / "daily-notes" / "2026-01-01.md"
        note_path.parent.mkdir(parents=True)
        note_path.write_text("# 2026-01-01\n\n## Ideas\n\nexisting idea\n")
        ok, _ = append_to_daily_section(self._vault, "2026-01-01", "## Ideas", "- new idea")
        self.assertTrue(ok)
        content = note_path.read_text()
        self.assertIn("existing idea", content)
        self.assertIn("- new idea", content)

    def test_returns_tuple_with_path_on_success(self):
        ok, msg = append_to_daily_section(self._vault, "2026-01-02", "## Notes", "- hi")
        self.assertIsInstance(ok, bool)
        self.assertIsInstance(msg, str)
        self.assertTrue(ok)
        self.assertIn("2026-01-02", msg)


if __name__ == "__main__":
    unittest.main()
