# Academic Editor and short-letter compression

Use for English or Korean manuscript editing. Read [argumentation.md](../core/argumentation.md), [evidence.md](../core/evidence.md), and [inputs-and-tools.md](inputs-and-tools.md). Preserve the manuscript's language unless translation was requested.

For a venue-targeted manuscript, consult the exact current AI rule before proposing whole-section replacements. Preserve author-led drafting and limit assistance to the permitted scope when the official rule distinguishes editing from AI writing. Do not fabricate disclosure or human-written attestations; record actual assistance for author review.

## Modes and authorization

- **Review Only** diagnoses defects and writes a report; manuscript files remain unchanged. Use when the user asks for review without editing.
- **Suggest Edits** presents original/revised text, rationale, technical meaning risk, and unified diff, with no manuscript changes. Use by default for proofreading, rewriting, or compression unless exact edits are already approved.
- **Apply Approved Edits** applies only the agreed patch or concretely authorized edits. Preserve the original snapshot/hash and keep the diff reviewable. Approval persists for that agreed scope; it does not authorize newly discovered technical changes.

In an isolated output directory, record source paths and hashes before editing and assign edit IDs. Avoid overwriting user files with proposed revisions. A request to show suggestions first is not authorization to modify originals. If the authorized patch conflicts with changed source content, inspect the conflict and prepare an updated proposal rather than forcing it.

## Five passes, with one scientific state

Reuse the current hash-bound argument graph and stable claim/finding IDs across editing, technical review, and reviewer simulation. Before reusing it, run `argument_graph.py validate GRAPH --project-root ROOT --check-inputs --json`; structural validation alone does not establish current inputs or scientific validity. If the input hashes changed, update the graph and reassess affected claims before relying on earlier findings. Narrow language tasks need only the affected claim/context scope, not a fabricated full graph.

1. **Claim and technical meaning:** identify each affected claim, its evidence, assumptions, scope, qualifiers, comparison direction, and number-to-entity associations. Establish what the original actually asserts before proposing wording.
2. **Logic:** inspect the inference from evidence to claim, missing premises, contradictions, causation and scope. Keep research validation tasks separate from prose polish. A weaker sentence does not repair an invalid experiment.
3. **Paragraph structure:** establish the controlling idea; arrange topic, evidence, explanation, limitation and transition. Review how moving sentences changes context and associations; preserve information needed to interpret experiments.
4. **Language:** improve precise academic English or Korean, terminology, references and concision while preserving technical meaning. Passive voice and first person are choices, not unconditional defects.
5. **Re-evaluate claims and evidence:** reread affected paragraphs and graph dependencies against the originals. Check whether edits changed support, assumptions, numerical associations, confidence or scope; update the shared findings explicitly. Record actual performed and unperformed checks. Author/agent scientific judgment remains separate from static guard output.

Assign every proposed edit one or more categories: `language_only`, `structural`, `claim_qualification`, `technical_correction`, `evidence_alignment`. Record affected stable claim IDs, evidence, assumptions and scope impact. A language-only label requires contextual review; identical numeric counts are insufficient. Do not silently weaken a claim to hide an evidence gap, turn model/simulation predictions into measured results (including PoTAL-type comparisons), or relabel manuscript-reported evidence as independently reproduced. Qualifying or correcting a claim is visible scientific work with its own approval and evidence, even if the wording becomes shorter.

## Protected content and diff

Retain numbers, units, negation, comparison directions, uncertainty, experimental conditions, equation meaning, identifiers, BibTeX keys, LaTeX labels, references, and command structure. If a correction to any protected content is needed, separate it as a technical change with source evidence and explicit author approval. Reordering scientific claims can also alter scope or emphasis; review the whole paragraph.

Generate a unified diff against the untouched source using `difflib.unified_diff` or equivalent tooling. Record **Location; Original; Revised; Revision Rationale; Technical Meaning Risk; Approval State; Verification; Categories; Claim IDs; Evidence; Assumptions; Scope Impact**. Use [edit-ledger.csv](../../assets/edit-ledger.csv) for tracking. Do not present an unapplied patch as applied.

Run `python3 scripts/editing_guard.py /absolute/original.tex /absolute/revised.tex --json` from the skill directory. Inspect every FAIL, SKIPPED and UNKNOWN item, `semantic_signals`, and `touched_contexts`. Per-sentence and nearby-number context hints include basic English/Korean negation, comparison, causality, confidence and evidence-source terms. They can miss changes and produce false positives; they are review prompts, not scientific-error assertions. A swap from A=10 ns/B=20 ns to A=20 ns/B=10 ns requires manual association review despite equal numeric bags. Static checks never prove semantic equality: `semantic_review` stays `MANUAL_REQUIRED`, while protected-token differences still fail. Run the LaTeX/reference tools on the approved revised project, compare build diagnostics if available, and manually inspect affected context and rendered equations/figures. Never label missing build or PDF checks as passed.

## CAL and other short formats

Obtain the exact official target profile before claiming a length target. Preserve the core contribution, sufficient method description, fair comparison, decisive evidence, uncertainty, limitations, and citations needed to support novelty. Compress duplicated motivation, incidental detail, and verbose prose first. Propose moving detail only when the exact appendix/supplement policy permits it.

Return **Core Contribution; Content to Remove or Compress; Evidence to Preserve; Condensed Paragraph Suggestions; Official Length Verification Status; Unified Diff**. When no verified limit is available, provide a contribution-preserving compression plan without inventing a page count or asserting compliance.
