# Paper Craft verification record

Executed 2026-10-08 on macOS, Python 3.14.6, Codex CLI 0.160.0. Runtime scripts use only Python standard library. Python 3.10 compatibility was checked by syntax parsing and configured type checking; a Python 3.10 interpreter run was not performed.

## Automated checks actually run

| Command / surface | Observed result | Scope |
| --- | --- | --- |
| `python3 -m unittest discover -s tests -q` | **56 tests PASS**, 13.672 seconds | 21 manuscript tests, 20 venue tests, 7 package tests, 8 independent-audit regression tests |
| `python3 .agents/skills/paper-craft/scripts/validate_skill.py --json` | **PASS**, no findings | This package's scalar YAML subset, UI metadata, internal Markdown links, standalone resources, Python 3.10 syntax, JSON syntax |
| Bundled OpenAI `skill-creator/scripts/quick_validate.py` | **Skill is valid!** | Official bundled validator, run using cached PyYAML in a temporary development environment; no runtime dependency added |
| `python3 .agents/skills/paper-craft/scripts/validate_profiles.py --json` | **PASS**, 18 profiles | Exact identities, registry paths, required rules, provenance/status/type consistency; not live policy certification |
| `uvx --offline ruff check .agents/skills/paper-craft/scripts tests` | **All checks passed!** | Ruff 0.16.10, configured E4/E7/E9/F/I rules; offline cached development tool |
| `uvx --offline basedpyright` | **0 errors, 0 warnings, 0 notes** | Basedpyright 1.40.1, Python 3.10 target, standard mode; offline cached development tool |
| Python AST handler inspection | No bare or broad `Exception` / `BaseException` handlers | Packaged Python scripts; no external static-analysis dependency |

The copied-directory tests execute validators, LaTeX/citation tools, and exact-profile offline preflight from outside this repository. They require no attachments or source-materials directory. Install/update tests verify existing user content survives in a backup outside the normal `skills/` discovery directory. Source, bibliography, and editing tests verify the read-only behavior and explicit UNKNOWN/SKIPPED states.

## Actual LaTeX build

Executed:

```bash
python3 .agents/skills/paper-craft/scripts/latex_integrity_check.py \
  tests/fixtures/latex/valid/main.tex --build --json
```

Exit 0. `latex_build`: **PASS**, private-copy pdflatex build completed without detected final-log warnings. Input SHA-256 before/after identical. Overall report **UNKNOWN** because reference semantics require manual review; PDF inspection **SKIPPED**, no PDF supplied and `pdfinfo` unavailable in this environment. Temporary build artifacts were not written into the source fixture. This build does not validate real venue templates, rendered anonymity, geometry, or a research implementation.

## Actual Codex invocation

Executed the local CLI with an explicit `$paper-craft` request:

```bash
codex exec --ephemeral --sandbox read-only -c model_reasoning_effort='"low"' --json \
  '$paper-craft Use this installed skill to review this research idea. Memory traffic slows accelerator inference. We combine a cache and a prefetcher. We have no experiments or closest-prior-work comparison. Output only a concise novelty audit with Problem, Challenge, Insight, Contribution, Prior Work Comparison, Missing Evidence, Recommended Next Steps. Do not edit files.'
```

Exit 0, `turn.completed`. Codex read the actual package entrypoint, novelty/domain guides and report schema. Its answer separated the proposed memory bottleneck, candidate coordination hypothesis, unestablished contribution, missing closest-work comparison, evidence gaps and proposed fair comparisons. It invented no measured results or named prior papers and made no manuscript edits. This is one observed semantic execution, not an acceptance guarantee or a statistical evaluation of routing reliability.

`codex debug prompt-input` also showed the skill in discovery context. That debugging surface did not expand the entire entrypoint into its emitted prompt; it is recorded only as discovery evidence. The `codex exec` run supplied the actual invocation evidence. Existing local user-config warnings (`env` ignored) and unrelated MCP transport 502 messages appeared in the run; they did not prevent the read-only task completing. User configuration and remote MCP services were not changed.

