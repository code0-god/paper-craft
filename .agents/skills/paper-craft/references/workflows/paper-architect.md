# Paper Architect

Use for argument analysis, a new paper outline, or paragraph-level organization. Read [argumentation.md](../core/argumentation.md); use [evidence.md](../core/evidence.md) to bound claims.

First inventory the manuscript and research artifacts. Write the intended answer to the research question, then an argument map linking problem, gap, mechanism, design rationale, evaluation, and contribution. Mark unsupported edges and circular reasoning. Only after that map is coherent, propose section order. Preserve venue and paper-type constraints; a short letter, measurement study, and experience paper need different detail allocation.

Before generating target-specific manuscript prose, check the exact venue profile's current AI-writing policy. If that policy restricts AI-authored sections or requires human-written attestation, support the allowed outline, critique, or editing work and identify the precise rule and its scope. Never generate a false author attestation. Do not generalize one venue's restriction to unrelated manuscripts.

For each section specify its reader question, prerequisite knowledge, claim, required evidence, dependency on the preceding section, and handoff to the next. The following roles are options, not a mandated table of contents:

| Section role | Reader question and needed evidence |
| --- | --- |
| Title | What precise problem or contribution is this paper about? Avoid unsupported superlatives. |
| Abstract | What problem, approach/insight, established result, and scoped contribution justify reading? Preserve exact reported results. |
| Introduction | Why does this problem matter, what is unresolved, and what does this study establish? |
| Background | Which concepts, assumptions, and system model are needed to follow the argument? |
| Related Work | How does the closest work compare, and which defensible gap remains? |
| Motivation | What observation demonstrates the problem, and what mechanism or hypothesis explains it? |
| Design / Architecture | Why do these choices address the challenges, and what alternatives or trade-offs exist? |
| Implementation | What is actually built; which constraints, interfaces, and missing components bound feasibility? |
| Methodology | What conditions, baselines, metrics, and reproducibility details make the tests appropriate? |
| Evaluation | Which evidence answers each research question and supports each contribution? |
| Discussion | What interpretation, alternatives, implications, and operating conditions follow from those results? |
| Limitations | Which assumptions, failure cases, or missing tests restrict the claims? |
| Conclusion | What bounded answer follows, and why is it significant? No new unsupported claim. |

Create paragraph-level outlines only where useful. For each paragraph give its purpose, draft topic sentence, evidence IDs, required reasoning, qualifier, and transition relationship. Use descriptive headings and adequate support, without fixed sentence counts. Move an explanation before the experiment that relies on it; keep definitions before use; avoid repeating the same motivation as a contribution.

Return **Argument Map; Section Findings; Paragraph Recommendations; Revised Outline; Unresolved Research Tasks**. If evidence is insufficient for a proposed section, identify the missing artifact rather than filling it with fabricated content.
