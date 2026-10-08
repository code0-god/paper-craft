# Novelty audit

Use for novelty and contribution analysis. The nine-step procedure operationalizes the user's requested audit; [source-guides.md](source-guides.md) separates source interpretation from Paper Craft's additional guidance.

Connect this audit to the common [scientific review](scientific-review.md) graph. Run the [minimal alternative audit](counterfactual-audit.md) early in technical reviews too, rather than deferring a necessity challenge until a separate novelty pass. Mathematical feasibility and hardware cost require independent judgments; lack of comparison is not proof that either design is better.

## Nine steps

1. **Motivation:** state the consequential problem, affected setting, and evidence that it occurs. A difficult or important problem does not establish the novelty of its solution.
2. **Failure mechanism:** distinguish the observed symptom from the mechanism proposed to cause it. Record whether the mechanism was measured, inferred, or hypothesized, including competing explanations.
3. **Challenge:** derive the technical obstacle from that mechanism and constraints. Explain why an existing or obvious approach cannot simply resolve it; identify what remains unknown.
4. **Insight:** state the new perspective, empirical discovery, architectural principle, or operational lesson. If no insight is available, report a candidate hypothesis rather than invent one.
5. **Method rationale:** connect each consequential design choice to a challenge, feasibility constraint, or trade-off. Alternatives can be viable: the design need not be the unique logical consequence of a single principle.
6. **Closest prior work:** compare assumptions, mechanism, capability, implementation scope, evaluation conditions, and limitations. Use original sources when available. If retrieval is unavailable, mark the comparison incomplete and novelty unresolved; never turn a failed search into a first-ever claim.
7. **Naive and simpler alternatives:** identify the simplest credible baseline and alternatives that test the claimed insight. Check whether these were implemented and tuned fairly. Label suggested baselines as planned, with no invented results.
8. **Design evidence:** identify which ablations, controlled comparisons, sensitivity analyses, traces, deployment observations, or proofs justify the consequential choices. End-to-end gains can establish utility; attribution requires evidence suited to the causal claim. Not every component needs an ablation if the claim can be justified another way.
9. **Established contribution:** write a bounded statement of what the current evidence establishes, what is only proposed, and what remains unverified. Specify the setting and comparison reference for each novelty claim.

## Diagnose, without an acceptance score

Flag motivation presented as contribution, repeated descriptions of others' failures, unexplained module additions, missing closest work, ignored simpler alternatives, untested superiority, or a list of combined technologies offered as the whole justification. For each finding give location, evidence, impact, and a test or analysis that could resolve it.

Do not reject an integrated system merely because its modules are established. Integration may create a new scheduling or dataflow structure, resolve incompatible constraints, enable a previously infeasible implementation, reveal a scaling limit, or produce useful operational knowledge. Evaluate that claim against the closest integrated alternatives and actual system effects. Measurement, design, implementation, and experience contributions are valid candidates without a new algorithm.

Do not require a minimum number of references, tasks, ablations, or insights. Do not assign an absolute novelty score or predict acceptance. Explain comparison coverage and uncertainty. Distinguish a confirmed overlap with prior work from missing information about overlap.

## Output

Return **Problem; Challenge; Insight; Contribution; Prior Work Comparison; Missing Evidence; Recommended Next Steps**. For each candidate contribution attach an evidence state from [evidence.md](evidence.md). Put research validation tasks ahead of cosmetic revisions when the contribution is not supported.
