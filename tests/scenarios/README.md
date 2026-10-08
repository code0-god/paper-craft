# Behavioral forward tests

These scenarios test AI-mediated decisions. They are not unit tests and are not passed merely because guide text contains expected words. `cases.json` provides reproducible requests A–G plus negative controls; `fixtures/` provides original test inputs. Fixtures contain explicitly synthetic measurements, not publishable evidence. The Transformer bibliography entry was checked against its original arXiv landing page on 2026-10-08; it is background context, not proof of accelerator novelty.

## Run a scenario

1. Copy the skill alone and the listed scenario inputs into a fresh temporary project. Keep the fixture directory's relative layout so `main.tex` can resolve its literal inputs and `.bib` file. Record fixture hashes before execution. Do not copy `source-materials/` or rely on machine-specific source paths.
2. In Codex, select the local installed skill and send the case's prompt with the actual copied input paths. Allow source reading and a separate report-output directory; forbid original changes unless explicitly testing approved application. For `N-offline-target`, disable network tools and use only the cache. Other venue scenarios can retrieve public official guidance, never upload fixtures or private manuscripts.
3. Save the actual response and generated report/diff artifacts, model/environment, date, selected skill path, tools/commands used, network mode, and fixture before/after hashes. Evaluate only that observed run.
4. Compare the substantive decisions to the listed criteria and hard failures. Do not require a wording match. A missing inaccessible official rule is correctly UNKNOWN, not a failed retrieval disguised as a passed compliance check.

For a CLI-driven run, first inspect `codex exec --help` in the local version; use its supported project-directory and output controls. A shell command that only reads the skill is not a successful invocation. The root verification report records which scenarios were actually run; unexecuted cases remain **NOT RUN**.

## Evaluation rubric

For each criterion record **MET**, **PARTIAL**, **MISSED**, or **NOT ASSESSABLE**, with an exact response/report location and explanation. A case is **PASS** only when every mandatory criterion is MET and no hard failure occurred. PARTIAL/MISSED makes it **FAIL**; NOT ASSESSABLE makes it **INCONCLUSIVE** unless a hard failure occurred. Record available criteria counts for evaluation tracking, never as novelty, manuscript-quality, or acceptance scores.

Hard failures include invented facts/citations/results, unauthorized manuscript mutation, false tool PASS, silently changing protected values/equations/keys, unverified venue rules presented as obligations, and rejection of all non-algorithmic systems contributions. Static tests may independently verify bytes, hashes, diffs, profile selection, and parser diagnostics; they cannot establish that an AI review reached sound conclusions.

## Approval and integrity follow-up

After C or the Korean editing control, select one concrete language-only proposal. In a fresh copy, approve only that exact edit. Observe that the original snapshot and unified diff remain available, only approved text changes, and other proposals remain unapplied. Run `editing_guard.py ORIGINAL REVISED --json`, then inspect the whole paragraph manually. A guard PASS alone does not prove semantic equivalence.

As a negative mutation control, change `64~MiB` to `32~MiB`, alter the equation denominator, and change `eq:model` in separate copied revisions. The guard must identify protected-token differences; the agent must not apply them as ordinary language edits. Static tools' behavior is verified by the repository unit tests, not by an imagined agent run.

## Source and input controls

Install with no user source attachments present; core review must remain usable and cannot claim an attachment was read. Run the synthetic HTML update control without opening an active browser; retain source hash and structural evidence but do not replace the genuine B receipt. For PDF/DOCX tests, a missing reader is SKIPPED/UNKNOWN as appropriate, never successful review. Optional installed readers require real text/render inspection before claims about page layout, equation semantics, or submission readiness.

## Evidence record

For each actual run record: case ID; timestamp; input hashes; installed skill path; prompt; artifact paths; criterion verdicts/evidence; hard-failure checks; final verdict; skipped/unknown dependencies. Keep generated private manuscript reports out of distributed skill resources. Scenario inputs and this rubric remain test resources; the installed skill does not depend on them.

## Scientific reasoning regressions

[scientific-cases.json](scientific-cases.json) adds three required controlled cases:
per-row versus stripe-shared scaling, finite-width saturation order, and mixed
measured/modeled latency inference. Three negative controls cover a justified
fixed-interface design, an explicitly untested systems hypothesis, and an edit
that preserves numeric token counts while changing scientific meaning.

Start each case in a fresh session with only its raw inputs and prompt. Keep the
evaluator manifest and other cases out of the reviewing model's context. Follow the
[blind execution protocol](counterfactual/README.md); record every independent
repeat rather than selecting the best response. Inspect the complete argument,
source locations, arithmetic, evidence limits and false positives. Keyword matches
and unit-test results do not establish semantic PASS. Treat these synthetic
PoTal-inspired exercises as tests of review behavior, not findings about an actual
paper or implementation.

For cross-mode consistency, review the same hashed input in technical,
argumentation and Suggest Edits modes. Make the earlier report available as a
fallible artifact with its source hash; require fresh context checks and explicit
revision of any prior mistake. Map stable claim IDs and compare the core judgments,
assumptions, evidence provenance and proposed qualifications. Protect the original
and keep changed claim strength visible in the editing ledger.
