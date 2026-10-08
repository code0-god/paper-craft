# Submission Preflight

Use only the exact publication/venue/year/track/stage context. Follow the venue guide linked from SKILL.md for profile selection and source precedence. Never reuse submission rules as camera-ready rules or an older year's limits as current verified limits.

## Prepare the check inventory

List manuscript root and associated files, target identity, selected profile, official sources, last verification dates, and any offline or conflicting constraints. A cached official rule may inform a review while remaining unverified for the current request. UNKNOWN means unresolved, not noncompliant or compliant.

Run the package's read-only tools from the skill directory:

```bash
python3 scripts/latex_integrity_check.py /absolute/project/main.tex --project-root /absolute/project --json
python3 scripts/reference_audit.py /absolute/project/main.tex --json
python3 scripts/venue_preflight.py --help
```

Use the actual venue-preflight CLI described by its help output; provide exact target metadata, never guessed profile selectors. If build/PDF checks are authorized and available, use `--build` or `--pdf` on the LaTeX tool. Builds must use an isolated copy/output directory and shell escape must remain disabled; inspect the implementation's supported safety limits before building untrusted projects.

## Automatic and manual results

| Check | Appropriate evidence and limits |
| --- | --- |
| Page/reference/appendix policy | Exact verified official rule plus rendered PDF; determine counted sections manually when boundaries are ambiguous. |
| Official template | Document class/options and official template/version; static detection does not establish typography or legal compliance. |
| Anonymity; author/affiliation | Manual inspection of text, acknowledgments, citations, URLs, supplement, PDF metadata, and artifacts against target rules. Do not infer anonymity from an empty author command alone. |
| References | Resolved keys and independently checked bibliographic facts; no fabricated citation repairs. |
| Equations; figures/tables | Static duplicate labels, unresolved references, included-file paths; rendered placement and semantic correctness remain manual. |
| LaTeX warnings | Actually produced compiler logs, including undefined references, overfull boxes, missing glyphs/assets; absence of a build is SKIPPED. |
| AI use; ethics | Exact current publisher/venue disclosure rules plus author confirmation of actual use. Do not treat this guide as a policy. |
| File and supplementary package | Actual required uploads/formats and checked file manifest; external upload is separate authorization. |
| Reproducibility; artifact | Target-stage rules plus actual implementation/data/environment documentation, availability limits, and artifact contents. Artifact evaluation can be optional or have a separate deadline. |

For deterministic checks use PASS/FAIL/SKIPPED/UNKNOWN with evidence and reasons. For manual checks use UNKNOWN until actually inspected; a suggested checklist is not a completed check. If `latexmk`, a TeX distribution, or a PDF parser is missing, report SKIPPED with the missing dependency. No aggregate “ready” or “compliant” result when mandatory checks remain unknown.

Return **Target and Profile; Applied Official Rules; Automatic Results; Manual Results; Unknown/Conflicting Rules; Blocking Issues; Author Actions**. Link each rule to its URL, verified date, applicability, and status. Keep style recommendations separate from official obligations.
