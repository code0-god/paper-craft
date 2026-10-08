#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
# How to run: python3 source_material.py inspect lecture.html --source-id B --json
"""Inspect local reference HTML as inert text with source anchors and hash."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Final, Literal, TypedDict

from manuscript_common import Finding, InputError, Status, notice, read_text


class Block(TypedDict):
    tag: str
    anchor: str | None
    line: int
    text: str
    provenance: str


class MaterialReport(TypedDict):
    tool: str
    status: Status
    findings: list[Finding]
    source_id: Literal["A", "B"]
    path: str
    format: str
    sha256: str
    blocks: list[Block]
    distribution: str


BLOCK_TAGS: Final = frozenset({"h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "blockquote", "pre", "td", "th"})
INERT_TAGS: Final = frozenset({"script", "style", "template", "noscript"})
VOID_TAGS: Final = frozenset({"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"})


class MaterialParser(HTMLParser):
    """Accumulate document text; active content and external resources stay inert."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.blocks: list[Block] = []
        self.stack: list[tuple[str, str | None, int, int]] = []
        self.suppressed: list[str] = []
        self.last_identity: tuple[str, str | None, int, int] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag in VOID_TAGS:
            if tag == "br" and self.blocks and not self.suppressed:
                self.blocks[-1]["text"] += "\n"
            return
        if tag in INERT_TAGS or self.suppressed:
            self.suppressed.append(tag)
            return
        self.stack.append((tag, values.get("id"), *self.getpos()))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "br" and self.blocks and not self.suppressed:
            self.blocks[-1]["text"] += "\n"

    def handle_endtag(self, tag: str) -> None:
        if self.suppressed:
            if tag in self.suppressed:
                while self.suppressed and self.suppressed.pop() != tag:
                    continue
            return
        positions = [index for index, item in enumerate(self.stack) if item[0] == tag]
        if positions:
            del self.stack[positions[-1]:]

    def handle_data(self, data: str) -> None:
        if self.suppressed or not data.strip():
            return
        parent = next((item for item in reversed(self.stack) if item[0] in BLOCK_TAGS),
                      self.stack[-1] if self.stack else ("text", None, *self.getpos()))
        anchor = parent[1] or next((item[1] for item in reversed(self.stack) if item[1]), None)
        identity = (parent[0], anchor, parent[2], parent[3])
        if self.blocks and self.last_identity == identity:
            self.blocks[-1]["text"] += data
        else:
            self.blocks.append({"tag": parent[0], "anchor": anchor, "line": parent[2],
                                "text": data, "provenance": "source_text"})
        self.last_identity = identity


def inspect(path: Path, source_id: Literal["A", "B"]) -> MaterialReport:
    """Extract original text only; interpretation must be separately attributed."""
    text = read_text(path)
    blocks: list[Block]
    if path.suffix.lower() in {".html", ".htm"}:
        parser = MaterialParser()
        parser.feed(text)
        parser.close()
        blocks = [{**block, "text": re.sub(r"\s+", " ", block["text"]).strip()} for block in parser.blocks]
        format_name = "html"
    elif path.suffix.lower() in {".txt", ".md"}:
        blocks = [{"tag": "text", "anchor": None, "line": index, "text": line,
                   "provenance": "source_text"} for index, line in enumerate(text.splitlines(), 1) if line.strip()]
        format_name = path.suffix.lower().lstrip(".")
    else:
        raise InputError("Supported source formats: .html, .htm, .txt, .md; PDF/DOCX require separate extraction tools")
    return {"tool": "source_material", "status": "PASS", "findings": [notice("safe_extraction", "Local inert-text extraction only; no script execution, network access or source copying", "PASS")],
            "source_id": source_id, "path": str(path.resolve()), "format": format_name,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "blocks": blocks,
            "distribution": "Do not bundle original or full extracted text without rights; record source-derived interpretation separately from independent guidance"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    command = subparsers.add_parser("inspect")
    command.add_argument("path", type=Path)
    command.add_argument("--source-id", choices=("A", "B"), required=True)
    command.add_argument("--json", action="store_true", help="JSON output (also default)")
    args = parser.parse_args()
    try:
        print(json.dumps(inspect(args.path, args.source_id), ensure_ascii=False, indent=2))
        return 0
    except InputError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
