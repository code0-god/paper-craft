"""Concrete independent-audit regressions through the public CLI."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / ".agents/skills/paper-craft/scripts"


class AuditRegressions(unittest.TestCase):
    def run_tool(self, name: str, arguments: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, str(SCRIPTS / name), *arguments, "--json"],
                              capture_output=True, text=True, check=False, timeout=30)

    def test_direct_bib_when_duplicate_keys_exist(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            bibliography = Path(folder) / "refs.bib"
            bibliography.write_text("@misc{same,title={One}}\n@misc{same,title={Two}}\n", encoding="utf-8")
            result = self.run_tool("reference_audit.py", [str(bibliography)])
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("duplicate_bib_key", {item["check"] for item in json.loads(result.stdout)["findings"]})

    def test_directory_when_candidate_symlink_escapes(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            project = Path(folder) / "project"
            project.mkdir()
            outside = Path(folder) / "outside.tex"
            outside.write_text(r"\documentclass{article}\ref{OUTSIDE_PRIVATE_SENTINEL}", encoding="utf-8")
            (project / "linked.tex").symlink_to(outside)
            result = self.run_tool("latex_integrity_check.py", [str(project), "--project-root", str(project)])
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("OUTSIDE_PRIVATE_SENTINEL", result.stdout + result.stderr)

    def test_editing_when_leading_decimal_changes_value(self) -> None:
        self.assert_protected_change(".5 ns", "5 ns", ".tex", "numeric_tokens")

    def test_editing_when_byte_changes_to_bit(self) -> None:
        self.assert_protected_change("10 B", "10 b", ".tex", "unit_tokens")

    def test_editing_when_bibtex_key_changes(self) -> None:
        self.assert_protected_change("@misc{original,title={Title}}", "@misc{renamed,title={Title}}",
                                     ".bib", "bibtex_keys")

    def assert_protected_change(self, before: str, after: str, suffix: str, check: str) -> None:
        with tempfile.TemporaryDirectory() as folder:
            original, revised = Path(folder) / f"old{suffix}", Path(folder) / f"new{suffix}"
            original.write_text(before, encoding="utf-8")
            revised.write_text(after, encoding="utf-8")
            result = self.run_tool("editing_guard.py", [str(original), str(revised)])
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn(check, {item["check"] for item in json.loads(result.stdout)["findings"]
                              if item["status"] == "FAIL"})

    def test_reference_when_linebreak_precedes_literal_command_name(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            manuscript = Path(folder) / "main.tex"
            manuscript.write_text(r"\documentclass{article}\\ref{literal}", encoding="utf-8")
            result = self.run_tool("latex_integrity_check.py", [str(manuscript)])
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertNotIn("unresolved_reference", {item["check"] for item in json.loads(result.stdout)["findings"]})

    def test_source_when_adjacent_paragraphs_share_line(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "reference.html"
            source.write_text("<p>First claim.</p><p>Second claim.</p>", encoding="utf-8")
            result = self.run_tool("source_material.py", ["inspect", str(source), "--source-id", "B"])
        blocks = json.loads(result.stdout)["blocks"]
        self.assertEqual([block["text"] for block in blocks], ["First claim.", "Second claim."])

    def test_diff_when_original_has_no_final_newline(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            original, revised = Path(folder) / "old.txt", Path(folder) / "new.txt"
            original.write_text("Latency is 10 ns.", encoding="utf-8")
            revised.write_text("Measured latency is 10 ns.", encoding="utf-8")
            result = self.run_tool("editing_guard.py", [str(original), str(revised)])
        lines = json.loads(result.stdout)["unified_diff"].splitlines()
        self.assertIn("-Latency is 10 ns.", lines)
        self.assertIn("+Measured latency is 10 ns.", lines)
        self.assertEqual(lines.count("\\ No newline at end of file"), 2)


if __name__ == "__main__":
    unittest.main()
