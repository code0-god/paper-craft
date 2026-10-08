"""Read and validate versioned venue profiles without network access."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Final, TypeAlias
from urllib.parse import urlsplit

JSONValue: TypeAlias = (
    str | int | float | bool | None | list["JSONValue"] | dict[str, "JSONValue"]
)
DEFAULT_ROOT: Final = Path(__file__).resolve().parents[1] / "venues"
RULE_NAMES: Final = (
    "paper_length_policy", "reference_page_policy", "appendix_supplementary_policy",
    "template_requirements", "anonymity_requirements", "review_criteria",
    "ai_disclosure_requirements", "artifact_reproducibility_policy",
    "writing_style_guidance", "field_specific_evaluation_priorities",
)
OFFICIAL_TYPES: Final = frozenset({
    "call_for_papers", "submission_guidelines", "reviewer_guidelines",
    "official_template", "publisher_policy", "artifact_guidelines",
    "camera_ready_guidelines", "author_instructions",
})
SOURCE_TYPES: Final = OFFICIAL_TYPES | {"field_methodology", "observed_style", "unknown"}
STATUSES: Final = frozenset({"verified", "unverified", "outdated", "conflicting"})
IDENTITY_KEYS: Final = ("venue_id", "year", "track", "submission_stage")


class ProfileError(ValueError):
    """A venue package cannot safely be read or selected."""


def read_json(path: Path) -> JSONValue:
    """Read UTF-8 JSON; malformed or unavailable input remains an error."""
    try:
        value: JSONValue = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ProfileError(f"{path}: {error}") from error
    return value


def mapping(value: JSONValue, location: str) -> dict[str, JSONValue]:
    """Require an object at the JSON trust boundary."""
    if not isinstance(value, dict):
        raise ProfileError(f"{location}: expected JSON object")
    return value


def official_url(value: JSONValue, domains: list[str]) -> bool:
    """Require HTTPS and a registered official host, without user credentials."""
    if not isinstance(value, str):
        return False
    try:
        parsed = urlsplit(value)
        host = parsed.hostname or ""
        return (
            parsed.scheme == "https" and not parsed.username and not parsed.password
            and bool(parsed.path) and parsed.port in (None, 443)
            and any(host == domain or host.endswith("." + domain) for domain in domains)
        )
    except ValueError:
        return False


def valid_date(value: JSONValue) -> bool:
    """Reject invalid dates and dates later than today's local date."""
    if not isinstance(value, str):
        return False
    try:
        parsed = date.fromisoformat(value)
        return parsed.isoformat() == value and parsed <= date.today()
    except ValueError:
        return False


def registry(root: Path) -> list[dict[str, JSONValue]]:
    """Load registry entries, rejecting paths that escape the skill package."""
    data = mapping(read_json(root / "registry.json"), "registry")
    entries = data.get("venues")
    if data.get("schema_version") != 1 or not isinstance(entries, list) or not entries:
        raise ProfileError("registry: schema_version=1 and nonempty venues required")
    result: list[dict[str, JSONValue]] = []
    seen: set[str] = set()
    for raw in entries:
        entry = mapping(raw, "registry entry")
        venue = entry.get("venue_id")
        paths, domains = entry.get("profiles"), entry.get("official_domains")
        if not isinstance(venue, str) or not venue or venue in seen:
            raise ProfileError("registry: venue IDs must be unique nonempty strings")
        if not isinstance(entry.get("publication_type"), str) or entry.get("publication_type") not in {"conference", "journal"}:
            raise ProfileError(f"{venue}: invalid publication_type")
        if not isinstance(domains, list) or not domains or any(
            not isinstance(host, str) or not host or "/" in host or ":" in host
            for host in domains
        ):
            raise ProfileError(f"{venue}: invalid official_domains")
        if not isinstance(paths, list) or not paths:
            raise ProfileError(f"{venue}: nonempty profiles required")
        for path in paths:
            if not isinstance(path, str) or not path.endswith(".json"):
                raise ProfileError(f"{venue}: invalid profile path")
            resolved = (root / path).resolve()
            if not resolved.is_relative_to(root.resolve()) or not resolved.is_file():
                raise ProfileError(f"{venue}: missing or escaping profile path: {path}")
        seen.add(venue)
        result.append(entry)
    return result


