"""Exercise CLI page-range decisions with a controlled pdfinfo subprocess response."""

from __future__ import annotations

import contextlib
import importlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents/skills/paper-craft"
sys.path.insert(0, str(SKILL / "scripts"))
venue_preflight = importlib.import_module("venue_preflight")


class VenueLimitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.folder = Path(self.temporary.name)
        self.profile = self.load_profile("ksc-2026-research-submission.json")
        self.pdf = self.folder / "paper.pdf"
        self.pdf.write_bytes(b"%PDF-1.4\n% synthetic input for the pdfinfo subprocess seam\n")

    def load_profile(self, name: str) -> dict:
        profile = json.loads((SKILL / "venues/profiles" / name).read_text(encoding="utf-8"))
        profile["last_verified_date"] = date.today().isoformat()
        for rule in profile["rules"].values():
            if rule["verification_status"] == "verified":
                rule["verified_at"] = date.today().isoformat()
        return profile

    def write_package(self) -> None:
        registry = json.loads((SKILL / "venues/registry.json").read_text(encoding="utf-8"))
        entry = next(item for item in registry["venues"] if item["venue_id"] == self.profile["venue_id"])
        entry["profiles"] = ["profile.json"]
        (self.folder / "registry.json").write_text(
            json.dumps({"schema_version": 1, "venues": [entry]}), encoding="utf-8",
        )
        (self.folder / "profile.json").write_text(json.dumps(self.profile), encoding="utf-8")

    def preflight(self, pages: int, extra: tuple[str, ...] = ()) -> subprocess.CompletedProcess[str]:
        self.write_package()
        arguments = [sys.executable, str(SKILL / "scripts/venue_preflight.py"), str(self.pdf),
                     "--venue", self.profile["venue_id"], "--track", self.profile["track"],
                     "--profile-root", str(self.folder), "--json", *extra]
        if self.profile["year"] is not None:
            arguments.extend(["--year", str(self.profile["year"])])
        output, errors = io.StringIO(), io.StringIO()
        response = subprocess.CompletedProcess(["pdfinfo-test", str(self.pdf.resolve())], 0,
                                               f"Pages: {pages}\n", "")
        with patch.object(sys, "argv", arguments[1:]), \
                patch.object(venue_preflight.shutil, "which", return_value="pdfinfo-test"), \
                patch.object(venue_preflight.subprocess, "run", return_value=response) as pdfinfo, \
                contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            status = venue_preflight.main()
        pdfinfo.assert_called_once_with(["pdfinfo-test", str(self.pdf.resolve())], capture_output=True,
                                       text=True, timeout=30, check=False)
        return subprocess.CompletedProcess(arguments, status, output.getvalue(), errors.getvalue())

    def assert_pages(self, result: subprocess.CompletedProcess[str], pages: int, status: str) -> None:
        report = json.loads(result.stdout)
        finding = next(item for item in report["findings"] if item["check"] == "pdf_page_count")
        self.assertEqual(result.returncode, int(status == "FAIL"), result.stderr)
        self.assertEqual(finding["observed_total_pages"], pages)
        self.assertEqual(finding["status"], status)
        self.assertFalse(report["current_rules_verified"])
        self.assertEqual(report["submission_compliance"], "UNKNOWN")

    def test_underflow_when_cached_minimum_is_two(self) -> None:
        # Given fresh cached KSC rules requiring 2..3 total pages.
        # When pdfinfo reports one page.
        result = self.preflight(1)
        # Then cached comparison fails without certifying current rules.
        self.assert_pages(result, 1, "FAIL")

    def test_range_when_total_matches_either_boundary(self) -> None:
        for pages in (2, 3):
            with self.subTest(pages=pages):
                # Given fresh cached KSC rules; when checking either boundary.
                result = self.preflight(pages)
                # Then the cached range passes.
                self.assert_pages(result, pages, "PASS")

    def test_overflow_when_total_exceeds_maximum(self) -> None:
        # Given a maximum of three pages; when four pages are observed.
        result = self.preflight(4)
        # Then the cached range fails.
        self.assert_pages(result, 4, "FAIL")

    def test_maximum_only_when_cal_has_no_minimum(self) -> None:
        # Given the existing CAL maximum-only profile.
        self.profile = self.load_profile("cal-continuing-letter-submission.json")
        for pages, status in ((1, "PASS"), (4, "PASS"), (5, "FAIL")):
            with self.subTest(pages=pages):
                # When checking one, four, or five pages.
                result = self.preflight(pages)
                # Then the original maximum-only behavior is preserved.
                self.assert_pages(result, pages, status)

    def test_unknown_when_offline_stale_conflicting_or_main_only(self) -> None:
        for condition in ("offline", "stale", "conflicting", "main"):
            for pages in (1, 2, 4):
                with self.subTest(condition=condition, pages=pages):
                    # Given rules that cannot establish an applicable total-page range.
                    self.profile = self.load_profile("ksc-2026-research-submission.json")
                    rule = self.profile["rules"]["paper_length_policy"]
                    if condition == "stale":
                        rule["verified_at"] = "2020-01-01"
                    if condition == "conflicting":
                        rule["verification_status"] = "conflicting"
                    if condition == "main":
                        rule["value"]["basis"] = "main"
                    # When measuring below, within, or above the cached range.
                    result = self.preflight(pages, ("--offline",) if condition == "offline" else ())
                    # Then page observations cannot become policy certification.
                    self.assert_pages(result, pages, "UNKNOWN")

    def test_validation_when_minimum_is_invalid(self) -> None:
        for minimum in (True, False, 0, -1, 1.5, "2", None, [], {}, 4):
            with self.subTest(minimum=minimum):
                # Given a malformed or inverted minimum-page limit.
                self.profile["rules"]["paper_length_policy"]["value"]["min_pages"] = minimum
                self.write_package()
                # When validating the profile through the CLI trust boundary.
                result = subprocess.run(
                    [sys.executable, str(SKILL / "scripts/validate_profiles.py"), str(self.folder), "--json"],
                    capture_output=True, text=True, timeout=30, check=False,
                )
                # Then invalid minima are rejected as structured failures.
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertEqual(json.loads(result.stdout)["status"], "FAIL")

    def test_read_only_when_counting_pdf_pages(self) -> None:
        # Given a PDF whose source bytes must stay intact.
        before = self.pdf.read_bytes()
        # When the CLI inspects its page count.
        result = self.preflight(2)
        # Then the PDF remains byte-for-byte identical.
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.pdf.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