## Independent forward use and code audit

An independent agent applied the actual skill to synthetic multi-file LaTeX, research notes, Korean prose, operational-experience notes, and HTML. Its substantive local outputs are `tests/results/forward-tests.md`, `proposed.tex`, and `proposed.patch`. Generated reports and local evidence are intentionally Git-ignored; they are not expected-answer fixtures or files required by a fresh checkout. The agent did not read the scenario rubric before performing the reviews. Re-run the committed scenario prompts to create new reports.

Observed A–G outputs cover novelty, argument maps/paragraph outlines, English proposals with rationale/risk/diff, architecture evidence/baseline review, scoped venue preflight, CAL compression proposals, and reviewer/response simulation. Follow-up E actually opened the exact ISCA 2026 official guidelines (132 returned lines) and compared the directly stated rules with the profile. Linked publisher policies/template PDFs were not independently read; those checks remain limited. The earlier offline CLI report remains UNKNOWN. Additional checks cover Korean language preservation, nonalgorithmic systems contributions, missing experimental evidence, absent exact venue editions (including ISCA 2028 research camera-ready), unavailable PDF input, and inert synthetic source ingestion. See the forward report for exact per-case execution status; no blanket 12-case PASS is inferred from unit tests.

The actual English proposal retained all **9 protected token categories** (PASS). Semantic equivalence remained **UNKNOWN / MANUAL_REQUIRED**. Patch dry-run (`git apply --check -p0`) succeeded. Eight original manuscript/research input hashes remained unchanged. The proposal was not applied.

A separate read-only code audit reproduced eight defects: standalone BibTeX input ignored, directory symlink escaped the project boundary, leading decimal numeric changes missed, byte/bit unit changes missed, BibTeX key edits missed, contradictory template options falsely accepted, escaped TeX commands misparsed, and adjacent HTML paragraphs merged. Root/venue implementations corrected these with concrete regression coverage. The original eight reproductions were replayed after correction; all produced the expected outcome with **no remaining findings in that replay**. An additional regression verifies valid unified diffs for inputs without a final newline. This replay is bounded evidence, not a claim that every possible TeX construct is supported.

## Sources and profiles

- Reference A website actually read; separate user attachment absent. Short guide records headings and interpretation boundaries. Original not redistributed.
- Reference B actual HTML statically inspected: **PASS**, 259 inert blocks with original-line/section anchors, no script/style/noscript/template text. SHA-256 `8b7a3ac5746b44810f2fe7d86c3aab29f0c9aa6cb21846fb20cf3fb589ca43f9`; original 38,963-byte file preserved outside the package. License/authorship not authenticated beyond the supplied footer attribution.
- 16 venue IDs / 18 exact profiles. **99 verified historical rules**, **81 unverified rules**, including independently labeled methodological advice. **14 profiles across 12 IDs contain some verified official rules**; none is claimed fully verified for future submissions. TC/TACO/TOCS/TPDS official rules remain UNKNOWN after unavailable/403 author-page retrievals. CAL uses retrieved official indexed primary text with direct-fetch 403 disclosed. See [official-source inventory](../.agents/skills/paper-craft/references/venues/sources.md).

## Limits and unperformed checks

No real submitted paper or production experiment was supplied. The semantic examples are synthetic. No statistical claim about reviewer judgments, acceptance, scientific novelty, or model consistency is made. Real DOCX extraction/layout and real PDF rendering/geometry were **not run**; required tools/artifacts were unavailable. TeX macro expansion, conditional semantics, complex/generated bibliography structures, citation authenticity, complete anonymity, publisher form fields, ethics attestations and artifact reproducibility remain manual or require an appropriate tool. Static protected-token comparison cannot prove numerical associations or technical meaning.

Writing-style observations from representative venue papers were **not sampled**; profile observations are empty and independent methodological advice is explicitly labeled. No GitHub installation against a real remote was attempted because this repository has no remote. Local copied-directory installation was actually exercised. No publication, remote upload, commit, or global user-skill replacement was performed.
