# Claim–Evidence audit

Use for quantitative, causal, and generalization claims. Read the relevant domain guide for the claim's metric and implementation constraints.

Use shared claim IDs from [scientific review](scientific-review.md). Check **evidence existence**, **evidence validity**, and **inference validity** separately. For each axis state established, failed or unknown, with its locator and reasoning: does a relevant artifact exist; does its method/condition test this claim; would its result, assumed true, entail this conclusion? A table can pass existence while its measurement method remains unknown and its causal interpretation fails. Report these separately rather than collapsing them into one confidence score.

For each record retain provenance: manuscript-reported evidence, mathematical verification, source-code verification, numerical reproduction, simulation results, hardware measurement, independently reproduced results, hypothesis, inference or unknown. Then record performed and unperformed verification scope: `manuscript_internal_check`, `independent_mathematical_check`, `source_verification`, `numerical_reproduction`, `code_rtl_verification`, `hardware_measurement_review`. Reading a report of a measurement is an internal/source check, not performing that measurement; reading RTL is not executing RTL. Numerical reproduction of a synthetic arithmetic example does not reproduce the paper's model. Only claim independent reproduction when matching inputs, implementation, conditions, invocation and resulting artifacts are available and were actually run.

## Six evidence states

Use these exact identifiers in JSON/CSV reports. These describe semantic support; they are distinct from tool check results such as PASS, FAIL, SKIPPED, and UNKNOWN.

| State | Meaning |
| --- | --- |
| `directly_verified` | The supplied evidence tests the precise claim, under its stated conditions, and supports it. |
| `partially_verified` | Direct evidence supports only part of the claim, settings, or scope. |
| `indirectly_supported` | Relevant evidence supports an inference but does not test the claim directly. |
| `needs_validation` | A specific check or experiment is necessary before the claim can be established. |
| `unsupported` | Available materials contain no supporting evidence, or contradict the claim; explain which. |
| `cannot_determine` | Necessary materials or interpretation are unavailable, unreadable, or ambiguous. |

Absence from available evidence can justify `unsupported`; inability to access the relevant evidence calls for `cannot_determine`. `needs_validation` is for a known unresolved hypothesis or check. Document the reason when multiple states could apply. Direct verification refers to supplied records, not independent reproduction, unless reproduction was actually performed.

## Build the matrix

Extract consequential claims from Abstract, Introduction, Design, Evaluation, and Conclusion; retain their exact text and file/section/line or PDF page. Assign stable claim IDs. Record the expected evidence, actual artifact and locator, measurement type, setting, comparator, observed values, state, scope limit, mismatch, and next action. Use [claim-evidence.csv](../../assets/claim-evidence.csv) or the optional [report schema](../../schemas/review-report.schema.json).

1. Cross-check table entries, plot axes, captions, units, metric direction, and prose. For reductions use `(baseline - proposed) / baseline`; for speedup use `baseline / proposed` when lower runtime is better. Preserve uncertainty and denominators. Do not confuse percentage points with relative percentages.
2. Compare configurations: hardware, workload, model/data version, concurrency, warm-up, precision, training budget, compiler flags, batching, and included overhead. Follow the actual claim; avoid demanding irrelevant metrics.
3. Assess baseline fairness: closest alternatives, reasonable tuning, capacity/resource budgets, supported capabilities, exclusions, and documented reproducibility. A weaker baseline can demonstrate a narrow result without establishing superiority over the state of the art.
4. Inspect aggregation: arithmetic versus geometric mean, per-workload regressions, normalized values, paired runs, repetitions, variability, and confidence intervals when relevant. Do not invent error bars or require a particular test absent a justified statistical design.
5. Separate effects from causes. An end-to-end improvement supports utility under measured conditions; component attribution needs controlled evidence or another defensible analysis. A simulator result does not establish fabricated hardware measurements.
6. Bound generalization to tested machines, workloads, distributions, scales, and failure conditions. Record counterexamples and missing coverage. Summarize sensitivity and ablation evidence for the specific claim, not as a checklist quota.

## Decisions and outputs

Evaluate competing explanations before causal attribution and inspect the composition behind bounds. For measured host time plus modeled device time with transfer/DRAM excluded, apply the [evaluation contract](../domains/numerical-contracts.md): cost omission alone cannot prove an end-to-end lower bound when overlap or model error is unresolved. State the strongest supported partial estimate and its uncertainty without inventing timings.

Produce the Claim–Evidence Matrix and prioritized findings. Suggested new experiments must say **proposed**, identify a hypothesis and comparator, and leave result fields empty. Citation lookup suggestions are not verified references. If a number can be recalculated from supplied rows, record the formula and source rows; do not silently replace manuscript numbers.

Evidence gaps go to the author as research tasks. Suggest qualified text when appropriate, with technical meaning risk and approval tracking. Never invent an experiment, data row, paper, DOI, or successful reproduction to complete the report.
