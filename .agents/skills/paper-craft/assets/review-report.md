# Paper Craft review

## Scope and verification

- Task and mode:
- Manuscript root, associated files, and locations actually read:
- Input hashes where relevant:
- Domain; manuscript language:
- Target venue/year/track/stage, profile, official sources and dates:
- Missing materials, retrieval restrictions, and skipped checks:
- Research observations versus hypotheses:
- Verification scope: checks actually performed; checks unperformed (separate from support state):
- Current argument graph or reference, input hashes, stable claim IDs and source locators (when relevant):
- Graph freshness verification command/result; changed inputs and resulting state updates:
- Provenance kind, artifact locators and actual reproduction run locator; do not promote reported/simulated results to measurement:

For structured output, use `schema_version: 2` with [review-report.schema.json](../schemas/review-report.schema.json), then run `python3 scripts/validate_review_report.py review.json --json`. Unversioned and explicit version 1 reports remain readable. V2 retains `evidence_state`, and adds `verification_scope`, `provenance`, and `evidence_axes` to findings/claims; findings also carry `claim_ids`. Inputs have stable `id` values. Provenance and scope do not replace support state. Validator PASS means valid metadata structure, never valid science; graph references and hashes still need the graph tool's current-input check.

## Findings

| ID | Location | Category | Severity | Actual evidence | Explanation and impact | Improvement / required material | Evidence state |
| --- | --- | --- | --- | --- | --- | --- | --- |

## Evidence axes and finding updates

| Claim / finding ID | Evidence existence: status, rationale, locator | Evidence validity: status, rationale, locator | Inference sufficiency: status, rationale, locator | Provenance | Performed / unperformed verification |
| --- | --- | --- | --- | --- | --- |

| Finding ID | Previous / current state | New material and locator | Reason for update | Related graph IDs |
| --- | --- | --- | --- | --- |

## Edit classification

For each edit record one or more of `language_only`, `structural`, `claim_qualification`, `technical_correction`, `evidence_alignment`, affected claim IDs, evidence, assumptions and scope impact. Preserve originals/diffs and author approval scope. Separately list research validation tasks and presentation changes. A model prediction must not become a measured result through polishing.

## Task-specific results

Include only requested sections: Research Design Review; Argument Map and Outline; Novelty Audit; Claim–Evidence Matrix; Architecture/Systems Technical Review; Academic Editing Suggestions; Reviewer Simulation and Response Preparation; Venue Compliance; Submission Preflight.

Keep official requirements, observed style, and independent methodological recommendations explicitly separate. Proposed experiments have no claimed outcomes. Simulation is not an actual review or acceptance prediction.

## Checks actually performed

| Check | Result: PASS/FAIL/SKIPPED/UNKNOWN | Evidence / command / dependency | Limits |
| --- | --- | --- | --- |

## Next actions

Prioritize research validation, correctness, and mandatory verified requirements before presentation changes. Identify approvals needed only for specific proposed manuscript modifications.
