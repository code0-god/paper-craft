#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
# How to run: python3 latex_integrity_check.py main.tex --json
"""Check a reachable LaTeX project without modifying manuscript files."""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Final

from manuscript_common import (
    LITERAL,
    Command,
    Finding,
    InputError,
    Project,
    all_commands,
    emit,
    issue,
    load_project,
    notice,
    resolve_path,
)

REFS: Final = frozenset({"ref", "eqref", "autoref", "cref", "Cref", "pageref",
                        "vref", "Vref", "cpageref", "Cpageref", "nameref", "subref",
                        "crefrange", "Crefrange"})


def static_check(project: Project) -> list[Finding]:
    """Check labels, references and graphic paths using static evidence only."""
    findings = list(project.findings)
    labels: dict[str, list[Command]] = defaultdict(list)
    parsed = all_commands(project)
    conditional = any(item["check"] == "conditional_commands" for item in project.findings)
    external = any(command.name == "externaldocument" for command in parsed)
    dynamic = any(command.name == "label" and not LITERAL.fullmatch(command.value)
                  for command in parsed)
    for command in parsed:
        if command.name == "label" and LITERAL.fullmatch(command.value):
            labels[command.value].append(command)
    for label, definitions in labels.items():
        if len(definitions) > 1:
            for command in definitions[1:]:
                message = f"Duplicate label {label}; first at {definitions[0].path}:{definitions[0].line}"
                findings.append(notice("duplicate_label", "Conditional label candidates: " + message) if conditional
                                else issue("duplicate_label", message, command))
    for command in parsed:
        if command.name not in REFS:
            continue
        if not LITERAL.fullmatch(command.value):
            findings.append(notice("reference", f"Dynamic reference at {command.path}:{command.line}"))
            continue
        for label in command.value.split(","):
            if label.strip() not in labels:
                if external or dynamic or project.findings:
                    findings.append(notice("reference", f"Cannot resolve {label.strip()} with incomplete/dynamic/external graph"))
                else:
                    findings.append(issue("unresolved_reference", f"Undefined label {label.strip()}", command))
    for file in project.files:
        for match in re.finditer(r"\\(?:crefrange|Crefrange)\s*\{[^{}]+\}\s*\{([^{}]+)\}", file.text):
            label = match.group(1)
            if label not in labels:
                at = Command("ref", label, file.path, file.text.count("\n", 0, match.start()) + 1, match.start())
                findings.append(notice("reference", f"Cannot resolve range end {label}") if external or dynamic or project.findings
                                else issue("unresolved_reference", f"Undefined range endpoint {label}", at))
        for match in re.finditer(r"\b(Figure|Fig\.|Table)\s*(?:~|\\(?:nobreakspace| )\s*)?\\(?:ref|cref|Cref|autoref)\{([^{}]+)\}", file.text):
            label = match.group(2)
            definitions = labels.get(label, [])
            if not definitions:
                continue
            source = next(item for item in project.files if item.path == definitions[0].path)
            stack: list[str] = []
            for token in re.finditer(r"\\(begin|end)\{([^{}]+)\}", source.text[:definitions[0].offset]):
                if token.group(1) == "begin":
                    stack.append(token.group(2).rstrip("*"))
                elif stack:
                    stack.pop()
            expected = "table" if match.group(1) == "Table" else "figure"
            actual = next((env for env in reversed(stack) if env in {"figure", "table"}), None)
            if actual and actual != expected:
                findings.append(issue("figure_table_reference", f"{match.group(1)} refers to {actual} label {label}", definitions[0]))
    graphic_dirs = [path for file in project.files for group in re.finditer(
        r"\\graphicspath\s*\{((?:\s*\{[^{}]*\})+)\s*\}", file.text)
        for path in re.findall(r"\{([^{}]*)\}", group.group(1))]
    for command in parsed:
        if command.name != "includegraphics":
            continue
        if not LITERAL.fullmatch(command.value):
            findings.append(notice("graphics_path", f"Dynamic graphics at {command.path}:{command.line}"))
            continue
        variants = [command, *(Command(command.name, directory + command.value, command.path,
                                      command.line, command.offset) for directory in graphic_dirs)]
        if not any(resolve_path(project, item, (".pdf", ".png", ".jpg", ".jpeg", ".eps", ".ps", ".mps", "")) for item in variants):
            findings.append(notice("graphics_path", f"Conditional graphics {command.value}; expansion required") if conditional
                            else issue("graphics_path", f"Missing or outside project: {command.value}", command))
    findings.append(notice("static_scope", f"Inspected {len(project.files)} reachable file(s); no TeX macro expansion", "PASS"))
    findings.append(notice("semantic_references", "Reference meaning, counter binding and visual placement need manual review", "UNKNOWN"))
    return findings


