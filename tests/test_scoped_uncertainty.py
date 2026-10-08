"""CLI regressions for uncertainty scoped to symbol producers and consumers."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / ".agents/skills/paper-craft/scripts"


class ScopedUncertaintyTests(unittest.TestCase):
    def check_case(self, name: str, tool: str, files: dict[str, str],
                   expected: dict[str, list[str]]) -> None:
        # Given a self-contained source graph and its original byte hashes.
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for filename, text in files.items():
                (root / filename).write_text(text, encoding="utf-8")
            before = {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in files}
            invocation = [sys.executable, str(SCRIPTS / tool), str(root / "main.tex"), "--json"]
            # When invoking the actual public CLI without --build.
            result = subprocess.run(invocation, capture_output=True, text=True, timeout=30, check=False)
            after = {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in files}
        report = json.loads(result.stdout)
        if destination := os.environ.get("SCOPED_TEX_EVIDENCE"):
            artifact = Path(destination) / f"{name}.json"
            artifact.parent.mkdir(parents=True, exist_ok=True)
            artifact.write_text(json.dumps({"invocation": invocation, "files": files,
                                           "before_sha256": before, "after_sha256": after,
                                           "exit_code": result.returncode, "stdout": report,
                                           "stderr": result.stderr, "expected": expected}, indent=2),
                                encoding="utf-8")
        # Then each relevant finding and exit code match, and every input is unchanged.
        self.assertEqual(before, after)
        self.assertEqual(set(report), {"tool", "status", "findings"})
        self.assertEqual(result.returncode, int(any(item["status"] == "FAIL" for item in report["findings"])))
        for check, statuses in expected.items():
            self.assertEqual([item["status"] for item in report["findings"] if item["check"] == check],
                             statuses, result.stdout)

    def test_labels_when_uncertainty_has_a_specific_scope(self) -> None:
        cases = [
            ("term", r"\newcommand{\myterm}{PoTal}\ref{fig:missing}", ["FAIL"], []),
            ("cite_macro", r"\newcommand{\mycite}{\cite{key}}\ref{missing}", ["FAIL"], []),
            ("graphics_macro", r"\newcommand{\plot}{\includegraphics{\file}}\ref{missing}", ["FAIL"], []),
            ("condition_text", r"\iftrue text\else other\fi\ref{missing}", ["FAIL"], []),
            ("dynamic_graphics", r"\includegraphics{\file}\ref{missing}", ["FAIL"], []),
            ("dynamic_ref", r"\ref{\name}\ref{missing}", ["FAIL"], ["SKIPPED"]),
            ("braced_condition_text", r"\ifthenelse{test}{text}{other}\ref{missing}", ["FAIL"], []),
            ("braced_conditional_label", r"\IfFileExists{path}{\label{foo}}{}\ref{foo}\ref{bar}", ["FAIL"], ["SKIPPED"]),
            ("newif_text", r"\newif\ifdraft\ifdraft text\fi\ref{missing}", ["FAIL"], []),
            ("escaped_range", r"\\crefrange{a}{b}", [], []),
            ("conditional_ref", r"\iftrue\ref{missing}\fi", [], ["SKIPPED"]),
            ("conditional_label", r"\iftrue\label{foo}\fi\ref{foo}\ref{bar}", ["FAIL"], ["SKIPPED"]),
            ("constant_macro", r"\newcommand{\mk}{\label{foo}}\ref{foo}\ref{bar}", ["FAIL"], ["SKIPPED"]),
            ("macro_chain", r"\newcommand{\mk}{\other}\def\other{\label{foo}}\ref{foo}\ref{bar}", ["FAIL"], ["SKIPPED"]),
            ("parameter_macro", r"\newcommand{\mk}[1]{\label{#1}}\ref{foo}", [], ["SKIPPED"]),
            ("bare_macro", r"\newcommand{\mk}{\label}\mk{foo}\ref{foo}", [], ["SKIPPED"]),
            ("dynamic_label", r"\label{\name}\ref{foo}", [], ["SKIPPED"]),
            ("external", r"\externaldocument{other}\ref{foo}", [], ["SKIPPED"]),
            ("dynamic_input", r"\input{\name}\ref{foo}", [], ["SKIPPED"]),
            ("missing_input", r"\input{missing}\ref{foo}", [], ["SKIPPED"]),
            ("macro_input", r"\newcommand{\mk}{\input{other}}\ref{foo}", [], ["SKIPPED"]),
            ("includeonly_empty", r"\includeonly{}\include{missing}\ref{foo}", [], ["SKIPPED"]),
            ("range_term", r"\newcommand{\term}{PoTal}\label{a}\crefrange{a}{b}", ["FAIL"], []),
            ("conditional_range", r"\label{a}\iftrue\crefrange{a}{b}\fi", [], ["SKIPPED"]),
        ]
        for name, text, failures, skipped in cases:
            with self.subTest(case=name):
                self.check_case("labels_" + name, "latex_integrity_check.py", {"main.tex": text},
                                {"unresolved_reference": failures, "reference": skipped})

    def test_citations_when_uncertainty_has_a_specific_scope(self) -> None:
        cases = [
            ("term", r"\newcommand{\myterm}{PoTal}\cite{key}", ["FAIL"], []),
            ("cite_macro", r"\newcommand{\mycite}[1]{\cite{#1}}\cite{key}", ["FAIL"], []),
            ("label_macro", r"\newcommand{\mk}[1]{\label{#1}}\cite{key}", ["FAIL"], []),
            ("condition_text", r"\iftrue text\fi\cite{key}", ["FAIL"], []),
            ("dynamic_cite", r"\cite{\key}\cite{missing}", ["FAIL"], ["SKIPPED"]),
            ("conditional_cite", r"\iftrue\cite{key}\fi", [], ["SKIPPED"]),
            ("constant_bibitem", r"\newcommand{\mk}{\bibitem{foo}}\cite{foo,bar}", ["FAIL"], ["SKIPPED"]),
            ("conditional_bibitem", r"\iftrue\bibitem{foo}\fi\cite{foo,bar}", ["FAIL"], ["SKIPPED"]),
            ("dynamic_bibitem", r"\bibitem{\key}\cite{foo}", [], ["SKIPPED", "SKIPPED"]),
            ("macro_bibitem", r"\newcommand{\mk}[1]{\bibitem{#1}}\cite{foo}", [], ["SKIPPED"]),
            ("macro_resource", r"\newcommand{\mk}{\bibliography{other}}\cite{foo}", [], ["SKIPPED"]),
            ("macro_resource_subset", r"\newcommand{\mk}{\bibliography{other}}\cite{foo,bar}", ["FAIL"], ["SKIPPED"]),
            ("conditional_resource", r"\iftrue\bibliography{other}\fi\cite{foo,bar}", ["FAIL"], ["SKIPPED"]),
            ("dynamic_resource", r"\bibliography{\file}\cite{foo}", [], ["SKIPPED"]),
            ("missing_input", r"\input{missing}\cite{foo}", [], ["SKIPPED"]),
            ("external_labels", r"\externaldocument{other}\cite{key}", ["FAIL"], []),
        ]
        for name, text, failures, skipped in cases:
            with self.subTest(case=name):
                files = {"main.tex": r"\bibliography{refs}" + text,
                         "refs.bib": "@misc{known,title={Known}}", "other.bib": "@misc{foo,title={Other}}"}
                self.check_case("cites_" + name, "reference_audit.py", files,
                                {"missing_citation_key": failures, "citation_key": skipped})

    def test_duplicates_when_only_some_definitions_are_conditional(self) -> None:
        for tool, definition, check in [("latex_integrity_check.py", "label", "duplicate_label"),
                                        ("reference_audit.py", "bibitem", "duplicate_bib_key")]:
            with self.subTest(tool=tool):
                text = rf"\iftrue\{definition}{{a}}\else\{definition}{{a}}\fi\{definition}{{b}}\{definition}{{b}}"
                self.check_case("duplicates_" + definition, tool, {"main.tex": text},
                                {check: ["SKIPPED", "FAIL"]})

    def test_included_candidates_when_reachability_is_conditional(self) -> None:
        for tool, definition, reference, missing, skipped in [
            ("latex_integrity_check.py", "label", "ref", "unresolved_reference", "reference"),
            ("reference_audit.py", "bibitem", "cite", "missing_citation_key", "citation_key"),
        ]:
            with self.subTest(tool=tool):
                files = {"main.tex": rf"\iftrue\input{{child}}\fi\{reference}{{foo}}\{reference}{{bar}}",
                         "child.tex": rf"\{definition}{{foo}}"}
                self.check_case("include_" + definition, tool, files,
                                {missing: ["FAIL"], skipped: ["SKIPPED"]})
                files["main.tex"] = rf"\newcommand{{\load}}{{\input{{child}}}}\{reference}{{foo}}\{reference}{{bar}}"
                self.check_case("macro_include_" + definition, tool, files,
                                {missing: ["FAIL"], skipped: ["SKIPPED"]})

    def test_excluded_includes_can_restore_cached_auxiliary_symbols(self) -> None:
        for tool, definition, reference, missing, skipped in [
            ("latex_integrity_check.py", "label", "ref", "unresolved_reference", "reference"),
            ("reference_audit.py", "bibitem", "cite", "missing_citation_key", "citation_key"),
        ]:
            with self.subTest(tool=tool):
                files = {"main.tex": rf"\includeonly{{}}\include{{child}}\{reference}{{foo}}",
                         "child.tex": rf"\{definition}{{foo}}"}
                self.check_case("excluded_aux_" + definition, tool, files,
                                {missing: [], skipped: ["SKIPPED"]})


if __name__ == "__main__":
    unittest.main()
