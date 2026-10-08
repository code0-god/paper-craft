"""Package discovery, isolated installs and preservation checks; no external dependencies."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / ".agents" / "skills" / "paper-craft"


class PackageTests(unittest.TestCase):
    def test_package_validates_when_complete(self) -> None:
        result = subprocess.run([sys.executable, str(SKILL / "scripts/validate_skill.py"), "--json"],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "PASS")

    def test_isolated_install_runs_without_source_materials(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            installed = Path(temporary) / "paper-craft"
            result = subprocess.run([sys.executable, str(SKILL / "scripts/install_skill.py"),
                                     "--destination", str(installed)],
                                    capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            validation = subprocess.run([sys.executable, str(installed / "scripts/validate_skill.py"),
                                         "--json"], cwd=temporary,
                                        capture_output=True, text=True, check=False)
            self.assertEqual(validation.returncode, 0, validation.stdout + validation.stderr)
            self.assertFalse((installed / "source-materials").exists())
            for script in sorted((installed / "scripts").glob("*.py")):
                if script.name.endswith("common.py") or script.name.startswith("_"):
                    continue
                help_result = subprocess.run([sys.executable, str(script), "--help"], cwd=temporary,
                                             capture_output=True, text=True, check=False)
                self.assertEqual(help_result.returncode, 0, str(script) + help_result.stderr)

    def test_existing_install_requires_update_and_preserves_user_data(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "paper-craft"
            destination.mkdir()
            note = destination / "local-notes.txt"
            note.write_text("keep research notes", encoding="utf-8")
            command = [sys.executable, str(SKILL / "scripts/install_skill.py"),
                       "--destination", str(destination)]
            refused = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertEqual(refused.returncode, 2)
            self.assertEqual(note.read_text(encoding="utf-8"), "keep research notes")
            updated = subprocess.run([*command, "--update"], capture_output=True, text=True, check=False)
            self.assertEqual(updated.returncode, 0, updated.stdout + updated.stderr)
            backup = Path(json.loads(updated.stdout)["backup"])
            self.assertEqual((backup / "local-notes.txt").read_text(encoding="utf-8"), "keep research notes")
            self.assertTrue((destination / "SKILL.md").is_file())

    def test_installed_tools_resolve_resources_outside_repository(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            installed = Path(temporary) / "paper-craft"
            install_result = subprocess.run(
                [sys.executable, str(SKILL / "scripts/install_skill.py"), "--destination", str(installed)],
                capture_output=True, text=True, check=False)
            self.assertEqual(install_result.returncode, 0, install_result.stdout + install_result.stderr)
            manuscript = Path(temporary) / "paper.tex"
            manuscript.write_text(
                "\\documentclass{article}\n\\begin{document}\n"
                "\\section{Method}\\label{sec:method}\nSee~\\ref{sec:method}.\n\\end{document}\n",
                encoding="utf-8")
            snapshot = manuscript.read_bytes()
            commands = [
                ["latex_integrity_check.py", str(manuscript), "--json"],
                ["reference_audit.py", str(manuscript), "--json"],
                ["validate_profiles.py", "--json"],
                ["venue_preflight.py", str(manuscript), "--venue", "ISCA", "--year", "2026",
                 "--track", "research", "--stage", "submission", "--offline", "--json"],
            ]
            for arguments in commands:
                result = subprocess.run(
                    [sys.executable, str(installed / "scripts" / arguments[0]), *arguments[1:]],
                    cwd=temporary, capture_output=True, text=True, check=False)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                report = json.loads(result.stdout)
                self.assertFalse(any(item["status"] == "FAIL" for item in report["findings"]))
                if report["tool"] == "venue_preflight":
                    self.assertIsNotNone(report["profile"])
                    self.assertFalse(report["current_rules_verified"])
            self.assertEqual(manuscript.read_bytes(), snapshot)

    def test_update_backup_stays_outside_skill_discovery_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / ".agents/skills/paper-craft"
            destination.mkdir(parents=True)
            (destination / "SKILL.md").write_text("old user content", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SKILL / "scripts/install_skill.py"),
                 "--destination", str(destination), "--update"],
                capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            backup = Path(json.loads(result.stdout)["backup"])
            self.assertFalse(backup.is_relative_to(destination.parent))
            self.assertEqual((backup / "SKILL.md").read_text(encoding="utf-8"), "old user content")

    def test_broken_reference_fails_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "paper-craft"
            root.mkdir()
            (root / "SKILL.md").write_text(
                '---\nname: paper-craft\ndescription: "Architecture research review"\n---\n'
                '[Required](references/missing.md)\n', encoding="utf-8")
            result = subprocess.run([sys.executable, str(SKILL / "scripts/validate_skill.py"),
                                     str(root), "--json"], capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 1)
            checks = {finding["check"] for finding in json.loads(result.stdout)["findings"]}
            self.assertIn("internal_link", checks)

    def test_invalid_frontmatter_is_rejected(self) -> None:
        for frontmatter in ('name: paper-craft\ndescription: []',
                            'name: paper-craft\nname: paper-craft\ndescription: "Review"',
                            'name: paper-craft\ndescription: ""'):
            with self.subTest(frontmatter=frontmatter), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary) / "paper-craft"
                root.mkdir()
                (root / "SKILL.md").write_text(f"---\n{frontmatter}\n---\nReview.\n", encoding="utf-8")
                result = subprocess.run([sys.executable, str(SKILL / "scripts/validate_skill.py"),
                                         str(root), "--json"], capture_output=True, text=True, check=False)
                self.assertEqual(result.returncode, 1)
                checks = {finding["check"] for finding in json.loads(result.stdout)["findings"]}
                self.assertTrue(checks.intersection({"frontmatter", "description"}))


if __name__ == "__main__":
    unittest.main()
