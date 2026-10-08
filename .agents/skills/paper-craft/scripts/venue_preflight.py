# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Read-only venue checks: python3 venue_preflight.py MANUSCRIPT --venue ID --year YYYY --track research --stage submission --offline --json."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path

from manuscript_common import InputError, load_project
from venue_common import DEFAULT_ROOT, JSONValue, ProfileError, applicability, select_profile


def preflight(args: argparse.Namespace) -> dict[str, JSONValue]:
    """Report static observations separately from historical rules and manual checks."""
    findings: list[JSONValue] = []
    manuscript: Path = args.manuscript
    identity: dict[str, JSONValue] = {
        "venue_id": args.venue.upper(), "year": args.year, "track": args.track,
        "submission_stage": args.stage,
    }

    def add(check: str, status: str, message: str, **details: JSONValue) -> None:
        findings.append({"check": check, "status": status,
                         "severity": "Major" if status == "FAIL" else "Suggestion",
                         "file": str(manuscript), "line": None, "message": message, **details})

    profile: dict[str, JSONValue] | None = None
    try:
        profile = select_profile(args.profile_root, identity)
    except ProfileError as error:
        add("profile_selection", "FAIL", str(error))
    if not manuscript.exists():
        add("input", "FAIL", "Manuscript path does not exist.")
    else:
        add("input", "PASS", "Manuscript exists; input remains read-only.")
    if profile is None:
        if not any(isinstance(item, dict) and item["status"] == "FAIL" for item in findings):
            add("profile_selection", "UNKNOWN", "No exact venue/year/track/stage profile. No fallback applied.")
        return result(identity, profile, findings)
    add("profile_selection", "PASS", "Exact venue/year/track/stage profile selected.")
    add("current_rules", "UNKNOWN", "Offline cache only." if args.offline else
        "This tool does not fetch policies. Agent must recheck official sources before submission.")
    rules = profile["rules"]
    if not isinstance(rules, dict):
        raise ProfileError("rules must be an object")
    for name, raw in rules.items():
        if isinstance(raw, dict):
            add(name, "UNKNOWN", "Manual or agent verification required; cached rule is not current certification.",
                cached_value=raw["value"], provenance_status=raw["verification_status"],
                cached_applicability=applicability(raw, args.offline), source_url=raw["source_url"],
                verified_at=raw["verified_at"], source_type=raw["source_type"])
    template = rules.get("template_requirements")
    if isinstance(template, dict):
        check_template(manuscript, template, args.offline, findings)
    pdf: Path | None = args.pdf
    if pdf is None and manuscript.suffix.lower() == ".pdf":
        pdf = manuscript
    length = rules.get("paper_length_policy")
    if pdf is not None and isinstance(length, dict):
        check_pdf(pdf, length, args.offline, findings)
    else:
        add("pdf_page_count", "SKIPPED", "No PDF supplied; TeX source cannot prove rendered page count.")
    for check, message in (
        ("anonymization_manual", "Inspect rendered names, affiliations, PDF metadata, acknowledgments, self-citations, and artifact links."),
        ("format_manual", "Inspect template version, fonts, margins, figures, equations, and reference style in rendered PDF."),
        ("artifact_manual", "Check artifact contents, availability, anonymity, badges, and cycle-specific deadlines."),
        ("ai_policy_manual", "Check exact target AI policy and researcher disclosure; policies differ across venues."),
    ):
        add(check, "UNKNOWN", message)
    return result(identity, profile, findings)


def result(identity: dict[str, JSONValue], profile: dict[str, JSONValue] | None,
           findings: list[JSONValue]) -> dict[str, JSONValue]:
    """Never certify complete submission compliance from partial static checks."""
    failed = any(isinstance(item, dict) and item.get("status") == "FAIL" for item in findings)
    return {"tool": "venue_preflight", "status": "FAIL" if failed else "UNKNOWN",
            "target": identity, "profile": profile, "current_rules_verified": False,
            "submission_compliance": "UNKNOWN", "findings": findings}


