# Writing-pattern atlas

Use [the version 1 atlas](../../venues/writing-patterns.json) to inspect information
order in named papers. It is separate from the version 1 official venue-profile
schema and exact `(venue_id, year, track, submission_stage)` selection. A 2024 paper
does not establish ISCA 2026 rules or continuing CAL author instructions.

## Evidence and sample

The initial sample comprises two ISCA 2024 papers and two CAL 2024 letters, chosen
for accessible full PDFs and contrasting contributions, not statistical coverage.
MICRO, HPCA, ASPLOS, SOSP and OSDI have explicit `unsampled` entries with empty
paper lists. No writing practice is asserted for those venues.

| Sampled paper | Read passages supporting observations | Bounded observation |
|---|---|---|
| [Tartan](https://www.pdl.cmu.edu/PDL-FTP/associated/Tartan-ISCA24.pdf) | III/IV (PDF pp. 4–5); VIII-C–E (pp. 13–14) | Bottlenecks precede mechanisms; separate component comparisons precede the combined result. |
| [Designing Cloud Servers for Lower Carbon](https://www.pdl.cmu.edu/PDL-FTP/CloudComputing/Wang_ISCA24.pdf) | IV (pp. 5–6), VI (pp. 11–12), VIII (p. 13) | Framework interfaces and assumptions are explicit; component and cluster results have distinct conditions. |
| [Virtual Vector Instruction Set](https://www.csl.cornell.edu/~cbatten/pdfs/golden-apu-ubmark-cal2024.pdf) | III/IV (pp. 3–4), V (p. 4) | The instruction subset is bounded and abstraction overhead is discussed alongside opportunities. |
| [Address Scaling](https://www.pdl.cmu.edu/PDL-FTP/associated/Address_Scaling_Architectural_Support.pdf) | I/II (pp. 1–3), III/V (pp. 3–4) | The locality insight follows prior limitations; comparison settings distinguish benefit from capacity cost. |

These are text observations about individual papers, not mandatory section orders,
reviewer criteria, venue-wide norms, acceptance explanations or scientific endorsements.
The CAL examples show focused scope; they do not justify hiding missing experiments
or treating short format as an exemption from evidence. Review the contribution's
actual claims before suggesting any similar organization.

The atlas records publication year, DOI, public paper URL, PDF SHA-256, exact revision
(currently `UNKNOWN`), page count, partial read coverage, observation locators and
verification status. Locators use **one-based PDF pages**, including cover pages.
Tartan's PDF page 2 is printed page 548; its later cover date does not replace the
proceedings year. Address Scaling's PDF pages 1–4 are printed pages 69–72. The vector
paper's local pagination is 1–4 despite bibliographic pages 29–32; text extraction
contains duplicated spans and broken reference tokens. Treat extraction noise as a
reader limitation, not evidence about rendered manuscript quality.

`verified` means a curator read the specified textual passages for the bounded
observation. It does not mean the whole paper, visual layout, equation correctness,
figures, numerical results, code or scientific inference was verified. `read_coverage`
explicitly names unread scope and limitations. A locator naming a figure/table is
based on its caption/discussion unless visual inspection is separately recorded.

## Keep five venue-review dimensions separate

1. **Submission compliance:** exact official target and live policy verification;
   offline applicability remains `UNKNOWN`.
2. **Contribution fit:** relate the actual research question and contribution to the
   venue's verified scope; do not predict acceptance.
3. **Technical evidence:** evaluate validity, baselines, counterfactuals and inference
   at the scope of the claims, independently of presentation style.
4. **Argument clarity:** assess how premises, mechanisms, evidence and qualifications
   connect; label Paper Craft's recommendations as independent guidance.
5. **Observed writing patterns:** cite the exact sampled paper passages and coverage,
   keeping the sample limit visible even when adapting an idea.

The category vocabulary is `official_requirement`, `official_recommendation`,
`observed_pattern`, `independent_guidance`. Paper-derived atlas observations cannot
establish either official category; the validator rejects that classification.
Official rules and recommendations belong in the exact venue profiles with official
provenance. Independent guidance remains an interpretation, not a measured pattern
or an official instruction. The initial atlas contains only `observed_pattern`.

## Validate or extend

```sh
python3 scripts/validate_writing_patterns.py --json
python3 scripts/validate_writing_patterns.py /path/to/atlas.json --json
```

The stdlib CLI validates metadata shape, HTTPS URL syntax, hashes, dates, categories,
sample counts, references, page bounds and whether every verified observation's
locator occurs in recorded read coverage. It does **not** access the network,
authenticate public availability, recompute hashes from remote PDFs, read documents,
judge logical truth, certify representativeness or establish today's venue rules.
Output uses `tool`, `status`, `findings`; `scientific_validity` and
`current_rule_applicability` stay `UNKNOWN` even on structural `PASS`. Exit 0 means
no structural failure, 1 means detected failure, and 2 means invalid CLI usage.
The [schema](../../schemas/writing-patterns.schema.json) documents the data contract;
cross-record checks are performed by the CLI.

To extend an unsampled venue, first identify real public papers and publication
metadata, download/hash the actual PDFs, and read the relevant passages. Record
partial coverage honestly, mark unidentified revisions `UNKNOWN`, then add short
original paraphrases with exact locators and sample-only scope. Update the venue's
paper IDs, sample count and sampling status in this same format. An unread paper
cannot support a verified observation. Never create placeholder papers, copy
sentences, infer mandates from examples, or fill coverage using expected conventions.
