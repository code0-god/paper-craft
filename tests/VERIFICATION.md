# Paper Craft verification record

## Scientific review improvement — current verification, 2026-10-08

Baseline was commit `bf070bc` on `main`: Python **70 PASS**, Node **38 PASS**,
no existing test failure. The only pre-existing untracked data was `output/`.
All four original review files still have their baseline SHA-256 hashes; they
were not modified, moved or deleted. `output/` is now ignored. No GitHub push,
npm publication or user-host configuration change occurred during this work.

### Final automated checks actually run

| Check | Observed result | Scope |
|---|---|---|
| `python3 -m unittest discover -s tests -q` | **134 PASS**, 14.006 s, Python 3.14.6 | Existing tests plus scientific graph, report, uncertainty, output, editing, numerical, PDF and atlas regressions |
| `uv run --offline --no-project --python 3.10 python -m unittest discover -s tests -q` | **134 PASS**, 10.903 s, Python 3.10.21 | Actual minimum Python runtime execution, not only syntax parsing |
| `npm test` | **38 PASS**, 6.180 s, Node 26.7.0 | Actual tarball packaging, isolated local/global installs, offline npm/npx, eight host targets and backup integrity |
| Node 18.20.8 `npm test` | **38 PASS**, 5.433 s | Actual supported Node 18 execution with the expanded payload; no registry publication |
| Node 22.23.2 `npm test` | **38 PASS** in Phase A | Portability changes tested before the Python-only scientific additions; later payload not separately rerun on Node 22 |
| `npm run check`; `git diff --check` | **PASS** | Four Node source/test syntax checks; whitespace |
| `uvx --offline ruff check .`; `uvx --offline basedpyright` | **PASS**; **0 errors / 0 warnings / 0 notes** | Ruff 0.16.10, basedpyright 1.40.1; development tools, no new runtime dependencies |
| Skill/Profile/Writing-pattern validators | **PASS** | Standalone links/Python 3.10 syntax; 23 profiles/18 venues; four papers/12 bounded observations |
| Graph template and v2 report validators | **Structure PASS**, scientific/reuse status **UNKNOWN** | Empty assertion-free graph template and real v2 fixture; legacy reports also accepted |
| Draft 2020-12 JSON Schema checks | **PASS** | All schemas checked; legacy/v2 reports, graph template and writing atlas validated using cached optional development `jsonschema` |
| SHA-pinned GitHub Actions workflow / actionlint 1.7.12 | **PASS** | Syntax/expressions checked after new validators were integrated; ShellCheck not run |
| Final npm pack dry-run | **86 public files**, 117,077 compressed bytes | Swift helper and new standalone resources included; no `output/`, test data or local evidence |

The automated CI matrix defines Ubuntu/macOS/Windows with Python 3.10/3.14 and
Node 22, plus Ubuntu Node 18/26. **Hosted CI, Ubuntu and Windows execution were
not performed.** Native PDF tests skip only when their optional tool capability
is unavailable. Portable PDF seams retain product outcome checks; they do not
claim actual Poppler or Windows integration.

### Defect reproduction and fixes

- Unrelated macros previously suppressed definite missing labels/citation keys.
  Failing regressions preceded the scoped producer/conditional implementation;
  literal closed graphs now FAIL missing symbols, while dynamic/external cases
  retain uncertainty. Macro-produced literal candidates affect their own names.
- Independent review reproduced an `includeonly` false positive against actual
  successful `pdflatex` partial builds using cached auxiliary labels. Two new
  label/citation subcases failed before the fix. Excluded includes now explicitly
  leave their auxiliary symbol source unresolved. Ordinary missing symbols still
  fail in closed graphs. Auxiliary TeX is not executed by the static checker.
- Missing/timed-out Git originally returned an empty output-warning list. Both
  new failure cases failed before the fix and now explicitly warn that tracking
  could not be checked. Ordinary non-repository destinations remain supported.
- Initial PDF test executables used POSIX shebangs, incompatible with Windows
  discovery/execution. Controlled tool availability/subprocess seams now exercise
  the actual CLI parser and report, while native macOS installation/CLI tests
  remain real. A test asserting the fixture's implementation was removed after
  independent review; all **16 meaningful PDF outcome tests** remain.
- Graph validators reject overlapping performed/unperformed scopes and stale
  hashes. Report v2 preserves the six legacy evidence states while adding source
  provenance, independent evidence axes, claim references and edit categories.