def check_template(manuscript: Path, rule: dict[str, JSONValue], offline: bool,
                   findings: list[JSONValue]) -> None:
    """Check literal class/options only; macros and rendered geometry require review."""
    if manuscript.is_dir() or manuscript.suffix.lower() != ".tex":
        findings.append({"check": "template_setting", "status": "UNKNOWN", "severity": "Suggestion",
                         "file": str(manuscript), "line": None,
                         "message": "Pass an explicit root .tex file for literal template checks; directory inputs require manual entry selection."})
        return
    candidates: list[tuple[Path, str, re.Match[str]]] = []
    try:
        project = load_project(manuscript)
        for tex in project.files:
            match = re.search(r"\\documentclass\s*(?:\[([^\]]*)\])?\s*\{([^{}]+)\}", tex.text)
            if match:
                candidates.append((tex.path, tex.text, match))
    except InputError as error:
        findings.append({"check": "template_setting", "status": "FAIL", "severity": "Major",
                         "file": str(manuscript), "line": None, "message": str(error)})
        return
    expected = rule.get("value")
    status, message = "UNKNOWN", "No unique literal LaTeX documentclass or verified required class in cached profile."
    file, line = str(manuscript), None
    uncertain = any(item["check"] in {"conditional_commands", "include_graph", "include_path"} for item in project.findings)
    if len(candidates) == 1 and not uncertain:
        path, text, match = candidates[0]
        file, line = str(path), text.count("\n", 0, match.start()) + 1
        actual_class = match.group(2).strip()
        options = {option.strip() for option in (match.group(1) or "").split(",")}
        message = f"Observed class={actual_class}; options={','.join(sorted(options))}."
        if isinstance(expected, dict) and expected.get("required") is True and expected.get("documentclass"):
            required_options = expected.get("options", [])
            same = actual_class == expected["documentclass"] and isinstance(required_options, list) and set(
                str(option) for option in required_options
            ).issubset(options)
            status = ("PASS" if same else "FAIL") if applicability(rule, offline) == "CACHED" else "UNKNOWN"
            if isinstance(required_options, list) and any(
                "=" in option and option.split("=", 1)[0].strip() in required_options
                for option in options
            ):
                status = "UNKNOWN"
                message += " Required flag also has an explicit value; conflicting/valued option semantics need manual inspection."
            message += " Compared only with cached literal settings; rendered compliance and current rules remain UNKNOWN."
    findings.append({"check": "template_setting", "status": status,
                     "severity": "Major" if status == "FAIL" else "Suggestion",
                     "file": file, "line": line, "message": message,
                     "source_url": rule.get("source_url")})


def check_pdf(pdf: Path, rule: dict[str, JSONValue], offline: bool,
              findings: list[JSONValue]) -> None:
    """Use optional pdfinfo; never mistake total pages for technical-content pages."""
    executable = shutil.which("pdfinfo")
    status, message, pages = "SKIPPED", "pdfinfo not installed; install Poppler to count PDF pages.", None
    if not pdf.is_file():
        status, message = "FAIL", "PDF path does not exist or is not a file."
    elif executable:
        try:
            completed = subprocess.run([executable, str(pdf.resolve())], capture_output=True,
                                       text=True, timeout=30, check=False)
            match = re.search(r"^Pages:\s+(\d+)\s*$", completed.stdout, re.MULTILINE)
            if completed.returncode or match is None:
                status, message = "FAIL", "pdfinfo failed or returned no page count."
            else:
                pages = int(match.group(1))
                status, message = "PASS", f"Observed total PDF pages: {pages}."
                policy = rule.get("value")
                if isinstance(policy, dict) and policy.get("basis") == "all":
                    limit = policy.get("max_pages")
                    if isinstance(limit, int):
                        status = ("PASS" if pages <= limit else "FAIL") if applicability(rule, offline) == "CACHED" else "UNKNOWN"
                        message += f" Cached all-pages limit: {limit}; current-policy certification remains UNKNOWN."
                else:
                    status = "UNKNOWN"
                    message += " Content/reference/appendix boundaries require manual rendered-page inspection."
        except (OSError, UnicodeError, subprocess.TimeoutExpired) as error:
            status, message = "FAIL", f"PDF inspection failed: {error}"
    findings.append({"check": "pdf_page_count", "status": status,
                     "severity": "Major" if status == "FAIL" else "Suggestion",
                     "file": str(pdf), "line": None, "message": message,
                     "observed_total_pages": pages, "source_url": rule.get("source_url")})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manuscript", type=Path)
    parser.add_argument("--venue", required=True)
    parser.add_argument("--year", type=int, help="Required for conference editions; omit for continuing journals")
    parser.add_argument("--track", required=True, help="Exact registry track, e.g. research or letter")
    parser.add_argument("--stage", choices=("submission", "camera-ready", "revision"), default="submission")
    parser.add_argument("--profile-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--pdf", type=Path)
    parser.add_argument("--json", action="store_true")
    report = preflight(parser.parse_args())
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if any(isinstance(item, dict) and item.get("check") == "input" and item.get("status") == "FAIL"
           for item in report["findings"]):
        return 2
    return 1 if report["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
