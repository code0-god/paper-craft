# Reviewer Simulation and response preparation

Use the exact venue/year/track/stage profile when known, then [novelty.md](../core/novelty.md), [evidence.md](../core/evidence.md), and the relevant domain guide. If the target context or official review criteria are unavailable, identify that gap and perform a clearly scoped field review.

State that the review is an AI-assisted simulation, not an actual committee review or an acceptance prediction. Do not invent a reviewer identity, official score, confidential criteria, or a probability of acceptance.

Reuse the same current hash-bound argument graph, stable claim IDs, and current finding states used by technical review and editing. Validate current input hashes before reuse; stale source material requires explicit graph updates, not a fresh disconnected opinion. Cite claim IDs and evidence locators for each finding. When new material changes a finding, record its previous/current state (`open`, `resolved`, `disputed`, `deferred`), the new artifact/locator, performed verification, and the reason for the update. Do not silently resolve an issue in one mode while retaining it as critical in another. Distinguish evidence existence, methodological validity, and whether the inference supports the claimed scope; one axis cannot substitute for another.

Assess **Significance; Novelty; Technical Soundness; Clarity; Experimental Rigor; Reproducibility; Limitations; Venue Fit**. Distinguish an official criterion from independent methodological judgment and observed paper style. Consider positive evidence and scope-qualified strengths, not only defects.

Classify each issue:

- **Critical:** a central correctness, integrity, or evidence defect invalidates the principal claim as presently stated.
- **Major:** a consequential claim, comparison, method, or argument needs substantial evidence or revision.
- **Minor:** a local clarity, consistency, or presentation defect with limited effect on the conclusion.
- **Suggestion:** an optional improvement beyond what is needed for the present claim.

Severity concerns the impact on the manuscript's claims, not an inferred acceptance outcome. Every finding needs source location, concrete evidence, impact, revision direction, and verification state. Distinguish “not reported” from “not done” and “could be stronger” from “unsupported”. Questions should specify what answer or evidence would resolve them.

Return **Major Weaknesses; Technical Questions; Missing Experiments; Argumentation Problems; Suggested Revisions; Response Preparation**. Include priorities and existing strengths when useful; avoid automatic overall ratings.

For rebuttal or revision responses, map each actual reviewer comment to the manuscript issue and response. Separate clarification supported by existing evidence, a proposed manuscript change, and a new experiment requiring work. Draft respectful, technically precise responses with exact evidence locations. Do not claim an experiment was run, a change applied, or a concern resolved unless the artifact shows it. Record disagreements by assumptions or evidence rather than dismissing the reviewer. Preserve the venue's response length, anonymity, and new-material rules only when verified for that stage.