Independent review initially requested changes for three concrete defects; all
were fixed and re-audited. Final verdict **CLEAR / APPROVE**, no blockers.
Local artifact: `.omo/evidence/scientific-code-review.md`.

### Scientific review behavior actually executed

Nine fresh, isolated Codex CLI sessions used `gpt-6.1-sol` with high reasoning:
A/B/C twice each and three negative controls once each. All exited 0 with
`turn.completed`; complete-response assessment found **43 substantive criterion
observations PASS** under the manifest and no listed hard failure. One ancillary
false-positive quality-claim attribution was subsequently identified and corrected
as described below; A-r1's overall review quality is therefore **QUALIFIED**.
This is a finite controlled sample, not a reliability score. Reviewing sessions did not receive the evaluator
manifest or other cases. Original inputs and installed Skill trees stayed identical
within each run.

| Case | Observed scientific decision | Verification limit |
|---|---|---|
| Per-row versus stripe-shared | Finds the row-common alternative, explicitly changes quantization granularity, separates factoring from hardware/quality costs, identifies the necessity argument gap | No invented comparison or claim that per-row is superior; actual hardware/accuracy unknown |
| INT32 saturation | Both runs executed local Python arithmetic and the bundled checker: fragment result **-1**, joint result **0**; final clipping retains mismatch | Disproves the unrestricted synthetic identity, not actual RTL correctness or workload reachability |
| Modeled versus measured latency | Rejects measured end-to-end wording and omission-only lower-bound inference; requires component bounds, schedule/overlap and model calibration | No timing values or experiments invented; model and full-path measurement unperformed |
| Supported fixed-interface design | Accepts the narrow simulated comparison and valid interface constraint; permits integration contribution | No global novelty, universal superiority or hardware measurement claim |
| Untested systems hypothesis | Defers utility/novelty judgment and proposes mechanism-specific verification | Missing evidence is not proof of a wrong idea |
| Numeric-preserving semantic edit | Finds swapped method/value associations, model-to-hardware provenance and unjustified causal strengthening; keeps approval requirements | Token preservation never proves scientific meaning |

A separate combined six-exercise invocation passed as an integration smoke; it
is not counted as six fresh sessions. Exact raw prompts, responses, model/tool
versions, hashes and substantive source/response locators are kept under
`.omo/evidence/scientific-model/isolated/`. Initial installer refusals caused by
temporarily unavailable integration links were retained and recovered after the
Skill validator passed. Unrelated configured MCP 502 diagnostics did not prevent
successful turns; no user configuration was changed.

Two additional fresh sessions reviewed the **same source hash** in Argumentation
and Suggest Edits modes, bringing formal executions to **11 sessions**. Both
passed 12 substantive cross-mode checks, preserved C1/C2/C3 meanings and source
locations, rechecked the prior report's hashes and ran fresh mathematical checks.
Suggest Edits also ran the actual editing guard, delivered an English paragraph,
ledger and unapplied diff, and explicitly disclosed claim qualification and
evidence alignment requiring approval. Guard results stayed UNKNOWN/MANUAL_REQUIRED.

Both follow-ups independently narrowed the prior A-r1 heading that alleged an
overstated quality conclusion. The excerpt actually gives an unmeasured quality
comparison as a limitation; it makes no affirmative quality-preservation claim.
The core necessity judgment remains consistent, while this ancillary false
positive is openly corrected. Original responses and historical narrow criterion
receipts are retained. Evidence and exact locators:
`.omo/evidence/scientific-model/isolated/mode-switch/REPORT.md`. No serialized
graph existed in these narrow tasks; report hashes and stable claim mappings were
checked, and no graph-validator run is claimed. Other models and real hardware
were not evaluated.

### Venue and PDF evidence

Actual source bytes and cited passages were read for **Tartan** and **Designing
Cloud Servers for Lower Carbon** (ISCA 2024), and **Supporting a Virtual Vector
Instruction Set on a Commercial Compute-in-SRAM Accelerator** and **Address
Scaling** (CAL 2024). The atlas records PDF hashes, one-based pages, partial read
coverage and exact-revision UNKNOWN. Only `writing_style_observations` changed in
the ISCA submission and CAL profiles; official rules, registry and tuple selection
remain unchanged. MICRO/HPCA/ASPLOS/SOSP/OSDI are explicitly unsampled.

