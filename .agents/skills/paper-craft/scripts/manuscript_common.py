"""Read-only LaTeX graph and structured findings shared by manuscript checks."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Literal, TypedDict

Status = Literal["PASS", "FAIL", "SKIPPED", "UNKNOWN"]


class Finding(TypedDict):
    check: str
    status: Status
    severity: str
    file: str | None
    line: int | None
    message: str


class Report(TypedDict):
    tool: str
    status: Status
    findings: list[Finding]


@dataclass(frozen=True, slots=True)
class Command:
    name: str
    value: str
    path: Path
    line: int
    offset: int


@dataclass(frozen=True, slots=True)
class TexFile:
    path: Path
    text: str
    commands: tuple[Command, ...]


@dataclass(frozen=True, slots=True)
class Project:
    root: Path
    entry: Path
    files: tuple[TexFile, ...]
    findings: tuple[Finding, ...]


class InputError(Exception):
    """A local input cannot be read or its project boundary is invalid."""


COMMAND: Final = re.compile(r"\\([A-Za-z]+)\*?\s*(?:\[[^\]\n]*\]\s*)*(\{)")
LITERAL: Final = re.compile(r"^[^\\{}#$\n\r]+$")
INCLUDE: Final = frozenset({"input", "include", "subfile"})


def issue(check: str, message: str, at: Command | None = None) -> Finding:
    """Create a definite failure, optionally anchored to a parsed command."""
    return {"check": check, "status": "FAIL", "severity": "Major",
            "file": str(at.path) if at else None, "line": at.line if at else None,
            "message": message}


def notice(check: str, message: str, status: Status = "SKIPPED") -> Finding:
    """Create an explicit unperformed or successful check."""
    return {"check": check, "status": status, "severity": "Info",
            "file": None, "line": None, "message": message}


def emit(tool: str, findings: list[Finding]) -> int:
    """Emit JSON; only a definite failed check exits 1."""
    statuses = {item["status"] for item in findings}
    status: Status = "PASS"
    if "FAIL" in statuses:
        status = "FAIL"
    elif "UNKNOWN" in statuses:
        status = "UNKNOWN"
    elif "SKIPPED" in statuses:
        status = "SKIPPED"
    report: Report = {"tool": tool, "status": status, "findings": findings}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return int(status == "FAIL")


def read_text(path: Path) -> str:
    """Read UTF-8 without silently replacing manuscript bytes."""
    try:
        return path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as exc:
        raise InputError(f"Cannot read UTF-8 input {path}: {exc}") from exc


def escaped_at(text: str, position: int) -> bool:
    """An odd preceding backslash run escapes a character or command start."""
    previous = position - 1
    while previous >= 0 and text[previous] == "\\":
        previous -= 1
    return bool((position - previous - 1) % 2)


def mask_tex(text: str) -> str:
    """Mask comments and verbatim content, preserving line/offset locations."""
    def blank(match: re.Match[str]) -> str:
        return re.sub(r"[^\n]", " ", match.group())

    text = re.sub(r"\\begin\{(verbatim\*?|Verbatim|lstlisting|minted)\}.*?"
                  r"\\end\{\1\}", blank, text, flags=re.DOTALL)
    text = re.sub(r"\\verb\*?([^A-Za-z\s]).*?\1", blank, text)
    chars = list(text)
    for position, char in enumerate(text):
        if char != "%":
            continue
        if escaped_at(text, position):
            continue
        end = text.find("\n", position)
        end = len(text) if end < 0 else end
        chars[position:end] = " " * (end - position)
    return "".join(chars)


def commands(path: Path, text: str) -> tuple[Command, ...]:
    """Extract balanced braced arguments; never execute TeX macros."""
    found: list[Command] = []
    for match in COMMAND.finditer(text):
        if escaped_at(text, match.start()):
            continue
        start = match.end()
        depth = 1
        end = start
        while end < len(text) and depth:
            if text[end] in "{}" and not escaped_at(text, end):
                depth += 1 if text[end] == "{" else -1
            end += 1
        if depth == 0:
            found.append(Command(match.group(1), text[start:end - 1], path,
                                 text.count("\n", 0, match.start()) + 1, match.start()))
    return tuple(found)


def mask_definitions(text: str) -> str:
    """Exclude literal commands inside unevaluated macro definition bodies."""
    pattern = re.compile(r"\\(?:newcommand|renewcommand|providecommand|DeclareRobustCommand)\*?\s*"
                         r"(?:\{\\[^{}]+\}|\\[A-Za-z@]+)\s*(?:\[[^\]]*\]\s*)*\{|"
                         r"\\(?:def|gdef|edef|xdef)\s*\\[A-Za-z@]+[^\n{]*\{")
    characters = list(text)
    for match in pattern.finditer(text):
        end, depth = match.end(), 1
        while end < len(text) and depth:
            if text[end] in "{}" and not escaped_at(text, end):
                depth += 1 if text[end] == "{" else -1
            end += 1
        characters[match.start():end] = re.sub(r"[^\n]", " ", text[match.start():end])
    return "".join(characters)


def resolve_path(project: Project, command: Command, suffixes: tuple[str, ...]) -> Path | None:
    """Resolve literal paths within the supplied boundary, without external reads."""
    value = command.value.strip()
    if not LITERAL.fullmatch(value):
        return None
    bases = (project.entry.parent, command.path.parent)
    for base in bases:
        candidate = (base / value).resolve()
        if not candidate.is_relative_to(project.root):
            continue
        for suffix in suffixes:
            path = (candidate if candidate.suffix else Path(str(candidate) + suffix)).resolve()
            if path.is_relative_to(project.root) and path.is_file():
                return path
    return None


def load_project(input_path: Path, root: Path | None = None) -> Project:
    """Follow only reachable literal inputs; uncertain paths never become PASS."""
    entry = input_path.resolve()
    boundary = root.resolve() if root else (entry if entry.is_dir() else entry.parent)
    if not boundary.is_dir() or not entry.is_relative_to(boundary):
        raise InputError("Entry must be inside --project-root")
    if entry.is_dir():
        eligible = {path.resolve() for path in entry.glob("*.tex")
                    if path.resolve().is_relative_to(boundary) and path.resolve().is_file()}
        candidates = [path for path in sorted(eligible)
                      if re.search(r"\\documentclass\b", mask_tex(read_text(path)))]
        if len(candidates) != 1:
            raise InputError("Directory needs exactly one root document; pass explicit .tex file")
        entry = candidates[0]
    if not boundary.is_dir() or not entry.is_file() or not entry.is_relative_to(boundary):
        raise InputError("Entry must be an existing file inside --project-root")
    pending = [entry]
    files: list[TexFile] = []
    findings: list[Finding] = []
    visited: set[Path] = set()
    while pending:
        path = pending.pop()
        if path in visited:
            continue
        visited.add(path)
        original = mask_tex(read_text(path))
        text = mask_definitions(original)
        parsed = commands(path, text)
        files.append(TexFile(path, text, parsed))
        project = Project(boundary, entry, (), ())
        if re.search(r"\\(?:newcommand|renewcommand|providecommand|DeclareRobustCommand|def|gdef|edef|xdef)\b", original):
            findings.append(notice("macro_expansion", f"Macro definitions at {path}; macro-generated commands and conditional labels need manual review"))
        conditional = bool(re.search(r"\\if[A-Za-z@]*\b", text))
        if conditional:
            findings.append(notice("conditional_commands", f"Conditional TeX branches at {path}; static reachability uncertain"))
        for command in parsed:
            if command.name not in INCLUDE:
                continue
            if not LITERAL.fullmatch(command.value.strip()):
                findings.append(notice("include_graph", f"Dynamic input at {path}:{command.line}; manual resolution required"))
                continue
            included = resolve_path(project, command, (".tex", ""))
            if included:
                pending.append(included)
            else:
                findings.append(notice("include_path", f"Conditional input {command.value}; expansion required") if conditional
                                else issue("include_path", f"Missing or outside project: {command.value}", command))
        if re.search(r"\\(?:input|include)\s+[^\s{]", text):
            findings.append(notice("include_graph", f"Unbraced input at {path}; manual resolution required"))
        if re.search(r"\\includeonly\b", text):
            findings.append(notice("include_graph", "includeonly found; static graph includes all listed inputs"))
    return Project(boundary, entry, tuple(files), tuple(findings))


def all_commands(project: Project) -> tuple[Command, ...]:
    return tuple(command for file in project.files for command in file.commands)
