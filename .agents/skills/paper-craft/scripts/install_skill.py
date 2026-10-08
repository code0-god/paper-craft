#!/usr/bin/env python3
"""Copy the entire skill; updates retain the previous directory as a backup."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from validate_skill import validate


def install(source: Path, destination: Path, update: bool = False) -> Path | None:
    """Validate first, stage on the same filesystem, retain all old files on update."""
    source = source.resolve()
    destination = destination.expanduser().absolute()
    if destination.is_symlink():
        raise ValueError("Destination cannot be a symlink")
    resolved = destination.resolve()
    if resolved.is_relative_to(source) or source.is_relative_to(resolved):
        raise ValueError("Source and destination must not overlap")
    if destination.name != "paper-craft":
        raise ValueError("Destination directory must be named paper-craft")
    report = validate(source)
    if report["status"] != "PASS":
        raise ValueError(json.dumps(report, ensure_ascii=False))
    if destination.exists() and (not update or not destination.is_dir()):
        raise FileExistsError("Destination exists; --update retains a backup before replacement")
    destination.parent.mkdir(parents=True, exist_ok=True)
    backup: Path | None = None
    with tempfile.TemporaryDirectory(prefix=".paper-craft-install-", dir=destination.parent) as temporary:
        staged = Path(temporary) / "paper-craft"
        shutil.copytree(source, staged, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        if destination.exists():
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            if destination.parent.name == "skills":
                backup = destination.parent.parent / "paper-craft-backups" / stamp / "paper-craft"
            else:
                backup = destination.with_name(f"paper-craft.backup-{stamp}")
            if backup.exists():
                raise FileExistsError(f"Backup already exists: {backup}")
            backup.parent.mkdir(parents=True, exist_ok=True)
            destination.rename(backup)
        try:
            os.rename(staged, destination)
        except OSError:
            if backup is not None:
                backup.rename(destination)
            raise
    return backup


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", required=True, type=Path,
                        help="Full target directory, e.g. ~/.agents/skills/paper-craft")
    parser.add_argument("--update", action="store_true")
    args = parser.parse_args()
    try:
        backup = install(Path(__file__).resolve().parents[1], args.destination, args.update)
    except (OSError, ValueError) as error:
        parser.exit(2, f"install_skill: {error}\n")
    print(json.dumps({"tool": "install_skill", "status": "PASS",
                      "destination": str(args.destination.expanduser().absolute()),
                      "backup": str(backup) if backup else None}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