The optional native reader actually extracted all four pages of the public
Cornell CAL PDF, read metadata, rendered pages 1/4 and ran opt-in Tesseract OCR.
Text/render operations passed; OCR stayed **UNKNOWN**. The images were opened and
were legible; pages 2/3 and all equations/figures were not visually reviewed.
Input SHA-256 stayed unchanged; source/PDF revision identity stayed UNKNOWN.
Poppler is unavailable here; its outcomes were tested with controlled seams only.
Source/reading/PDF receipts are under `.omo/evidence/venue-patterns/` and
`.omo/evidence/pdf-reader/`.

### Changed file responsibilities

Paths below are relative to `.agents/skills/paper-craft/` unless prefixed otherwise.

| Files | Role and reason |
|---|---|
| `SKILL.md` | Routes all existing modes through shared scientific prerequisites, private output and explicit verification limits |
| `references/core/scientific-review.md`, `claim-graph.md`, `counterfactual-audit.md`, `references/workflows/scientific-triage.md` | Common ten-step process, stable dependency map, alternatives and early findings |
| `references/core/argumentation.md`, `novelty.md`, `evidence.md` | Existing workflows share premises, evidence axes and judgments |
| `references/domains/numerical-contracts.md`, `architecture.md`, `systems.md`, `codesign.md` | Separate mathematical, finite-precision, hardware and evaluation contracts; scope-dependent domain checks |
| `references/workflows/academic-editing.md`, `reviewer-simulation.md`, `inputs-and-tools.md` | Claim-aware five-pass editing, shared findings and honest input/tool capabilities |
| `references/workflows/output-policy.md`, `scripts/review_output.py` | Private OS defaults, explicit/environment overrides, Git warnings and read-only file hashes |
| `scripts/manuscript_common.py`, `tex_uncertainty.py`, `latex_integrity_check.py`, `reference_audit.py` | Producer/consumer uncertainty, conservative partial-build handling and definite static errors |
| `scripts/argument_graph.py`, `argument_graph_model.py`, `schemas/argument-graph.schema.json`, `assets/argument-graph.json` | Offline graph schema/reference validation, source-hash freshness and assertion-free template |
| `scripts/numerical_contract_check.py` | Reproducible standard-library signed-saturation counterexample |
| `scripts/editing_guard.py`, `editing_semantics.py` | Existing protected tokens/diff plus conservative context and numerical association risk hints |
| `scripts/validate_review_report.py`, `review_report_fields.py`, `schemas/review-report.schema.json` | v2 reports with legacy unversioned/v1 reading; provenance, evidence axes and stable claim references |
| `assets/review-report.md`, `edit-ledger.csv` | Performed scope, evidence type, argument effects and edit categories; original ledger columns retained |
| `scripts/pdf_reader.py`, `pdfkit_reader.swift`, `references/workflows/pdf-reader.md` | Optional local PDF operations, selected rendering, uncertain opt-in OCR and hash-binding clues |
| `venues/writing-patterns.json`, `schemas/writing-patterns.schema.json`, `scripts/validate_writing_patterns.py`, `references/venues/writing-patterns.md` | Evidence-based four-paper atlas with partial coverage and bounded observations |
| `references/venues/README.md`, `sources.md`, `venues/profiles/isca-2026-research-submission.json`, `cal-continuing-letter-submission.json` | Separate five review dimensions and sampled observations; official requirements preserved |
| Root `README.md`, `package.json`, `.gitignore`, `.github/workflows/ci.yml` | Installation/usage documentation, bundled Swift payload, generated-output protection and portable checks |
| Root `tests/test_argument_graph.py`, `test_numerical_contracts.py`, `test_review_reports.py`, `test_semantic_editing.py`, `test_review_output.py`, `test_scoped_uncertainty.py`, `test_pdf_reader.py`, `test_writing_patterns.py` | New meaningful regression coverage for each executable boundary |
| Root `tests/npm.test.mjs`, `agent-install.test.mjs`, `test_install_targets.py`, `test_venue_limits.py`, `test_venues.py`, `test_audit_regressions.py`, `test_manuscript_tools.py`, `symlink_support.py` | Portable npm launchers/external-tool seams and precise optional symlink capability handling |
| Root `tests/scenarios/README.md`, `scientific-cases.json`, `counterfactual/`, `numerical-contracts/`, `evidence-inference/`, `graphs/`, `reports/`, `tests/VERIFICATION.md` | Synthetic blind-review inputs/rubrics, valid/invalid serialized fixtures and this actual execution record |

