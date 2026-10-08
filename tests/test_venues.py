"""Exercise exact venue selection, provenance boundaries and CLI uncertainty."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents/skills/paper-craft"
SCRIPTS = SKILL / "scripts"
VENUES = SKILL / "venues"
MAIN = ROOT / "tests/fixtures/latex/valid/main.tex"
ASPlOS = r"\documentclass[sigplan,anonymous,review,nonacm]{acmart}\begin{document}Text.\end{document}"


class VenueTests(unittest.TestCase):
    def run_tool(self, tool: str, arguments: list[str], environment: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, str(SCRIPTS / tool), *arguments, "--json"],
                              capture_output=True, text=True, timeout=30, check=False,
                              env=environment)

    def preflight(self, extra: list[str], manuscript: Path = MAIN) -> subprocess.CompletedProcess[str]:
        return self.run_tool("venue_preflight.py", [str(manuscript), *extra])

    def package(self, folder: str, profile: dict) -> Path:
        path = Path(folder) / "venues"
        path.mkdir()
        (path / "profile.json").write_text(json.dumps(profile), encoding="utf-8")
        entry = {"venue_id": "ASPLOS", "publication_type": "conference",
                 "official_domains": ["asplos-conference.org", "acm.org"], "profiles": ["profile.json"]}
        (path / "registry.json").write_text(json.dumps({"schema_version": 1, "venues": [entry]}), encoding="utf-8")
        return path

    def profile(self) -> dict:
        profile = json.loads((VENUES / "profiles/asplos-2027-research-submission.json").read_text(encoding="utf-8"))
        profile["last_verified_date"] = date.today().isoformat()
        for rule in profile["rules"].values():
            if rule["verification_status"] == "verified":
                rule["verified_at"] = date.today().isoformat()
        return profile

    def test_registry_when_all_supported_targets_are_packaged(self) -> None:
        # Given the real shipped venue package.
        expected = {"ISCA", "MICRO", "HPCA", "ASPLOS", "PACT", "SOSP", "OSDI", "EUROSYS", "ATC", "NSDI", "MLSYS", "CAL", "TC", "TACO", "TOCS", "TPDS", "KSC", "DAC"}
        # When validating its CLI surface.
        result = self.run_tool("validate_profiles.py", [])
        # Then all identities and scoped metadata pass package validation.
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["profile_count"], 23)
        self.assertEqual({entry["venue_id"] for entry in json.loads((VENUES / "registry.json").read_text())["venues"]}, expected)

    def test_exact_year_when_future_edition_has_no_profile(self) -> None:
        # Given an ISCA edition without cached rules.
        # When requesting that exact edition.
        result = self.preflight(["--venue", "ISCA", "--year", "2027", "--track", "research"])
        # Then no prior-year profile is selected.
        report = json.loads(result.stdout)
        self.assertEqual(result.returncode, 0)
        self.assertIsNone(report["profile"])
        self.assertEqual(report["status"], "UNKNOWN")

    def test_ksc_general_paper_when_submission_and_final_rules_differ(self) -> None:
        for stage, template in (("submission", "DocForm_1.docx"), ("camera-ready", "DocForm_2.docx")):
            with self.subTest(stage=stage):
                result = self.preflight(["--venue", "KSC", "--year", "2026", "--track", "research", "--stage", stage, "--offline"])
                self.assertEqual(result.returncode, 0, result.stderr)
                report = json.loads(result.stdout)
                rules = report["profile"]["rules"]
                self.assertTrue(rules["template_requirements"]["value"]["template_url"].endswith(template))
                self.assertIsNone(rules["ai_disclosure_requirements"]["value"])
                self.assertIsNone(rules["reference_page_policy"]["value"])
                self.assertEqual(report["submission_compliance"], "UNKNOWN")
                if stage == "submission":
                    self.assertEqual(rules["paper_length_policy"]["value"], {"min_pages": 2, "max_pages": 3, "basis": "all"})
                    self.assertIsNone(rules["anonymity_requirements"]["value"]["double_blind"])
                    self.assertEqual(rules["anonymity_requirements"]["verification_status"], "verified")
                else:
                    self.assertIsNone(rules["paper_length_policy"]["value"])
                    self.assertFalse(rules["anonymity_requirements"]["value"]["double_blind"])

    def test_dac_when_edition_and_stage_select_distinct_instructions(self) -> None:
        for year, stage, family in ((2026, "submission", "ACM"), (2026, "camera-ready", "ACM"), (2027, "submission", "IEEE")):
            with self.subTest(year=year, stage=stage):
                result = self.preflight(["--venue", "DAC", "--year", str(year), "--track", "research", "--stage", stage, "--offline"])
                self.assertEqual(result.returncode, 0, result.stderr)
                rules = json.loads(result.stdout)["profile"]["rules"]
                self.assertEqual(rules["paper_length_policy"]["value"], {"max_pages": 6, "basis": "main"})
                self.assertEqual(rules["reference_page_policy"]["value"]["limit"], 1)
                self.assertEqual(rules["template_requirements"]["value"]["template_family"], family)
                self.assertEqual(rules["template_requirements"]["value"]["allowed_font_sizes_pt"], [9, 10])
                self.assertEqual(rules["anonymity_requirements"]["value"]["double_blind"], stage == "submission")
                if stage == "submission":
                    self.assertFalse(rules["ai_disclosure_requirements"]["value"]["prohibited_generation"])
                    self.assertEqual(rules["ai_disclosure_requirements"]["verification_status"], "verified")

    def test_new_venues_when_uncached_context_must_not_borrow_rules(self) -> None:
        for venue, year, track, stage in (("KCC", 2026, "research", "submission"), ("KSC", 2025, "research", "submission"), ("KSC", 2026, "undergraduate", "submission"), ("DAC", 2027, "engineering", "submission"), ("DAC", 2027, "research", "camera-ready"), ("DAC", 2028, "research", "submission")):
            with self.subTest(venue=venue, year=year, track=track, stage=stage):
                result = self.preflight(["--venue", venue, "--year", str(year), "--track", track, "--stage", stage])
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIsNone(json.loads(result.stdout)["profile"])

    def test_exact_track_when_industry_rules_are_absent(self) -> None:
        # Given research-only ISCA instructions.
        # When requesting industry-track review.
        result = self.preflight(["--venue", "ISCA", "--year", "2026", "--track", "industry"])
        # Then research rules cannot leak into the industry target.
        self.assertIsNone(json.loads(result.stdout)["profile"])

    def test_stage_when_camera_ready_has_separate_limit(self) -> None:
        # Given an ISCA camera-ready target.
        # When selecting its exact stage.
        result = self.preflight(["--venue", "ISCA", "--year", "2026", "--track", "research", "--stage", "camera-ready"])
        # Then the recorded final-paper rule is 13, not submission's 11.
        profile = json.loads(result.stdout)["profile"]
        self.assertEqual(profile["rules"]["paper_length_policy"]["value"]["max_pages"], 13)
        self.assertEqual(profile["submission_stage"], "camera-ready")

    def test_track_when_operational_contribution_is_selected(self) -> None:
        # Given OSDI's operational systems track.
        # When selecting the operational tuple.
        result = self.preflight(["--venue", "OSDI", "--year", "2026", "--track", "operational-systems"])
        # Then deployment lessons, not mandatory algorithm novelty, guide review.
        profile = json.loads(result.stdout)["profile"]
        self.assertEqual(profile["track"], "operational-systems")
        self.assertIn("Operational", profile["rules"]["review_criteria"]["value"][0])

    def test_journal_when_year_is_explicitly_continuing(self) -> None:
        # Given a continuing CAL letter profile.
        # When year is omitted.
        result = self.preflight(["--venue", "CAL", "--track", "letter"])
        # Then a null-year letter is selected without inventing a conference edition.
        profile = json.loads(result.stdout)["profile"]
        self.assertIsNone(profile["year"])
        self.assertEqual(profile["rules"]["paper_length_policy"]["value"], {"max_pages": 4, "basis": "all"})

    def test_offline_when_historical_sources_are_verified(self) -> None:
        # Given verified historical rules and no live access.
        # When running offline.
        result = self.preflight(["--venue", "ISCA", "--year", "2026", "--track", "research", "--offline"])
        # Then historical provenance remains, but current applicability is UNKNOWN.
        report = json.loads(result.stdout)
        rule = next(item for item in report["findings"] if item["check"] == "paper_length_policy")
        self.assertEqual(rule["provenance_status"], "verified")
        self.assertEqual(rule["cached_applicability"], "UNKNOWN")
        self.assertFalse(report["current_rules_verified"])
        self.assertEqual(report["submission_compliance"], "UNKNOWN")

    def test_unknown_when_official_journal_rules_unavailable(self) -> None:
        # Given inaccessible TOCS author instructions.
        # When selecting its supported continuing profile.
        result = self.preflight(["--venue", "TOCS", "--track", "regular"])
        # Then official formatting facts remain null and unverified.
        rule = json.loads(result.stdout)["profile"]["rules"]["paper_length_policy"]
        self.assertIsNone(rule["value"])
        self.assertEqual(rule["verification_status"], "unverified")

    def test_template_when_literal_required_options_match(self) -> None:
        # Given a valid literal ASPLOS class declaration.
        with tempfile.TemporaryDirectory() as folder:
            package = self.package(folder, self.profile())
            path = Path(folder) / "main.tex"
            path.write_text(ASPlOS, encoding="utf-8")
            # When checking literal cached settings.
            result = self.preflight(["--venue", "ASPLOS", "--year", "2027", "--track", "research", "--profile-root", str(package)], path)
        # Then that static comparison passes, but overall compliance remains UNKNOWN.
        report = json.loads(result.stdout)
        self.assertEqual(next(item["status"] for item in report["findings"] if item["check"] == "template_setting"), "PASS")
        self.assertEqual(report["status"], "UNKNOWN")

    def test_template_when_required_options_missing(self) -> None:
        # Given an article class in a named ASPLOS submission.
        with tempfile.TemporaryDirectory() as folder:
            package = self.package(folder, self.profile())
            path = Path(folder) / "main.tex"
            path.write_text(r"\documentclass{article}", encoding="utf-8")
            # When comparing with exact fresh cached settings.
            result = self.preflight(["--venue", "ASPLOS", "--year", "2027", "--track", "research", "--profile-root", str(package)], path)
        # Then the cached literal mismatch is a reported failure.
        self.assertEqual(result.returncode, 1)
        self.assertEqual(next(item["status"] for item in json.loads(result.stdout)["findings"] if item["check"] == "template_setting"), "FAIL")

    def test_template_when_required_flags_have_conflicting_false_values(self) -> None:
        # Given lexical required flags overridden by explicit false values.
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "main.tex"
            path.write_text(r"\documentclass[sigplan,anonymous,review,nonacm,anonymous=false,review=false]{acmart}", encoding="utf-8")
            # When inspecting against the real default cache with online mode.
            result = self.preflight(["--venue", "ASPLOS", "--year", "2027", "--track", "research"], path)
        # Then subset membership cannot incorrectly certify active required flags.
        item = next(item for item in json.loads(result.stdout)["findings"] if item["check"] == "template_setting")
        self.assertIn(item["status"], {"FAIL", "UNKNOWN"})
        self.assertIn("explicit value", item["message"])

    def test_stale_rules_when_verification_date_is_old(self) -> None:
        # Given structurally valid but old cached rules and mismatching class.
        profile = self.profile()
        profile["last_verified_date"] = "2020-01-01"
        for rule in profile["rules"].values():
            if rule["verification_status"] == "verified":
                rule["verified_at"] = "2020-01-01"
        with tempfile.TemporaryDirectory() as folder:
            package = self.package(folder, profile)
            path = Path(folder) / "main.tex"
            path.write_text(r"\documentclass{article}", encoding="utf-8")
            # When checking the old profile.
            result = self.preflight(["--venue", "ASPLOS", "--year", "2027", "--track", "research", "--profile-root", str(package)], path)
        # Then stale settings cannot become definite current-policy violations.
        self.assertEqual(result.returncode, 0)
        self.assertEqual(next(item["status"] for item in json.loads(result.stdout)["findings"] if item["check"] == "template_setting"), "UNKNOWN")

    def test_profile_validation_when_provenance_fields_are_invalid(self) -> None:
        # Given invalid metadata variants at the JSON trust boundary.
        variants = [
            ("source_url", "https://www.asplos-conference.org.attacker.test/cfp/"),
            ("source_type", "field_methodology"), ("source_type", "unknown"),
            ("verified_at", "2999-01-01"), ("verified_at", None),
            ("verification_status", []), ("applies_to", {"venue_id": "MICRO"}),
        ]
        for field, value in variants:
            with self.subTest(field=field, value=value), tempfile.TemporaryDirectory() as folder:
                profile = self.profile()
                profile["rules"]["paper_length_policy"][field] = value
                package = self.package(folder, profile)
                # When validating each malformed profile via CLI.
                result = self.run_tool("validate_profiles.py", [str(package)])
                # Then it produces a structured failure, not a crash or PASS.
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertEqual(json.loads(result.stdout)["status"], "FAIL")

    def test_unknown_source_when_unverified_value_is_asserted(self) -> None:
        # Given an asserted page limit with no checked source.
        with tempfile.TemporaryDirectory() as folder:
            profile = self.profile()
            rule = profile["rules"]["paper_length_policy"]
            rule.update(verification_status="unverified", source_type="unknown", source_url=None, verified_at=None)
            package = self.package(folder, profile)
            # When validating provenance.
            result = self.run_tool("validate_profiles.py", [str(package)])
        # Then UNKNOWN cannot smuggle an asserted official requirement.
        self.assertEqual(result.returncode, 1)

    def test_identity_when_registry_points_to_another_venue(self) -> None:
        # Given a registry entry whose profile identity has been replaced.
        with tempfile.TemporaryDirectory() as folder:
            profile = self.profile()
            profile["venue_id"] = "MICRO"
            for rule in profile["rules"].values():
                rule["applies_to"]["venue_id"] = "MICRO"
            package = self.package(folder, profile)
            # When requesting the registry's advertised venue.
            result = self.preflight(["--venue", "ASPLOS", "--year", "2027", "--track", "research", "--profile-root", str(package)])
        # Then the mismatched profile is rejected, not returned as ASPLOS.
        self.assertEqual(result.returncode, 1)
        self.assertIsNone(json.loads(result.stdout)["profile"])

    def test_path_boundary_when_registry_symlink_escapes(self) -> None:
        # Given a profile symlink outside the package.
        with tempfile.TemporaryDirectory() as folder:
            package = self.package(folder, self.profile())
            outside = Path(folder) / "outside.json"
            outside.write_text((package / "profile.json").read_text(), encoding="utf-8")
            (package / "profile.json").unlink()
            (package / "profile.json").symlink_to(outside)
            # When loading registry paths.
            result = self.run_tool("validate_profiles.py", [str(package)])
        # Then path escape is detected before reading an external profile.
        self.assertEqual(result.returncode, 1)

    def test_comments_and_unused_files_when_literal_template_is_checked(self) -> None:
        # Given a decoy class in comments and an unused external-looking TeX file.
        with tempfile.TemporaryDirectory() as folder:
            package = self.package(folder, self.profile())
            path = Path(folder) / "main.tex"
            path.write_text("% \\documentclass{article}\n" + ASPlOS, encoding="utf-8")
            (Path(folder) / "unused.tex").write_text(r"\documentclass{article}", encoding="utf-8")
            before = path.read_bytes()
            # When checking the selected root.
            result = self.preflight(["--venue", "ASPLOS", "--year", "2027", "--track", "research", "--profile-root", str(package)], path)
            after = path.read_bytes()
        # Then unused content cannot affect template compliance or modify manuscript.
        self.assertEqual(result.returncode, 0)
        self.assertEqual(before, after)

    def test_optional_pdf_tool_when_pdfinfo_not_on_path(self) -> None:
        # Given a PDF path with the optional executable unavailable.
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "paper.pdf"
            path.write_bytes(b"%PDF-1.4\n")
            environment = dict(os.environ, PATH="")
            # When checking optional PDF support.
            result = self.run_tool("venue_preflight.py", [str(MAIN), "--venue", "CAL", "--track", "letter", "--pdf", str(path)], environment)
        # Then the unperformed check is SKIPPED with its dependency reason.
        item = next(item for item in json.loads(result.stdout)["findings"] if item["check"] == "pdf_page_count")
        self.assertEqual(item["status"], "SKIPPED")
        self.assertIn("pdfinfo", item["message"])

    def test_input_when_manuscript_path_missing(self) -> None:
        # Given a nonexistent input path.
        with tempfile.TemporaryDirectory() as folder:
            # When running preflight.
            result = self.preflight(["--venue", "ISCA", "--year", "2026", "--track", "research"], Path(folder) / "missing.tex")
        # Then input usage fails with JSON rather than certification.
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["status"], "FAIL")

    def test_ai_policy_when_drafting_restriction_differs_from_disclosure(self) -> None:
        # Given shipped NSDI and OSDI AI policies.
        profiles = [json.loads((VENUES / f"profiles/{venue}-research-submission.json").read_text()) for venue in ("nsdi-2027", "osdi-2026")]
        # When inspecting policy action fields.
        policies = [profile["rules"]["ai_disclosure_requirements"]["value"] for profile in profiles]
        # Then generation restrictions stay separate from disclosure/attestation.
        self.assertTrue(all(policy["prohibited_generation"] for policy in policies))
        self.assertIsNone(policies[1]["disclosure"])
        self.assertIn("attestation", policies[0]["disclosure"])


if __name__ == "__main__":
    unittest.main()
