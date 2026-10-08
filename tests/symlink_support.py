"""Skip only when Windows explicitly denies symbolic-link creation privileges."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


def symlink_or_skip(link: Path, target: Path) -> None:
    try:
        link.symlink_to(target)
    except OSError as error:
        if sys.platform == "win32" and getattr(error, "winerror", None) == 1314:
            raise unittest.SkipTest("Windows symbolic-link privilege is unavailable") from error
        raise
