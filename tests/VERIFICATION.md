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