def build_check(project: Project) -> Finding:
    """Build only an opt-in private copy with rc files and shell escape disabled."""
    executable = shutil.which("latexmk")
    if not executable or not shutil.which("pdflatex"):
        return notice("latex_build", "latexmk/pdflatex unavailable; build not performed")
    with tempfile.TemporaryDirectory(prefix="paper-craft-build-") as folder:
        target = Path(folder) / "project"
        shutil.copytree(project.root, target, symlinks=True,
                        ignore=shutil.ignore_patterns(".git", ".omx", "__pycache__"))
        if any(path.is_symlink() for path in target.rglob("*")):
            return notice("latex_build", "Project contains symlinks; safe isolated build skipped")
        working = target / project.entry.parent.relative_to(project.root)
        # No latexmk rc evaluation; TeX reads/writes restricted to its private copy.
        environment = {"PATH": str(Path(executable).parent) + ":/usr/bin:/bin",
                       "openin_any": "p", "openout_any": "p", "MKTEXPK": "0", "MKTEXTFM": "0"}
        try:
            result = subprocess.run([executable, "-norc", "-pdf", "-no-shell-escape",
                                     "-interaction=nonstopmode", "-halt-on-error", project.entry.name],
                                    cwd=working, env=environment, capture_output=True, text=True, timeout=120)
        except (OSError, subprocess.TimeoutExpired) as exc:
            return notice("latex_build", f"Build did not finish: {exc}", "UNKNOWN")
        logs = result.stdout + result.stderr
        if result.returncode:
            return issue("latex_build", "Private-copy build failed: " + logs[-2000:])
        final_log = working / (project.entry.stem + ".log")
        if not final_log.is_file():
            return notice("latex_build", "Build exit was zero but final log is unavailable", "UNKNOWN")
        warnings = re.findall(r"(?:LaTeX|Package [^ ]+) Warning:[^\n]*", final_log.read_text(encoding="utf-8", errors="replace"))
        if warnings:
            return notice("latex_warnings", "Build completed; final-log warnings: " + "; ".join(warnings), "UNKNOWN")
        return notice("latex_build", "Private-copy pdflatex build completed without detected warnings", "PASS")


def pdf_check(path: Path) -> Finding:
    """Inspect a local PDF only when pdfinfo is installed."""
    if not path.is_file():
        raise InputError(f"PDF not found: {path}")
    executable = shutil.which("pdfinfo")
    if not executable:
        return notice("pdf_inspection", "pdfinfo unavailable; PDF pages not checked")
    try:
        result = subprocess.run([executable, str(path.resolve())], capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return notice("pdf_inspection", f"PDF inspection did not finish: {exc}", "UNKNOWN")
    return notice("pdf_inspection", result.stdout.strip(), "PASS") if result.returncode == 0 else issue("pdf_inspection", result.stderr.strip())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--project-root", type=Path)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--pdf", type=Path)
    parser.add_argument("--json", action="store_true", help="JSON output (also default)")
    args = parser.parse_args()
    try:
        project = load_project(args.root, args.project_root)
        findings = static_check(project)
        findings.append(build_check(project) if args.build else notice("latex_build", "Not requested; use --build for private-copy compilation"))
        findings.append(pdf_check(args.pdf) if args.pdf else notice("pdf_inspection", "No --pdf supplied; PDF inspection not performed"))
        return emit("latex_integrity_check", findings)
    except InputError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
