"""Observable CLI checks: static certainty, original preservation and safe extraction."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from symlink_support import symlink_or_skip

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / ".agents/skills/paper-craft/scripts"
FIXTURES = ROOT / "tests/fixtures"


class ManuscriptToolsTests(unittest.TestCase):
    def run_tool(self, tool: str, arguments: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, str(SCRIPTS / tool), *arguments, "--json"],
                              capture_output=True, text=True, timeout=30, check=False)

    def check_synthetic(self, text: str, tool: str) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "main.tex"
            path.write_text(text, encoding="utf-8")
            return self.run_tool(tool, [str(path)])

    def test_reachable_graph_when_unused_files_have_errors(self) -> None:
        # Given a root with a valid reachable file and an invalid unused file.
        path = FIXTURES / "latex/valid/main.tex"
        # When inspecting the selected root.
        result = self.run_tool("latex_integrity_check.py", [str(path)])
        # Then unused labels, refs and citations cannot cause static failures.
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("FAIL", [item["status"] for item in json.loads(result.stdout)["findings"]])

    def test_static_defects_when_labels_paths_and_types_break(self) -> None:
        # Given duplicate labels, missing refs and a Figure referring to a Table.
        path = FIXTURES / "latex/invalid.tex"
        # When checking the file.
        result = self.run_tool("latex_integrity_check.py", [str(path)])
        # Then each independently observable defect is reported.
        checks = {item["check"] for item in json.loads(result.stdout)["findings"] if item["status"] == "FAIL"}
        self.assertEqual(result.returncode, 1)
        self.assertTrue({"duplicate_label", "unresolved_reference", "graphics_path", "figure_table_reference"} <= checks)

    def test_reference_uncertainty_when_external_document_is_used(self) -> None:
        # Given an external-document label unavailable locally.
        text = r"\documentclass{article}\externaldocument{other}\ref{external:label}"
        # When statically checking without remote access.
        result = self.check_synthetic(text, "latex_integrity_check.py")
        # Then uncertainty is not a definite broken reference.
        self.assertEqual(result.returncode, 0)
        self.assertIn("SKIPPED", [item["status"] for item in json.loads(result.stdout)["findings"] if item["check"] == "reference"])

    def test_dynamic_paths_when_macro_expansion_is_needed(self) -> None:
        # Given a macro-based include and graphic path.
        text = r"\documentclass{article}\input{\sectionfile}\includegraphics{\plotfile}"
        # When checking without executing TeX.
        result = self.check_synthetic(text, "latex_integrity_check.py")
        # Then those checks are skipped rather than guessed.
        self.assertEqual(result.returncode, 0)
        self.assertTrue(all(item["status"] == "SKIPPED" for item in json.loads(result.stdout)["findings"] if item["check"] in {"include_graph", "graphics_path"}))

    def test_missing_include_when_literal_path_does_not_exist(self) -> None:
        # Given a literal missing input.
        text = r"\documentclass{article}\input{missing}"
        # When checking its graph.
        result = self.check_synthetic(text, "latex_integrity_check.py")
        # Then the literal path is a definite failure.
        self.assertEqual(result.returncode, 1)
        self.assertIn("include_path", [item["check"] for item in json.loads(result.stdout)["findings"]])

    def test_citation_variants_when_bibliography_is_available(self) -> None:
        # Given a real reachable local BibTeX fixture.
        path = FIXTURES / "latex/valid/main.tex"
        # When auditing keys.
        result = self.run_tool("reference_audit.py", [str(path)])
        # Then comments and verbatim citations do not fail the audit.
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("missing_citation_key", [item["check"] for item in json.loads(result.stdout)["findings"]])

    def test_missing_key_when_citation_has_two_optional_arguments(self) -> None:
        # Given a standard cite variant with an absent key.
        text = r"\documentclass{article}\citet[see][p. 3]{absent}"
        # When auditing it.
        result = self.check_synthetic(text, "reference_audit.py")
        # Then the absent key is reported at its command location.
        self.assertEqual(result.returncode, 1)
        self.assertIn("missing_citation_key", [item["check"] for item in json.loads(result.stdout)["findings"]])

    def test_duplicate_bib_keys_when_resources_share_entry(self) -> None:
        # Given two entries with one key.
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "main.tex"
            path.write_text(r"\documentclass{article}\bibliography{refs}\cite{x}", encoding="utf-8")
            (Path(folder) / "refs.bib").write_text("@misc{x,title={One}}\n@misc{x,title={Two}}", encoding="utf-8")
            # When auditing the resources.
            result = self.run_tool("reference_audit.py", [str(path)])
        # Then duplicate keys fail even when every citation resolves.
        self.assertEqual(result.returncode, 1)
        self.assertIn("duplicate_bib_key", [item["check"] for item in json.loads(result.stdout)["findings"]])

    def test_unavailable_build_when_build_not_requested(self) -> None:
        # Given a valid manuscript.
        path = FIXTURES / "latex/valid/main.tex"
        # When using the default read-only CLI.
        result = self.run_tool("latex_integrity_check.py", [str(path)])
        # Then compilation is explicitly unperformed.
        findings = json.loads(result.stdout)["findings"]
        self.assertEqual([item["status"] for item in findings if item["check"] == "latex_build"], ["SKIPPED"])

    def test_original_bytes_when_all_read_only_tools_run(self) -> None:
        # Given original source bytes.
        path = FIXTURES / "latex/valid/main.tex"
        before = hashlib.sha256(path.read_bytes()).digest()
        # When the CLI inspects the manuscript.
        result = self.run_tool("latex_integrity_check.py", [str(path)])
        # Then input remains byte-identical.
        self.assertEqual(result.returncode, 0)
        self.assertEqual(hashlib.sha256(path.read_bytes()).digest(), before)

    def test_protected_changes_when_numeric_units_and_math_change(self) -> None:
        # Given original and an unsafe proposal.
        with tempfile.TemporaryDirectory() as folder:
            original, revised = Path(folder) / "old.tex", Path(folder) / "new.tex"
            original.write_text(r"Latency 10 ns \cite{a}. $x+2$ \label{a}", encoding="utf-8")
            revised.write_text(r"Latency 11 ms \cite{b}. $x+3$ \label{b}", encoding="utf-8")
            # When comparing protected content.
            result = self.run_tool("editing_guard.py", [str(original), str(revised)])
        # Then altered numbers, units, keys, labels and formulas fail.
        report = json.loads(result.stdout)
        self.assertEqual(result.returncode, 1)
        self.assertTrue({"numeric_tokens", "unit_tokens", "citation_keys", "labels", "math_expressions"} <= {item["check"] for item in report["findings"] if item["status"] == "FAIL"})
        self.assertTrue(report["unified_diff"].startswith("--- "))

    def test_semantic_review_when_english_or_korean_text_is_edited(self) -> None:
        # Given proposals preserving technical tokens in either language.
        for before, after in [(r"Our result is 10 ns \cite{a}.", r"Latency is 10 ns \cite{a}."),
                              ("결과 지연은 10 ns.", "측정 지연은 10 ns.")]:
            with self.subTest(language=before), tempfile.TemporaryDirectory() as folder:
                original, revised = Path(folder) / "old.tex", Path(folder) / "new.tex"
                original.write_text(before, encoding="utf-8")
                revised.write_text(after, encoding="utf-8")
                # When guarding an ordinary language change.
                result = self.run_tool("editing_guard.py", [str(original), str(revised)])
                # Then token checks pass but meaning remains manual.
                report = json.loads(result.stdout)
                self.assertEqual(result.returncode, 0)
                self.assertEqual(report["semantic_review"], "MANUAL_REQUIRED")
                self.assertEqual(report["status"], "UNKNOWN")

    def test_static_extraction_when_html_contains_active_content(self) -> None:
        # Given HTML with scripts, styles and a template.
        path = FIXTURES / "materials/inert.html"
        # When extracting local blocks.
        result = self.run_tool("source_material.py", ["inspect", str(path), "--source-id", "B"])
        # Then only inert source blocks with positions and hash are emitted.
        report = json.loads(result.stdout)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(report["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())
        self.assertTrue(all(block["provenance"] == "source_text" and block["line"] > 0 for block in report["blocks"]))
        self.assertFalse({"script", "style", "template"} & {block["tag"] for block in report["blocks"]})
        self.assertEqual(report["blocks"][0]["anchor"], "argument")

    def test_usage_error_when_input_is_missing(self) -> None:
        # Given a nonexistent input.
        path = FIXTURES / "absent.tex"
        # When checking it.
        result = self.run_tool("latex_integrity_check.py", [str(path)])
        # Then usage/input errors remain separate from manuscript failures.
        self.assertEqual(result.returncode, 2)

    def test_project_boundary_when_input_traverses_parent(self) -> None:
        # Given an existing file outside the permitted project root.
        with tempfile.TemporaryDirectory() as folder:
            project = Path(folder) / "project"
            project.mkdir()
            (Path(folder) / "private.tex").write_text(r"\label{private}", encoding="utf-8")
            main = project / "main.tex"
            main.write_text(r"\documentclass{article}\input{../private}", encoding="utf-8")
            # When following the input graph.
            result = self.run_tool("latex_integrity_check.py", [str(main)])
        # Then outside data is not read into the graph.
        report = json.loads(result.stdout)
        self.assertEqual(result.returncode, 1)
        self.assertIn("include_path", [item["check"] for item in report["findings"]])

    def test_project_boundary_when_input_symlink_escapes_root(self) -> None:
        # Given a symlink targeting an outside source.
        with tempfile.TemporaryDirectory() as folder:
            project = Path(folder) / "project"
            project.mkdir()
            private = Path(folder) / "private.tex"
            private.write_text(r"\label{private}", encoding="utf-8")
            symlink_or_skip(project / "linked.tex", private)
            main = project / "main.tex"
            main.write_text(r"\documentclass{article}\input{linked}", encoding="utf-8")
            # When following the symlinked input.
            result = self.run_tool("latex_integrity_check.py", [str(main)])
        # Then boundary failure is visible without reading the target.
        self.assertEqual(result.returncode, 1)
        self.assertIn("include_path", [item["check"] for item in json.loads(result.stdout)["findings"]])

    def test_macro_body_when_labels_are_not_yet_instantiated(self) -> None:
        # Given macro definitions containing literal labels.
        text = r"\documentclass{article}\newcommand{\foo}{\label{x}}\newcommand{\bar}{\label{x}}\ref{x}"
        # When static analysis does not execute macros.
        result = self.check_synthetic(text, "latex_integrity_check.py")
        # Then unevaluated definitions do not create duplicate-label failures.
        self.assertEqual(result.returncode, 0)
        self.assertIn("macro_expansion", [item["check"] for item in json.loads(result.stdout)["findings"]])

    def test_void_tags_when_noscript_contains_external_image(self) -> None:
        # Given inert and visible void tags in one local document.
        path = FIXTURES / "materials/inert.html"
        # When extracting blocks.
        result = self.run_tool("source_material.py", ["inspect", str(path), "--source-id", "B"])
        # Then fallback content stays excluded and visible anchors survive.
        report = json.loads(result.stdout)
        self.assertFalse({"noscript", "script", "template", "style"} & {block["tag"] for block in report["blocks"]})
        self.assertIn("void-safe", [block["anchor"] for block in report["blocks"]])

    def test_percent_when_plaintext_result_is_modified(self) -> None:
        # Given plaintext percentages (not LaTeX comments).
        with tempfile.TemporaryDirectory() as folder:
            original, revised = Path(folder) / "old.txt", Path(folder) / "new.txt"
            original.write_text("Accuracy 95% at 1 GHz.", encoding="utf-8")
            revised.write_text("Accuracy 95 at 1 GHz.", encoding="utf-8")
            # When guarding a proposal that removes the unit.
            result = self.run_tool("editing_guard.py", [str(original), str(revised)])
        # Then percent removal is detected.
        self.assertEqual(result.returncode, 1)
        self.assertIn("unit_tokens", [item["check"] for item in json.loads(result.stdout)["findings"] if item["status"] == "FAIL"])

    def test_uncertainty_when_conditional_branches_repeat_label(self) -> None:
        # Given mutually exclusive labels and an unreachable missing input.
        text = r"\documentclass{article}\iftrue\label{x}\else\label{x}\input{absent}\fi"
        # When static checking cannot evaluate conditionals.
        result = self.check_synthetic(text, "latex_integrity_check.py")
        # Then branch candidates remain uncertainty rather than definite failures.
        self.assertEqual(result.returncode, 0)
        self.assertNotIn("FAIL", [item["status"] for item in json.loads(result.stdout)["findings"]])

    def test_uncertainty_when_multi_citation_has_extra_argument_groups(self) -> None:
        # Given biblatex multicite syntax requiring additional argument parsing.
        text = r"\documentclass{article}\parencites{one}{two}"
        # When using the supported static citation subset.
        result = self.check_synthetic(text, "reference_audit.py")
        # Then unsupported groups are explicitly skipped.
        self.assertEqual(result.returncode, 0)
        self.assertEqual([item["status"] for item in json.loads(result.stdout)["findings"] if item["check"] == "multi_citation"], ["SKIPPED"])


if __name__ == "__main__":
    unittest.main()