### Earlier implementation records

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

## npm distribution follow-up, 2026-10-08

The subsequent request authorized repository commits and npm/npx installation/update support. The existing Skill was committed as `eabe469`; Git now has `origin` at `git@github.com:code0-god/paper-craft.git`. Generated reports, local evidence, attachments, caches, tarballs, node_modules and secret configuration are Git-ignored. Synthetic Fixtures, reproducible test code and this verification summary remain committed.

Implemented `@code0-god/paper-craft@0.1.0` with a `paper-craft` executable. The Node wrapper uses the existing Python preserving installer instead of duplicating file mutation logic. `install` and `update` support user, project and explicit destinations. No npm dependencies or automatic installation lifecycle hooks were added. Packaging explicitly selects the entire Skill's required text/code/schema files and the CLI, with no repository-only inputs or generated Python caches.

Actual `npm test` result: **9 PASS / 0 FAIL / 0 SKIPPED**, 5.007 seconds, macOS, Node 26.7.0, npm 12.0.2, Python 3.14.6. Native test-runner scenarios executed:

1. Real `npm pack`: **54 public runtime files**, complete canonical Skill, no private source material, tests, cache or generated reports.
2. Help/version with a nonexistent Python override: no installation or target changes.
3. Default user / explicit user / project / relative destination routing, including paths with spaces.
4. Unknown, missing or conflicting arguments, unavailable interpreter and simulated Python 3.9: graceful errors, existing target byte tree unchanged.
5. Interpreter environment override, explicit precedence and executable paths with spaces.
6. Real local `npm install --prefix`: package-relative payload copied independently; installed Skill/Profile validators PASS and offline venue selection works. npm package installation itself leaves the simulated home unchanged.
7. Real global `npm install --global --prefix` and installed executable: refusal preserves the old tree; `update` stores an exact complete backup.
8. Real offline `npm exec --package <local tarball>` installation.
9. Actual `npx --package <local tarball>` update into a fresh target and repeat update: prior user data survives in a byte-identical backup.

Subprocesses ran in unique temporary directories with isolated home/cache/config. Two observed test issues were corrected before the final run: npm 12's name-keyed pack JSON differs from older array output; inherited npm lifecycle `npm_config_allow_scripts` caused EALLOWSCRIPTS in a local install. The harness now accepts both JSON shapes and isolates npm configuration. User configuration was not edited. A separate read-only reviewer replayed the final `npm test`: **9/9 PASS**, no remaining findings.

`npm run check` passed Node syntax checks for CLI and tests. Ruff checks passed; Basedpyright reported 0 errors/warnings for the Python code. The existing Python suite was rerun before the initial commit: **56 PASS**, 11.855 seconds. No JavaScript LSP/typecheck is claimed; unavailable Biome was not installed. Older Node/npm releases and Windows were not executed.

Raw npm invocations/TAP and reviewer receipts are local Git-ignored evidence under `.omo/evidence/npm/` and `.omo/evidence/npm-distribution-code-review.md`. This committed summary is the portable record. No live registry publication or Git push was performed. Registry lookup for `@code0-god/paper-craft` returned E404; `@latest` instructions are explicitly conditional on publication and scope ownership. Local folder/tarball installation and update were actually tested and need no registry publication.

## MIT license follow-up, 2026-10-08

The owner selected MIT after the Git push and npm login. Root `LICENSE` and the self-contained Skill's `LICENSE` contain identical MIT notices, copyright 2026 code0-god. Package/lock metadata and Skill frontmatter identify MIT; README distinguishes project licensing from external original reference-material rights.

Actual `npm test`: **9 PASS / 0 FAIL**, 13.347 seconds. Packaging assertions require both MIT notices and preserve independent installation. Python package tests: **7 PASS**. Node syntax and Skill validator checks passed. Independent QA packed **56 files**, confirmed identical licenses and metadata, extracted the tarball, ran its installer in an isolated destination, and verified the installed Skill retains its notice. No private inputs were included. Local receipts are under `.omo/evidence/mit-license/`. No live npm publication was performed during this change.

## Multi-host and KSC/DAC follow-up, 2026-10-08