def validate_profile(profile: dict[str, JSONValue], domains: list[str]) -> list[str]:
    """Validate schema fields and semantic provenance with no optional dependency."""
    required = {
        "schema_version", "venue_id", "publication_type", "year", "track",
        "submission_stage", "official_source_urls", "last_verified_date", "rules",
        "writing_style_observations", "notes",
    }
    errors = [f"missing field: {key}" for key in sorted(required - profile.keys())]
    errors.extend(f"unknown field: {key}" for key in sorted(profile.keys() - required))
    if profile.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    for key in ("venue_id", "track", "notes"):
        if not isinstance(profile.get(key), str) or not profile.get(key):
            errors.append(f"{key} must be a nonempty string")
    kind = profile.get("publication_type")
    if not isinstance(kind, str) or kind not in {"conference", "journal"}:
        errors.append("invalid publication_type")
    year = profile.get("year")
    if year is None:
        if kind != "journal":
            errors.append("only continuing journal profiles may have year=null")
    elif isinstance(year, bool) or not isinstance(year, int) or not 1900 <= year <= 2200:
        errors.append("year must be integer 1900..2200 or null for a continuing journal")
    if not isinstance(profile.get("submission_stage"), str) or profile.get("submission_stage") not in {"submission", "camera-ready", "revision"}:
        errors.append("invalid submission_stage")
    urls = profile.get("official_source_urls")
    if not isinstance(urls, list) or any(not official_url(url, domains) for url in urls):
        errors.append("official_source_urls must contain official HTTPS URLs")
    last = profile.get("last_verified_date")
    if last is not None and not valid_date(last):
        errors.append("invalid last_verified_date")
    observations = profile.get("writing_style_observations")
    if not isinstance(observations, list):
        errors.append("writing_style_observations must be a list")
    else:
        for item in observations:
            if not isinstance(item, dict) or set(item) != {"paper_url", "observation", "scope_limit"}:
                errors.append("style observations require paper_url, observation, scope_limit")
            elif any(not isinstance(item[key], str) or not item[key] for key in item):
                errors.append("style observation fields must be nonempty strings")
    rules = profile.get("rules")
    if not isinstance(rules, dict):
        return errors + ["rules must be an object"]
    errors.extend(f"missing rule: {key}" for key in RULE_NAMES if key not in rules)
    identity = {key: profile.get(key) for key in IDENTITY_KEYS}
    verified_dates: list[str] = []
    for key, raw in rules.items():
        if not isinstance(raw, dict):
            errors.append(f"{key}: rule must be an object")
            continue
        required_rule = {
            "value", "source_url", "source_type", "verified_at", "applies_to",
            "verification_status", "notes",
        }
        errors.extend(f"{key}: missing {field}" for field in sorted(required_rule - raw.keys()))
        errors.extend(f"{key}: unknown {field}" for field in sorted(raw.keys() - required_rule))
        status, source_type = raw.get("verification_status"), raw.get("source_type")
        if not isinstance(status, str) or status not in STATUSES or not isinstance(source_type, str) or source_type not in SOURCE_TYPES:
            errors.append(f"{key}: invalid verification_status or source_type")
            continue
        if raw.get("applies_to") != identity:
            errors.append(f"{key}: applies_to must exactly match profile identity")
        if not isinstance(raw.get("notes"), str) or not raw.get("notes"):
            errors.append(f"{key}: nonempty notes required")
        source, verified = raw.get("source_url"), raw.get("verified_at")
        if source is not None and (not official_url(source, domains) or not isinstance(urls, list) or source not in urls):
            errors.append(f"{key}: source must be registered official URL")
        if verified is not None and not valid_date(verified):
            errors.append(f"{key}: invalid verified_at")
        if status == "verified":
            if source_type == "unknown":
                errors.append(f"{key}: unknown source type cannot be verified")
            if source_type in OFFICIAL_TYPES and (source is None or raw.get("value") is None):
                errors.append(f"{key}: verified official rule needs source and value")
            if verified is None:
                errors.append(f"{key}: verified rule needs verified_at")
        if status in {"verified", "outdated"} and isinstance(verified, str):
            verified_dates.append(verified)
        if key not in {"writing_style_guidance", "field_specific_evaluation_priorities"}:
            if source_type not in OFFICIAL_TYPES and raw.get("value") is not None:
                errors.append(f"{key}: unknown/advisory source cannot establish official requirement")
        if status == "unverified" and source_type in OFFICIAL_TYPES and raw.get("value") is not None:
            errors.append(f"{key}: unverified official value must remain null (UNKNOWN)")
        if key == "paper_length_policy" and raw.get("value") is not None:
            value = raw["value"]
            if not isinstance(value, dict) or not isinstance(value.get("max_pages"), int):
                errors.append(f"{key}: value requires integer max_pages")
            elif isinstance(value["max_pages"], bool) or value["max_pages"] <= 0:
                errors.append(f"{key}: max_pages must be positive")
            if isinstance(value, dict) and "min_pages" in value:
                minimum, maximum = value["min_pages"], value.get("max_pages")
                if isinstance(minimum, bool) or not isinstance(minimum, int) or minimum <= 0:
                    errors.append(f"{key}: min_pages must be a positive integer")
                elif isinstance(maximum, int) and minimum > maximum:
                    errors.append(f"{key}: min_pages must not exceed max_pages")
            if isinstance(value, dict) and (not isinstance(value.get("basis"), str) or value.get("basis") not in {"all", "main"}):
                errors.append(f"{key}: basis must be all or main")
        if key == "template_requirements" and raw.get("value") is not None:
            value = raw["value"]
            if not isinstance(value, dict) or not isinstance(value.get("required"), bool):
                errors.append(f"{key}: value requires boolean required")
            elif value.get("documentclass") is not None and not isinstance(value.get("documentclass"), str):
                errors.append(f"{key}: documentclass must be string or null")
            if isinstance(value, dict) and (not isinstance(value.get("options"), list) or any(
                not isinstance(option, str) for option in value.get("options", [])
            )):
                errors.append(f"{key}: options must be string list")
    expected_last = max(verified_dates) if verified_dates else None
    if last != expected_last:
        errors.append("last_verified_date must equal newest verified rule date, or null")
    return errors


