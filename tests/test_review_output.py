from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / ".agents/skills/paper-craft/scripts"
sys.path.insert(0, str(SCRIPTS))
review_output = importlib.import_module("review_output")


class ReviewOutputTests(unittest.TestCase):
    def test_explicit_directory_overrides_environment(self) -> None:
        with tempfile.TemporaryDirectory() as temporary, patch.dict(os.environ, {"PAPER_CRAFT_OUTPUT_DIR": "other"}):
            expected = Path(temporary).resolve() / "selected"
            path, origin = review_output.select_output(expected)
            self.assertEqual(path, expected)
            self.assertEqual(origin, "explicit")

    def test_environment_directory_is_used_without_creation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary).resolve() / "private reviews"
            result = subprocess.run([sys.executable, str(SCRIPTS / "review_output.py"), "--json"],
                                    env={**os.environ, "PAPER_CRAFT_OUTPUT_DIR": str(path)},
                                    capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["output_dir"], str(path))
            self.assertFalse(report["created"])
            self.assertFalse(path.exists())

    def test_os_defaults_use_user_state_outside_skill_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary).resolve()
            cases = [("linux", home / ".local/state/paper-craft/reviews"),
                     ("darwin", home / "Library/Application Support/PaperCraft/reviews"),
                     ("win32", home / "AppData/Local/PaperCraft/reviews")]
            for platform, base in cases:
                with self.subTest(platform=platform), patch.dict(os.environ, {}, clear=True), \
                     patch.object(Path, "home", return_value=home), patch.object(sys, "platform", platform):
                    output, origin = review_output.select_output()
                    self.assertEqual(output.parent, base)
                    self.assertEqual(origin, "os_default")
                    self.assertFalse(output.exists())

    def test_git_tracked_and_unignored_outputs_warn_without_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            tracked = root / "tracked"
            tracked.mkdir()
            source = tracked / "paper.txt"
            source.write_text("private original", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "tracked/paper.txt"], check=True)
            before = source.read_bytes()
            self.assertTrue(review_output.output_warnings(tracked))
            self.assertTrue(review_output.output_warnings(root / "new-reviews"))
            (root / ".gitignore").write_text("ignored/\n", encoding="utf-8")
            self.assertEqual(review_output.output_warnings(root / "ignored"), [])
            self.assertEqual(source.read_bytes(), before)

    def test_hashes_record_original_and_proposal_without_modification(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source, proposal = root / "original.tex", root / "proposal.tex"
            source.write_text("original result 10 ns", encoding="utf-8")
            proposal.write_text("proposed result 10 ns", encoding="utf-8")
            before = source.read_bytes(), proposal.read_bytes()
            result = subprocess.run([sys.executable, str(SCRIPTS / "review_output.py"),
                                     "--output-dir", str(root / "reports"), "--create", "--inputs", str(source),
                                     "--proposals", str(proposal), "--json"],
                                    capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertTrue(report["created"])
            self.assertEqual(report["inputs"][0]["status"], "HASHED")
            self.assertEqual(len(report["inputs"][0]["sha256"]), 64)
            self.assertNotEqual(report["inputs"][0]["sha256"], report["proposals"][0]["sha256"])
            self.assertEqual((source.read_bytes(), proposal.read_bytes()), before)

    def test_existing_private_outputs_are_git_ignored(self) -> None:
        result = subprocess.run(["git", "check-ignore", "output/reviews/paper/proposal.tex"],
                                cwd=SCRIPTS.parents[3], capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_git_execution_failure_is_not_a_clean_tracking_check(self) -> None:
        for error in (FileNotFoundError("git unavailable"), subprocess.TimeoutExpired("git", 10)):
            with self.subTest(error=type(error).__name__), tempfile.TemporaryDirectory() as temporary, \
                 patch.object(review_output.subprocess, "run", side_effect=error):
                warnings = review_output.output_warnings(Path(temporary) / "reports")
                self.assertTrue(warnings)
                self.assertIn("could not be checked", warnings[0])


if __name__ == "__main__":
    unittest.main()
