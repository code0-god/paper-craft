#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
# How to run: python3 reference_audit.py main.tex --json
"""Audit local citation keys; never generate or remotely verify references."""
from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Final

from manuscript_common import (
    LITERAL,
    Command,
    Finding,
    InputError,
    all_commands,
    emit,
    issue,
    load_project,
    notice,
    read_text,
    resolve_path,
)

CITES: Final = re.compile(r"^(?:cite|citep|citet|citealp|citealt|citenum|citeauthor|citeyear|citeyearpar|citefield|parencite|textcite|autocite|footcite|smartcite|supercite|fullcite|footfullcite|notecite|pnotecite|nocite)$", re.IGNORECASE)
BIB_ENTRY: Final = re.compile(r"@(?!comment\b|string\b|preamble\b)[A-Za-z]+\s*[({]\s*([^\s,{}()]+)\s*,", re.IGNORECASE)


def audit(input_path: Path, root: Path | None = None) -> list[Finding]:
    """Check citations against reachable bibliography resources and bibitem keys."""
    standalone = input_path.suffix.lower() == ".bib"
    project = None if standalone else load_project(input_path, root)
    findings = list(project.findings) if project else []
    parsed = all_commands(project) if project else ()
    keys: dict[str, list[str]] = defaultdict(list)
    sources: set[Path] = {input_path.resolve()} if standalone else set()
    if standalone and root is not None and not input_path.resolve().is_relative_to(root.resolve()):
        raise InputError("Bibliography must be inside --project-root")
    incomplete = bool(findings)
    for command in parsed:
        if command.name == "bibitem":
            keys[command.value].append(f"{command.path}:{command.line}")
        if command.name not in {"bibliography", "addbibresource"}:
            continue
        if project is None:
            continue
        for value in command.value.split(","):
            if not LITERAL.fullmatch(value.strip()):
                incomplete = True
                findings.append(notice("bibliography_path", f"Dynamic bibliography at {command.path}:{command.line}"))
                continue
            resource = Command(command.name, value.strip(), command.path, command.line, command.offset)
            path = resolve_path(project, resource, (".bib", ""))
            if path:
                sources.add(path)
            else:
                incomplete = True
                conditional = any(item["check"] == "conditional_commands" for item in project.findings)
                findings.append(notice("bibliography_path", f"Conditional bibliography {value.strip()}; expansion required") if conditional
                                else issue("bibliography_path", f"Missing or outside project: {value.strip()}", command))
    for path in sorted(sources):
        text = read_text(path)
        # BibTeX @comment bodies and percent comments are not entries.
        text = re.sub(r"@comment\s*\{.*?\}", "", text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r"(?m)^\s*%.*$", "", text)
        for match in BIB_ENTRY.finditer(text):
            keys[match.group(1)].append(f"{path}:{text.count(chr(10), 0, match.start()) + 1}")
    for key, locations in keys.items():
        if len(locations) > 1:
            findings.append(issue("duplicate_bib_key", f"Duplicate key {key}: {', '.join(locations)}"))
    for command in parsed:
        if re.fullmatch(r"(?:cites|parencites|textcites|autocites|footcites|smartcites|supercites)", command.name, re.IGNORECASE):
            findings.append(notice("multi_citation", f"Multi-citation syntax at {command.path}:{command.line}; inspect all argument groups manually"))
        if not CITES.fullmatch(command.name):
            continue
        if command.name == "nocite" and command.value.strip() == "*":
            continue
        if not LITERAL.fullmatch(command.value):
            findings.append(notice("citation_key", f"Dynamic citation at {command.path}:{command.line}"))
            continue
        for key in (value.strip() for value in command.value.split(",")):
            if key not in keys:
                findings.append(notice("citation_key", f"Cannot resolve {key} with incomplete bibliography") if incomplete
                                else issue("missing_citation_key", f"Citation key {key} absent from local bibliography", command))
    findings.append(notice("local_keys", f"Inspected {len(sources)} bibliography file(s), {len(keys)} unique key(s)", "PASS"))
    findings.append(notice("reference_authenticity", "Author/title/DOI accuracy, closest prior work and citation relevance need source verification", "UNKNOWN"))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--project-root", type=Path)
    parser.add_argument("--json", action="store_true", help="JSON output (also default)")
    args = parser.parse_args()
    try:
        return emit("reference_audit", audit(args.root, args.project_root))
    except InputError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