def select_profile(root: Path, identity: dict[str, JSONValue]) -> dict[str, JSONValue] | None:
    """Select exact venue/year/track/stage; never borrow another edition or track."""
    matches: list[dict[str, JSONValue]] = []
    for entry in registry(root):
        if str(entry["venue_id"]).casefold() != str(identity["venue_id"]).casefold():
            continue
        paths, domains = entry["profiles"], entry["official_domains"]
        if not isinstance(paths, list) or not isinstance(domains, list):
            raise ProfileError("invalid registry entry")
        for relative in paths:
            profile = mapping(read_json(root / str(relative)), str(relative))
            errors = validate_profile(profile, [str(domain) for domain in domains])
            if profile.get("venue_id") != entry["venue_id"] or profile.get("publication_type") != entry["publication_type"]:
                errors.append("profile identity/type differs from registry")
            if errors:
                raise ProfileError(f"{relative}: {'; '.join(errors)}")
            if all(profile[key] == identity[key] for key in IDENTITY_KEYS if key != "venue_id"):
                matches.append(profile)
    if len(matches) > 1:
        raise ProfileError("duplicate profiles for exact venue/year/track/stage")
    return matches[0] if matches else None


def applicability(rule: dict[str, JSONValue], offline: bool, today: date | None = None) -> str:
    """Cached provenance is historical; offline, stale, conflicting rules are UNKNOWN."""
    verified = rule.get("verified_at")
    if offline or rule.get("verification_status") != "verified" or not isinstance(verified, str):
        return "UNKNOWN"
    age = ((today or date.today()) - date.fromisoformat(verified)).days
    return "CACHED" if 0 <= age <= 90 else "UNKNOWN"
