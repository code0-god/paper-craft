#!/usr/bin/env python3
"""Validate this package's scalar YAML, local links, and Python syntax; stdlib only."""

from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path
from typing import TypedDict
from urllib.parse import unquote, urlparse


class Finding(TypedDict):
    check: str
    status: str
    severity: str
    file: str
    line: int | None
    message: str


class ValidationReport(TypedDict):
    tool: str
    status: str
    findings: list[Finding]


def scalar(value: str) -> str:
    """Parse the deliberately narrow, single-line string YAML used by this package."""
    if value.startswith('"'):
        parsed = json.loads(value)
        if not isinstance(parsed, str):
            raise ValueError("Expected string scalar")
        return parsed
    if re.fullmatch(r"[a-z][a-z0-9-]*", value):
        return value
    raise ValueError("Use a JSON-quoted YAML string or lowercase name scalar")


def frontmatter(text: str) -> dict[str, str]:
    """Reject malformed/duplicate fields instead of pretending to parse arbitrary YAML."""
    lines = text.splitlines()
    if not lines or lines[0] != "---" or "---" not in lines[1:]:
        raise ValueError("Missing YAML frontmatter delimiters")
    fields: dict[str, str] = {}
    for line in lines[1:lines.index("---", 1)]:
        if not line.strip():
            continue
        key, delimiter, value = line.partition(":")
        if not delimiter or key in fields or key.strip() != key:
            raise ValueError("Malformed or duplicate frontmatter field")
        if key not in {"name", "description", "compatibility", "license", "allowed-tools"}:
            raise ValueError(f"Unsupported package frontmatter field: {key}")
        fields[key] = scalar(value.strip())
    return fields


def validate(root: Path) -> ValidationReport:
    """Validate distributable structure without executing scripts or following symlinks."""
    findings: list[Finding] = []

    def fail(check: str, path: Path, message: str) -> None:
        findings.append({"check": check, "status": "FAIL", "severity": "Major",
                         "file": str(path), "line": None, "message": message})

    entry = root / "SKILL.md"
    if not entry.is_file():
        fail("entrypoint", entry, "SKILL.md is missing")
        return {"tool": "validate_skill", "status": "FAIL", "findings": findings}
    try:
        text = entry.read_text(encoding="utf-8")
        fields = frontmatter(text)
        name = fields.get("name", "")
        if (name != "paper-craft" or root.name != name or len(name) > 64
                or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name)):
            fail("name", entry, "Name must be paper-craft and match its directory")
        if not 1 <= len(fields.get("description", "")) <= 1024:
            fail("description", entry, "Description must contain 1–1024 characters")
        if "compatibility" in fields and not 1 <= len(fields["compatibility"]) <= 500:
            fail("compatibility", entry, "Compatibility must contain 1–500 characters")
    except (OSError, UnicodeError, ValueError) as error:
        fail("frontmatter", entry, str(error))

    resolved_root = root.resolve()
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            fail("standalone", path, "Package must not depend on symlinks")
            continue
        if not path.is_file():
            continue
        if path.suffix not in {".md", ".py", ".json", ".yaml"}:
            continue
        try:
            content = path.read_text(encoding="utf-8")
            if path.suffix == ".md":
                for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", content):
                    target = target.strip().strip("<>")
                    parsed = urlparse(target)
                    if parsed.scheme or not parsed.path:
                        continue
                    destination = (path.parent / unquote(parsed.path)).resolve()
                    if not destination.is_relative_to(resolved_root):
                        fail("standalone", path, f"Link escapes installed package: {target}")
                    elif not destination.is_file():
                        fail("internal_link", path, f"Missing resource: {target}")
            elif path.suffix == ".py":
                ast.parse(content, filename=str(path), feature_version=(3, 10))
            elif path.suffix == ".json":
                json.loads(content)
        except (OSError, UnicodeError, ValueError, SyntaxError) as error:
            fail("resource", path, str(error))

    metadata = root / "agents" / "openai.yaml"
    try:
        groups: dict[str, dict[str, str]] = {}
        current = ""
        for line in metadata.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            if not line.startswith(" ") and line.endswith(":"):
                current = line[:-1]
                if current in groups or current not in {"interface", "policy"}:
                    raise ValueError("Invalid/duplicate UI metadata group")
                groups[current] = {}
            else:
                key, delimiter, value = line.strip().partition(":")
                if (not line.startswith("  ") or not delimiter
                        or current not in groups or key in groups[current]):
                    raise ValueError("Invalid UI metadata entry")
                groups[current][key] = value.strip()
        interface = groups.get("interface", {})
        if scalar(interface.get("display_name", "")) != "Paper Craft":
            raise ValueError("UI display_name must be Paper Craft")
        if not 25 <= len(scalar(interface.get("short_description", ""))) <= 64:
            raise ValueError("UI short_description must contain 25–64 characters")
        if "$paper-craft" not in scalar(interface.get("default_prompt", "")):
            raise ValueError("UI default_prompt must explicitly invoke $paper-craft")
        if groups.get("policy", {}).get("allow_implicit_invocation") != "true":
            raise ValueError("Implicit invocation must be enabled")
    except (OSError, UnicodeError, ValueError) as error:
        fail("ui_metadata", metadata, str(error))
    return {"tool": "validate_skill", "status": "FAIL" if findings else "PASS",
            "findings": findings}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = validate(args.skill)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"{report['tool']}: {report['status']}")
        for finding in report["findings"]:
            print(f"{finding['file']}: {finding['message']}")
    return int(report["status"] == "FAIL")


if __name__ == "__main__":
    raise SystemExit(main())
