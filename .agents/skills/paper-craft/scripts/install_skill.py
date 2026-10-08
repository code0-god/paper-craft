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


def preflight(source: Path, destination: Path, update: bool = False) -> Path:
    """Reject predictable conflicts without creating directories or copying files."""
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
    for parent in destination.parents:
        if parent.exists() and not parent.is_dir():
            raise NotADirectoryError(f"Destination parent is not a directory: {parent}")
        if parent.is_symlink() and not parent.exists():
            raise FileNotFoundError(f"Destination parent is a broken symlink: {parent}")
    if update and destination.exists() and destination.parent.name == "skills":
        backup_root = destination.parent.parent / "paper-craft-backups"
        if backup_root.is_symlink() or (backup_root.exists() and not backup_root.is_dir()):
            raise FileExistsError(f"Backup directory is not a regular directory: {backup_root}")
    return destination


def install(source: Path, destination: Path, update: bool = False) -> Path | None:
    """Validate first, stage on the same filesystem, retain all old files on update."""
    source = source.resolve()
    destination = preflight(source, destination, update)
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
    parser.add_argument("--destination", required=True, type=Path, action="append",
                        help="Full target directory, e.g. ~/.agents/skills/paper-craft")
    parser.add_argument("--update", action="store_true")
    parser.add_argument("--batch", action="store_true", help="Emit a batch report, even for one target")
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[1]
    destinations: list[Path] = []
    completed: list[dict[str, str | None]] = []
    pending = args.destination
    batch = args.batch or len(args.destination) > 1
    try:
        for target in args.destination:
            target = preflight(source, target, args.update)
            resolved = target.resolve()
            if any(resolved == other.resolve() for other in destinations):
                continue
            if any(resolved.is_relative_to(other.resolve()) or other.resolve().is_relative_to(resolved)
                   for other in destinations):
                raise ValueError("Batch destinations must not overlap")
            destinations.append(target)
        pending = destinations
        for destination in destinations:
            backup = install(source, destination, args.update)
            completed.append({"destination": str(destination), "backup": str(backup) if backup else None})
    except (OSError, ValueError, RuntimeError, shutil.Error) as error:
        if batch:
            print(json.dumps({"tool": "install_skill", "status": "FAIL", "completed": completed,
                              "remaining": [str(target) for target in pending
                                            if str(target) not in
                                            {item["destination"] for item in completed}],
                              "error": str(error)}, indent=2))
            return 2
        parser.exit(2, f"install_skill: {error}\n")
    report = {"tool": "install_skill", "status": "PASS"}
    print(json.dumps({**report, "targets": completed} if batch else {**report, **completed[0]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
