from __future__ import annotations

import contextlib
import importlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / ".agents/skills/paper-craft/scripts"
sys.path.insert(0, str(SCRIPTS))
install_skill = importlib.import_module("install_skill")


class InstallTargetsTests(unittest.TestCase):
    def invoke(self, arguments: list[str]) -> tuple[int, str]:
        output = io.StringIO()
        with patch.object(sys, "argv", [str(SCRIPTS / "install_skill.py"), *arguments]):
            with contextlib.redirect_stdout(output):
                status = install_skill.main()
        if artifact := os.environ.get("PAPER_CRAFT_TEST_LOG"):
            with open(artifact, "a", encoding="utf-8") as stream:
                stream.write(json.dumps({"invocation": sys.executable,
                                         "args": [str(SCRIPTS / "install_skill.py"), *arguments],
                                         "status": status, "stdout": output.getvalue()}) + "\n")
        return status, output.getvalue()

    def test_source_overlap_refuses_entire_batch_before_copy(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            first = Path(temporary) / "first/paper-craft"
            status, output = self.invoke(["--destination", str(first), "--destination", str(SCRIPTS.parent),
                                          "--update"])
            self.assertEqual(status, 2)
            report = json.loads(output)
            self.assertEqual(report["completed"], [])
            self.assertIn("overlap", report["error"])
            self.assertFalse(first.parent.exists())

    def test_nested_destinations_refuse_entire_batch_before_copy(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            first = Path(temporary) / "paper-craft"
            status, output = self.invoke(["--destination", str(first),
                                          "--destination", str(first / "nested/paper-craft")])
            self.assertEqual(status, 2)
            self.assertIn("overlap", json.loads(output)["error"])
            self.assertFalse(first.exists())

    def test_home_expansion_failure_returns_batch_json_with_raw_remaining_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            first = Path(temporary) / "first/paper-craft"
            invalid = Path("~paper-craft-missing-user/paper-craft")
            expanduser = Path.expanduser

            def reject_missing_home(path: Path) -> Path:
                if path == invalid:
                    raise RuntimeError("Could not determine home directory.")
                return expanduser(path)

            with patch.object(Path, "expanduser", reject_missing_home):
                status, output = self.invoke(["--destination", str(first), "--destination", str(invalid)])
            report = json.loads(output)
            self.assertEqual(status, 2)
            self.assertEqual(report["status"], "FAIL")
            self.assertEqual(report["completed"], [])
            self.assertEqual(report["remaining"], [str(first), str(invalid)])
            self.assertIn("home directory", report["error"])
            self.assertFalse(first.parent.exists())

    def test_io_failure_reports_completed_targets_and_restores_failed_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            first = Path(temporary) / "one/skills/paper-craft"
            second = Path(temporary) / "two/skills/paper-craft"
            for destination in [first, second]:
                destination.mkdir(parents=True)
                (destination / "local.txt").write_text(str(destination), encoding="utf-8")
            alias = Path(temporary) / "alias"
            alias.symlink_to(first.parent, target_is_directory=True)
            rename = os.rename

            def fail_second_stage(source: str | Path, destination: str | Path) -> None:
                if Path(destination) == second and Path(source).parent.name.startswith(".paper-craft-install-"):
                    raise OSError("injected disk failure on second target")
                rename(source, destination)

            with patch.object(install_skill.os, "rename", side_effect=fail_second_stage):
                status, output = self.invoke(["--destination", str(first),
                                              "--destination", str(alias / "paper-craft"),
                                              "--destination", str(second),
                                              "--update"])
            report = json.loads(output)
            self.assertEqual(status, 2)
            self.assertEqual(report["status"], "FAIL")
            self.assertEqual([item["destination"] for item in report["completed"]], [str(first)])
            self.assertEqual(report["remaining"], [str(second)])
            self.assertIn("injected disk failure", report["error"])
            self.assertTrue((first / "SKILL.md").is_file())
            backup = Path(report["completed"][0]["backup"])
            self.assertEqual((backup / "local.txt").read_text(encoding="utf-8"), str(first))
            self.assertEqual((second / "local.txt").read_text(encoding="utf-8"), str(second))


if __name__ == "__main__":
    unittest.main()
