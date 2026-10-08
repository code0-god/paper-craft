#!/usr/bin/env python3
"""Select private review storage and capture hashes without changing manuscripts."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, TypedDict

Origin = Literal["explicit", "environment", "os_default"]


class Receipt(TypedDict):
    path: str
    sha256: str | None
    size: int | None
    status: str


class OutputReport(TypedDict):
    tool: str
    status: str
    output_dir: str
    selection: Origin
    created: bool
    warnings: list[str]
    inputs: list[Receipt]
    proposals: list[Receipt]


def git_root(path: Path, failures: list[str] | None = None) -> Path | None:
    ancestor = path
    while not ancestor.exists() and ancestor != ancestor.parent:
        ancestor = ancestor.parent
    if ancestor.is_file():
        ancestor = ancestor.parent
    try:
        result = subprocess.run(["git", "-C", str(ancestor), "rev-parse", "--show-toplevel"],
                                capture_output=True, text=True, timeout=10, check=False)
    except (OSError, subprocess.TimeoutExpired):
        if failures is not None:
            failures.append("Git tracking could not be checked; inspect the output path before committing.")
        return None
    return Path(result.stdout.strip()).resolve() if result.returncode == 0 else None


def output_warnings(path: Path) -> list[str]:
    failures: list[str] = []
    root = git_root(path, failures)
    if root is None or not path.resolve().is_relative_to(root):
        return failures
    relative = path.resolve().relative_to(root).as_posix()
    try:
        tracked = subprocess.run(["git", "-C", str(root), "ls-files", "-z", "--", relative],
                                 capture_output=True, timeout=10, check=False)
        ignored = subprocess.run(["git", "-C", str(root), "check-ignore", "--no-index", "-q", "--",
                                  relative + "/"], capture_output=True, timeout=10, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return ["Git tracking could not be checked; inspect the output path before committing."]
    if tracked.stdout:
        return ["Output path contains Git-tracked files; derived research data may enter source control."]
    if ignored.returncode != 0:
        return ["Output path is inside a Git repository and is not ignored; accidental git add is possible."]
    return []


def select_output(explicit: Path | None = None) -> tuple[Path, Origin]:
    """Explicit directory overrides environment, then private OS user storage."""
    configured = os.environ.get("PAPER_CRAFT_OUTPUT_DIR")
    if explicit is not None:
        return explicit.expanduser().resolve(), "explicit"
    if configured:
        return Path(configured).expanduser().resolve(), "environment"
    home = Path.home()
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", str(home / "AppData/Local"))) / "PaperCraft/reviews"
    elif sys.platform == "darwin":
        base = home / "Library/Application Support/PaperCraft/reviews"
    else:
        base = Path(os.environ.get("XDG_STATE_HOME", str(home / ".local/state"))) / "paper-craft/reviews"
    # A Git-managed home/configuration can contain the usual state directory.
    source_root = git_root(Path(__file__).resolve().parents[1])
    if source_root is not None and base.resolve().is_relative_to(source_root):
        base = Path(tempfile.gettempdir()) / f"paper-craft-{os.getuid() if hasattr(os, 'getuid') else 'user'}" / "reviews"
        if base.resolve().is_relative_to(source_root):
            raise ValueError("Default storage is inside the Skill repository; specify an external output directory")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    return (base / f"review-{stamp}").resolve(), "os_default"


def fingerprint(path: Path) -> Receipt:
    """Hash supplied local files; never treat a missing/unreadable file as read."""
    try:
        content = path.read_bytes()
    except (OSError, ValueError):
        return {"path": str(path), "sha256": None, "size": None, "status": "UNREADABLE"}
    return {"path": str(path.resolve()), "sha256": hashlib.sha256(content).hexdigest(),
            "size": len(content), "status": "HASHED"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--create", action="store_true", help="Create selected storage; no manuscript writes")
    parser.add_argument("--inputs", type=Path, nargs="*", default=[])
    parser.add_argument("--proposals", type=Path, nargs="*", default=[])
    parser.add_argument("--json", action="store_true", help="JSON is also the default")
    args = parser.parse_args()
    try:
        output, origin = select_output(args.output_dir)
        warnings = output_warnings(output)
        source_root = git_root(Path(__file__).resolve().parents[1])
        if source_root is not None and output.is_relative_to(source_root):
            warnings.append("Output is inside the Skill source repository; keep research derivatives private.")
        created = False
        if args.create:
            if origin == "os_default":
                output.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                output.mkdir(mode=0o700)
            else:
                output.mkdir(parents=True, exist_ok=True, mode=0o700)
            created = True
        report: OutputReport = {"tool": "review_output", "status": "PASS", "output_dir": str(output),
                                "selection": origin, "created": created, "warnings": warnings,
                                "inputs": [fingerprint(path) for path in args.inputs],
                                "proposals": [fingerprint(path) for path in args.proposals]}
        print(json.dumps(report, ensure_ascii=False, indent=2))
        for warning in warnings:
            print(f"review_output warning: {warning}", file=sys.stderr)
        return 0
    except (OSError, ValueError, RuntimeError) as error:
        parser.exit(2, f"review_output: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