The installer now supports eight documented native target IDs (`codex`, `claude`, `gemini`, `cursor`, `copilot`, `opencode`, `windsurf`, `devin`), `generic` custom destinations and `all`. Official discovery locations/invocation differences are cited in the packaged host-compatibility guide. This is documented native compatibility plus verified file installation, not a claim that every host application/version was executed. Default Codex behavior and single-target JSON remain compatible. Batch preflight rejects predictable conflicts before copying; each update preserves the original tree. Unexpected I/O failure restores the failed target and reports completed/remaining targets; the whole batch is not one atomic transaction.

Final automated runs:

- `npm test`: **38 PASS / 0 FAIL / 0 SKIPPED**, 9.481 seconds. Includes each user/project target, unknown/prototype-name rejection, physical-path deduplication, backup integrity, preflight refusal before mutation, packaged helper inclusion and actual npx tarball `--agent all --project` installation.
- `python3 -m unittest discover -s tests -q`: **70 PASS**, 12.018 seconds. Includes four batch conflict/I/O/home-expansion tests, 23 venue tests and seven minimum-page tests in addition to the prior core coverage. Batch failure formatting does not retry a failed home expansion or list a skipped physical alias as unfinished.
- `npm run check`: four JavaScript syntax checks PASS. Ruff PASS; Basedpyright **0 errors, 0 warnings, 0 notes**. Skill validator PASS; profile validator PASS for **23 profiles / 18 venue IDs**. README relative links and fenced code blocks valid.
- Independent read-only review: **CLEAR / APPROVE**, no blockers. Fragile natural-language assertion pins were replaced with structured policy/status checks. Evidence: `.omo/evidence/compatibility-code-review.md`.

New exact profiles: KSC 2026 general-paper submission and camera-ready; DAC 2026 research submission and camera-ready; DAC 2027 research submission. Official source pages were actually retrieved/read, including direct HTTPS retrieval for the KSC frame/403-reader case. KSC is 한국소프트웨어종합학술대회, not KCC/KCSE. Review length 2–3 pages and review/publication DOCX/HWP templates are separated; unknown final length, AI policy and unsupported typography remain UNKNOWN. DAC 2026 ACM and 2027 IEEE template families are kept distinct. Rules now total **123 historically verified / 107 unverified**; none implies future submission certification. Source/CLI receipts: `.omo/evidence/ksc-dac/REPORT.md`.

KSC's inclusive minimum required extending existing profile validation/schema and the cached all-pages comparison. Before correction the new regression tests failed for underflow/invalid minima; afterward 1/4-page KSC checks fail, 2/3 pass the cached numeric range, while offline/current-rule applicability remains UNKNOWN. Tests use a controlled `pdfinfo` seam; real Poppler rendering was not performed. Evidence: `.omo/evidence/venue-minimum-20261008/README.md`.

Available-host smoke used a unique temporary project outside this Git repository. Codex, Claude and OpenCode project installations match all **58 canonical files** byte-for-byte. OpenCode 1.18.15 actually discovered the isolated `.opencode/skills/paper-craft/SKILL.md`. Claude Code 2.1.293 successfully invoked `/paper-craft` through its real CLI with read-only tools, no session persistence and empty MCP configuration. An initial invocation used only main instructions; the entrypoint was clarified to require selected workflow guides before claiming a full workflow. One fresh-install follow-up verified successful `Read` tool results for both novelty and architecture guides. Other modules were explicitly reported unread; full Research Design/Evidence workflow coverage is not claimed. The same artificial 250-word constraint was exceeded on both attempts (281/289 words); those semantic instruction-following failures remain recorded rather than counted as passes. Codex's earlier real invocation record remains historical; it was not rerun here. Gemini/Cursor/Copilot/Windsurf/Devin binaries and Windows were not executed. Matrix and exact tool events: `.omo/evidence/native-host-smoke/native-host-smoke-manual-qa.md`.

No host applications, user configuration or real manuscripts were modified by verification. No package publication occurred. The universal fallback is explicit instruction-file/reference loading, with unsupported file/shell/browser capabilities reported; automatic discovery in arbitrary unknown tools is not claimed.

Final pack dry-run: **63 public files**, 72,185 compressed bytes, `bin/agent-targets.mjs` and all five new profiles included, no `.omo`, `.omx`, source-materials or tests paths. Raw batch follow-up regressions are under `.omo/evidence/multi-host-cli/error-path-followup.md`; final automated results above include that fix.
