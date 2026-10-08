# Academic Editor and short-letter compression

Use for English or Korean manuscript editing. Read [argumentation.md](../core/argumentation.md), [evidence.md](../core/evidence.md), and [inputs-and-tools.md](inputs-and-tools.md). Preserve the manuscript's language unless translation was requested.

For a venue-targeted manuscript, consult the exact current AI rule before proposing whole-section replacements. Preserve author-led drafting and limit assistance to the permitted scope when the official rule distinguishes editing from AI writing. Do not fabricate disclosure or human-written attestations; record actual assistance for author review.

## Modes and authorization

- **Review Only** diagnoses defects and writes a report; manuscript files remain unchanged. Use when the user asks for review without editing.
- **Suggest Edits** presents original/revised text, rationale, technical meaning risk, and unified diff, with no manuscript changes. Use by default for proofreading, rewriting, or compression unless exact edits are already approved.
- **Apply Approved Edits** applies only the agreed patch or concretely authorized edits. Preserve the original snapshot/hash and keep the diff reviewable. Approval persists for that agreed scope; it does not authorize newly discovered technical changes.

In an isolated output directory, record source paths and hashes before editing and assign edit IDs. Avoid overwriting user files with proposed revisions. A request to show suggestions first is not authorization to modify originals. If the authorized patch conflicts with changed source content, inspect the conflict and prepare an updated proposal rather than forcing it.

## Three passes

1. **Logical:** flag contradictions, missing evidence, unsupported causation, overbroad scope, repetitions, or absent intermediate reasoning. Classify research/experiment defects as validation tasks. Qualifying a claim may change its technical meaning; show the risk explicitly, even when the qualification is justified.
2. **Structural:** establish each paragraph's controlling idea; arrange topic, evidence, explanation, limitation, and transition; place design context before dependent results; connect figures/tables to the claim. Preserve information needed to interpret experiments.
3. **Language:** improve precise academic English or Korean, reduce empty modifiers and convoluted passive voice when appropriate, resolve ambiguous pronouns, unify terminology/abbreviations, and clarify sentence relationships. Preserve technical detail rather than simplifying it away. Passive voice and first person are choices, not unconditional defects.

## Protected content and diff

Retain numbers, units, negation, comparison directions, uncertainty, experimental conditions, equation meaning, identifiers, BibTeX keys, LaTeX labels, references, and command structure. If a correction to any protected content is needed, separate it as a technical change with source evidence and explicit author approval. Reordering scientific claims can also alter scope or emphasis; review the whole paragraph.

Generate a unified diff against the untouched source using `difflib.unified_diff` or equivalent tooling. Record **Location; Original; Revised; Revision Rationale; Technical Meaning Risk; Approval State; Verification**. Use [edit-ledger.csv](../../assets/edit-ledger.csv) for tracking. Do not present an unapplied patch as applied.

Run `python3 scripts/editing_guard.py /absolute/original.tex /absolute/revised.tex --json` from the skill directory. Inspect every FAIL or SKIPPED item; static token checks cannot prove semantic equality. Run the LaTeX/reference tools on the approved revised project, compare build diagnostics if available, and manually inspect affected context and rendered equations/figures. Never label missing build or PDF checks as passed.

## CAL and other short formats

Obtain the exact official target profile before claiming a length target. Preserve the core contribution, sufficient method description, fair comparison, decisive evidence, uncertainty, limitations, and citations needed to support novelty. Compress duplicated motivation, incidental detail, and verbose prose first. Propose moving detail only when the exact appendix/supplement policy permits it.

Return **Core Contribution; Content to Remove or Compress; Evidence to Preserve; Condensed Paragraph Suggestions; Official Length Verification Status; Unified Diff**. When no verified limit is available, provide a contribution-preserving compression plan without inventing a page count or asserting compliance.
