# Source receipts and interpretation boundaries

These are short reference-derived guides, not redistributed originals. The skill works without either attachment. To update them from new attachments, use the local-input procedure in the repository's `source-materials/README.md`, or the standalone steps below. Local paths in receipts are provenance, never runtime dependencies.

## A: Motivation ≠ Novelty

Source: [APRL / DGIST guide](https://gisbi-kim.github.io/motivation-is-not-novelty/). Website actually read on 2026-10-08; a separate user attachment was not present. License not established; no original included.

**Source interpretation (not an official evaluation standard):** Distinguish an important problem from a justified contribution. Diagnose why an obvious approach fails, identify the obstacle and insight, connect design choices to that explanation, and compare simpler alternatives. Ask whether experiments establish the contribution rather than merely repeat the problem. Anchors: opening diagnostic list; “Case 1. ResNet”, “Case 2. Transformer”, “Case 3. NeRF”; “제출/미팅 전 8문항 자가진단”, especially items 1, 3, 6, 7; fictional dialogue “5. 올바른 연구 전개 구조”.

The guide's reference counts, ablation counts, tier labels, single-principle derivations, and acceptance arithmetic are not adopted as thresholds. Its examples are pedagogical interpretations, not causal proof or comprehensive histories of the papers.

**Independent Paper Craft additions:** recognize systems integration, implementation, measurement, and experience contributions; accept multiple defensible principles; report comparison coverage and unknowns instead of novelty scores. The detailed nine-step audit in [novelty.md](novelty.md) implements the requested workflow, with these qualifications.

For scientific claims about the examples, consult original papers: [ResNet](https://arxiv.org/abs/1512.03385), [Transformer](https://arxiv.org/abs/1706.03762), [NeRF](https://arxiv.org/abs/2003.08934). Their landing pages were checked on 2026-10-08. Illustrative questions: what does residual parameterization change about optimization; why compare sequence computation and parallelism; what representation and sampling choices make continuous scene modeling effective? Detailed claims require the primary paper and its evidence, not the teaching guide alone.

## B: 논문 글쓰기 강의 요약

Actual supplied file: `논문_논리적_글쓰기.html`, UTF-8 HTML, 38,963 bytes. Read on 2026-10-08 using Python `HTMLParser`, without executing scripts; script/style/noscript text excluded. SHA-256: `8b7a3ac5746b44810f2fe7d86c3aab29f0c9aa6cb21846fb20cf3fb589ca43f9`. Footer attribution at original HTML line 1135: Thread `@snuwrlab`. Original lecturer, underlying thread, and license were not independently verified. Local lecture summary is the source, not an independently authenticated transcript.

### Evidence map and executable interpretation

Line numbers refer to that exact original hash, not an extracted-text file. Section IDs give more stable anchors for later editions.

| Original evidence | Source-based interpretation | Paper Craft action |
| --- | --- | --- |
| `#core`, lines 669–684; `#structure`, 693–715 | Question, reasoning, and conclusion form persuasion rather than a catalog. | Trace claim dependencies and missing premises before drafting sections. |
| `#introduction`, 723–732 | Establish necessity and a specific question. | Check problem evidence, gap, scope, and why the proposed study answers it. |
| `#literature`, 744–760; `#citation`, 768–779 | Compare prior work critically; separate source content from personal analysis. | Use comparison axes, exact citations, and explicit attribution boundaries. |
| `#methods`, 797–812 | Explain why the method suits the question and permits replication. | Connect design choices and experimental conditions to the hypothesis. |
| `#results`, 818–865 | Observation, interpretation, and answer have distinct roles; formats vary. | Label these roles even when a venue combines Evaluation and Discussion. |
| `#outline`, 872–881; `#flow`, 890–926 | Organization is a logic map; premise-to-result mismatches matter. | Create the argument map, then repair unsupported edges and section order. |
| `#paragraph`, 933–969 | Paragraphs have a central point and supporting sentences. | Identify topic, evidence, explanation, qualification, and transition; no fixed count. |
| `#story`, 976–985 | Author choices and interpretation give the paper a coherent narrative. | Show problem, alternatives, decisions, evidence, and bounded implications. |
| `#tables`, 992–1008 | Explain trends and exceptions within available evidence. | Cross-check axes, conditions, values, and inference boundaries. |
| `#readability`, 1015–1034; 1037–1061 | Clear language and calibrated claim strength preserve complexity. | Edit long or ambiguous sentences after logic review; preserve units and scope. |
| `#ai`, 1069–1106 | Researcher leads; generated information must be checked against originals. | Require author verification of claims and citations; track approved revisions. |

**Independent additions:** architecture modeling categories, baseline normalization, tail-latency interpretation, co-design accounting, six evidence states, source-status metadata, and static validators are Paper Craft procedures. They are not presented as statements from this lecture.

The lecture's illustrative supporting-sentence counts, sentence line lengths, and categorical introductory advice are guidance, not mandatory manuscript rules. Claim strength must depend on actual evidence; a stylistic “high confidence” example alone cannot establish causation.

## Update from an attachment, standalone

1. Keep the original in a local, non-distributed input directory. Record its path, format, byte count, SHA-256, title, asserted authorship, rights status, and acquisition date.
2. Run `python3 scripts/source_material.py inspect /absolute/path/to/file.html --source-id B --json` from the skill directory. Inspect text and structural anchors only; do not open active scripts or upload the input.
3. Compare the receipt to this guide. If the hash changes, re-read the relevant sections and refresh anchors; do not retain old line claims as newly verified.
4. Write short attributed paraphrases, separate interpretation and independently added advice, then rerun package validation. Mark absent, unreadable, or unverified material explicitly. Never claim an unprovided attachment was read.
5. Include originals in a distributed package only under an explicit compatible permission or license. The short guide, metadata, and local update procedure suffice for ordinary installation.
