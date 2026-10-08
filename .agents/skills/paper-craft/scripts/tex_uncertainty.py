"""Lexical TeX uncertainty: conditional spans and possible symbol producers."""
from __future__ import annotations

import re
from dataclasses import replace
from pathlib import Path
from typing import Final

from manuscript_common import Command, commands, escaped_at

PRODUCERS: Final = frozenset({"label", "bibitem", "bibliography", "addbibresource",
                            "input", "include", "subfile", "includeonly", "externaldocument"})
CONTROL: Final = re.compile(r"\\([A-Za-z@]+)")


def conditional_spans(text: str) -> tuple[tuple[int, int], ...]:
    """Mark primitive if/fi branches without evaluating their predicates."""
    spans: list[tuple[int, int]] = []
    starts: list[int] = []
    declaring = False
    covered_until = 0
    for match in CONTROL.finditer(text):
        if match.start() < covered_until or escaped_at(text, match.start()):
            continue
        name = match.group(1)
        if declaring:
            declaring = False
            continue
        if name in {"ifthenelse", "IfFileExists"}:
            end = match.end()
            for _ in range(3):
                while end < len(text) and text[end].isspace():
                    end += 1
                if end >= len(text) or text[end] != "{":
                    end = len(text)
                    break
                depth = 1
                end += 1
                while end < len(text) and depth:
                    if text[end] in "{}" and not escaped_at(text, end):
                        depth += 1 if text[end] == "{" else -1
                    end += 1
            spans.append((match.start(), end))
            covered_until = end
        elif name == "newif":
            declaring = True
        elif name.startswith("if"):
            starts.append(match.start())
        elif name == "fi" and starts:
            start = starts.pop()
            if not starts:
                spans.append((start, match.end()))
    if starts:
        spans.append((starts[0], len(text)))
    return tuple(spans)


def scoped_commands(path: Path, text: str, inherited: bool = False) -> tuple[Command, ...]:
    """Mark commands whose execution depends on an unexpanded conditional."""
    spans = conditional_spans(text)
    return tuple(replace(command, uncertain=inherited or any(
        start <= command.offset < end for start, end in spans)) for command in commands(path, text))


def possible_commands(path: Path, original: str, masked: str) -> tuple[Command, ...]:
    """Keep macro-body producers as candidates, never as definite definitions."""
    parsed = commands(path, original)
    candidates = [replace(command, uncertain=True) for command in parsed
                  if command.name in PRODUCERS and masked[command.offset] != original[command.offset]]
    offsets = {command.offset for command in parsed}
    for match in CONTROL.finditer(original):
        if escaped_at(original, match.start()):
            continue
        name = match.group(1)
        # A bare producer/alias or constructed control sequence cannot be resolved lexically.
        names = ("label", "bibitem", "input") if name == "csname" else (name,)
        for producer in names:
            if producer in PRODUCERS and match.start() not in offsets:
                candidates.append(Command(producer, "\\dynamic", path,
                                          original.count("\n", 0, match.start()) + 1,
                                          match.start(), uncertain=True))
    return tuple(candidates)
