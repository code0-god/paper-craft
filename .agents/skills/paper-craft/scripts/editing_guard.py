#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
# How to run: python3 editing_guard.py original.tex proposed.tex --json
"""Produce a read-only diff and flag protected manuscript token changes."""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Final, TypedDict

from manuscript_common import (
    Finding,
    InputError,
    Status,
    commands,
    issue,
    mask_tex,
    notice,
    read_text,
)
from reference_audit import BIB_ENTRY, CITES

NUMBER: Final = re.compile(r"(?<![A-Za-z0-9_\\])[-+]?(?:\d+(?:[.,]\d+)*|[.,]\d+)(?:[eE][-+]?\d+)?")
UNIT: Final = re.compile(r"(?<![A-Za-z'’])(?:GiB/s|GB/s|MiB/s|MB/s|Gbps|Mbps|GHz|MHz|kHz|Hz|"
                        r"GFLOPS|TFLOPS|FLOPS|GiB|MiB|GB|MB|KB|KiB|B|b|ns|ms|us|μs|µs|s|"
                        r"mW|kW|W|mJ|pJ|nJ|J|mm\^?2|mm²|cycles|bytes)(?![A-Za-z])|(?<!\\)%|\\%")
MATH: Final = re.compile(r"(?<!\\)\$\$.*?(?<!\\)\$\$|(?<!\\)\$(?!\$).*?(?<!\\)\$|"
                        r"\\\(.*?\\\)|\\\[.*?\\\]|"
                        r"\\begin\{(equation\*?|align\*?|alignat\*?|flalign\*?|gather\*?|multline\*?|math|displaymath|eqnarray\*?)\}.*?\\end\{\1\}", re.DOTALL)


class EditingReport(TypedDict):
    tool: str
    status: Status
    findings: list[Finding]
    original: str
    revised: str
    unified_diff: str
    semantic_review: str


class ProtectedTokens(TypedDict):
    numeric_tokens: Counter[str]
    unit_tokens: Counter[str]
    citation_keys: Counter[str]
    bibtex_keys: Counter[str]
    multi_citation_syntax: Counter[str]
    labels: Counter[str]
    reference_targets: Counter[str]
    latex_commands: Counter[str]
    math_expressions: Counter[str]


def protected(path: Path, text: str) -> ProtectedTokens:
    """Extract conserved tokens, not semantic meaning or factual correctness."""
    masked = mask_tex(text) if path.suffix.lower() in {".tex", ".bib", ".sty", ".cls"} else text
    parsed = commands(path, masked)
    cites = Counter(key.strip() for command in parsed if CITES.fullmatch(command.name)
                    for key in command.value.split(","))
    labels = Counter(command.value for command in parsed if command.name == "label")
    references = Counter(command.name + ":" + command.value for command in parsed
                         if command.name in {"ref", "eqref", "cref", "Cref", "autoref", "pageref", "nameref", "subref"})
    return {"numeric_tokens": Counter(NUMBER.findall(masked)),
            "unit_tokens": Counter(UNIT.findall(masked)),
            "citation_keys": cites,
            "bibtex_keys": Counter(match.group(1) for match in BIB_ENTRY.finditer(text))
                if path.suffix.lower() == ".bib" else Counter(),
            "multi_citation_syntax": Counter(re.sub(r"\s+", " ", value).strip() for value in re.findall(
                r"\\(?:cites|parencites|textcites|autocites|footcites|smartcites|supercites)\s*(?:\[[^\]]*\]\s*|\{[^{}]*\}\s*)+", masked, re.IGNORECASE)),
            "labels": labels, "reference_targets": references,
            "latex_commands": Counter(re.findall(r"\\(?:[A-Za-z]+\*?|[^A-Za-z\s])", masked)),
            "math_expressions": Counter(re.sub(r"\s+", " ", match.group()).strip()
                                        for match in MATH.finditer(masked))}


def review(original: Path, revised: Path) -> EditingReport:
    """Read two separate files; do not apply edits or alter either input."""
    before, after = read_text(original), read_text(revised)
    old_tokens, new_tokens = protected(original, before), protected(revised, after)
    findings: list[Finding] = []
    for check, previous in old_tokens.items():
        current = new_tokens[check]
        if previous != current:
            removed = list((previous - current).elements())
            added = list((current - previous).elements())
            findings.append(issue(check, f"Protected tokens changed; removed={removed}; added={added}"))
        else:
            findings.append(notice(check, "Protected token multiset preserved", "PASS"))
    findings.append(notice("technical_meaning", "Token preservation cannot prove numerical associations, causality, scope or technical meaning; author review required", "UNKNOWN"))
    diff = difflib.unified_diff(before.splitlines(keepends=True), after.splitlines(keepends=True),
                               fromfile=str(original), tofile=str(revised))
    patch = "".join(line if line.endswith("\n") else line + "\n\\ No newline at end of file\n"
                    for line in diff)
    return {"tool": "editing_guard", "status": "FAIL" if any(item["status"] == "FAIL" for item in findings) else "UNKNOWN",
            "findings": findings, "original": str(original.resolve()), "revised": str(revised.resolve()),
            "unified_diff": patch,
            "semantic_review": "MANUAL_REQUIRED"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original", type=Path)
    parser.add_argument("revised", type=Path)
    parser.add_argument("--json", action="store_true", help="JSON output (also default)")
    args = parser.parse_args()
    try:
        report = review(args.original, args.revised)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return int(report["status"] == "FAIL")
    except InputError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
