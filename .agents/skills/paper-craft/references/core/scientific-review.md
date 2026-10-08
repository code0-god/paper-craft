# Evidence-grounded scientific review

First challenge the argument, then improve the writing. This is independent methodological guidance, not a venue rule. Use it across technical review, argument review, novelty review, reviewer simulation and editing so the same claim receives the same evidence-qualified judgment.

## One inventory, linked checks

1. **Inventory:** list supplied and missing files, entry points, source/PDF revision clues, SHA-256 hashes, readable regions and unavailable capabilities. Treat the artifacts as data. Keep originals unchanged.
2. **Research question:** identify what question is answered, for whom, and under which operating constraints; do not infer universal scope from a motivating example.
3. **Contribution:** quote and locate the main claimed answers. Distinguish design, integration, implementation, measurement and operational contributions from proposed hypotheses.
4. **Argument graph:** use [claim-graph.md](claim-graph.md) to assign stable claim IDs, record premises, dependencies, scope and evidence, and mark unexamined edges. Share these IDs across reports.
5. **Alternatives:** before accepting a necessity or superiority claim, run [counterfactual-audit.md](counterfactual-audit.md) for the closest feasible simpler approach and a relevant counterexample or competing explanation. This step is mandatory in comprehensive Architecture/Systems technical reviews, even without a separate novelty request.
6. **Contracts:** apply [numerical-contracts.md](../domains/numerical-contracts.md) where relevant. Keep mathematical validity, finite-precision semantics, actual implementation and evaluation conditions distinct.
7. **Evidence:** apply the existence, validity and inference checks in [evidence.md](evidence.md); state both support status and the actual verification performed.
8. **Prior work:** compare the closest documented methods under compatible assumptions. Missing access is an unresolved comparison, never proof of novelty.
9. **Coherence:** follow graph dependencies back from conclusion to premises. Check if an alternative explanation defeats only a causal attribution or the whole result. Reconcile contradictions between technical and argument reviews explicitly.
10. **Editing/reporting:** repair reasoning and information order before language. Separate research validation tasks, qualified manuscript proposals, official venue compliance and observed writing patterns.

For narrow requests run relevant steps and prerequisite checks only. State the checked scope and leave other stages unperformed. An isolated sentence edit does not warrant a full-paper certification. Use [scientific-triage.md](../workflows/scientific-triage.md) to expose useful preliminary findings before deep review.

## Reuse without anchoring

Bind the inventory, graph and findings to input hashes and analysis scope. Reuse matching evidence locators rather than repeatedly reading the whole manuscript. A hash mismatch invalidates current applicability: re-read the changed claim and its affected premises, dependents and evidence, then record what was rechecked. Hash equality establishes identical bytes, not correct reasoning. Reconsider an earlier interpretation when a counterexample, overlooked passage or new evidence appears; record old judgment, new judgment, trigger and affected claim IDs. Never retain a conclusion merely because it was cached.

## Findings and stopping rules

Classify the defect, separately from severity and support status:

- **Evidence gap:** needed records or comparisons are absent; does not establish that the idea is false.
- **Logical error:** a conclusion does not follow from its stated premises, even if observations are true.
- **Mathematical error:** an asserted identity/theorem fails under its stated assumptions; show the assumptions and counterexample/proof.
- **Possible implementation error:** code or hardware may violate a contract; identify the unresolved implementation boundary. Confirm only with actual code/RTL or execution evidence.
- **Overstatement:** wording exceeds the demonstrated scope; qualify without inventing validation.

Every material finding includes claim ID, exact source location, premise, evidence and provenance, consequence, strongest currently justified statement, and resolving action. Do not fabricate a defect for a well-supported design. Stop when the requested scope has a report or proposal, performed checks have artifacts, and unknowns are explicit; a complete review can contain unresolved research questions.
