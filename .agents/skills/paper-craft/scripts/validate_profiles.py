# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Validate packaged profiles: python3 validate_profiles.py [venues] --json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from venue_common import (
    DEFAULT_ROOT,
    IDENTITY_KEYS,
    JSONValue,
    ProfileError,
    mapping,
    read_json,
    registry,
    validate_profile,
)


def audit(root: Path) -> dict[str, JSONValue]:
    """Check the registry and every profile, including duplicate identities."""
    findings: list[JSONValue] = []
    count = 0
    identities: set[str] = set()
    try:
        entries = registry(root)
        for entry in entries:
            paths, domains = entry["profiles"], entry["official_domains"]
            if not isinstance(paths, list) or not isinstance(domains, list):
                raise ProfileError("invalid registry entry")
            for relative in paths:
                path = root / str(relative)
                profile = mapping(read_json(path), str(path))
                errors = validate_profile(profile, [str(domain) for domain in domains])
                if profile.get("venue_id") != entry["venue_id"]:
                    errors.append("venue_id differs from registry")
                if profile.get("publication_type") != entry["publication_type"]:
                    errors.append("publication_type differs from registry")
                identity = json.dumps([profile.get(key) for key in IDENTITY_KEYS])
                if identity in identities:
                    errors.append("duplicate venue/year/track/stage profile")
                identities.add(identity)
                count += 1
                findings.append({
                    "check": "profile_schema_and_provenance", "status": "FAIL" if errors else "PASS",
                    "severity": "Major" if errors else "Suggestion", "file": str(path), "line": None,
                    "message": "; ".join(errors) if errors else "Profile structure and provenance valid; not a live rule verification.",
                })
    except ProfileError as error:
        findings.append({"check": "registry", "status": "FAIL", "severity": "Major",
                         "file": str(root), "line": None, "message": str(error)})
    failed = any(isinstance(item, dict) and item.get("status") == "FAIL" for item in findings)
    return {"tool": "validate_profiles", "status": "FAIL" if failed else "PASS",
            "profile_count": count, "findings": findings}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = parser.parse_args()
    report = audit(args.path)
    print(json.dumps(report, ensure_ascii=False, indent=2) if args.json else
          f"{report['status']}: {report['profile_count']} profiles\n" + "\n".join(
              f"{item['status']}: {item['file']}: {item['message']}"
              for item in report["findings"] if isinstance(item, dict)
          ))
    return 1 if report["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
