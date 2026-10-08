# Venue intelligence

Use this guide for venue review, reviewer simulation, targeted drafting, compression,
and submission preflight. Resolve **venue, publication type, year, track, and stage**
before applying requirements. Ask only for missing context that changes the result;
an exploratory review can proceed with UNKNOWN venue compliance.

## Select exact context

Read [registry](../../venues/registry.json), then only the matching profile. Conference
profiles use a concrete year. Continuing journal profiles deliberately use `year: null`
and must still be reverified for the submission date. `research` means the main/regular
research track; ATC's cached `research` profile is a full paper. It does not cover short
papers. CAL uses `letter`; TC, TACO, TOCS and TPDS use `regular`.

Match the tuple exactly: `(venue_id, year, track, submission_stage)`. Venue ID case is
insensitive; year, track and stage are not aliases. Missing tuple returns UNKNOWN.
Do not borrow rules from an earlier edition, another track, a special issue, or the
camera-ready stage. ISCA 2026 submission and camera-ready profiles are separate.
OSDI 2026 research and operational-systems profiles are separate. NSDI Frontiers and
operational tracks require new profiles, not the research profile with changed labels.

KSC means 한국소프트웨어종합학술대회 (Korea Software Congress), not KCC, KCSE or
Korea Supercomputing Conference. Its 2026 `research` tuple denotes **일반논문**
(general papers), including Oral/Poster presentation choices, and excludes the
undergraduate/junior competition. Submission and publication templates differ.
KSC's broad scope does not broaden Paper Craft beyond architecture/systems research.

DAC means Design Automation Conference (The Chips to Systems Conference). Its
`research` tuple covers regular Research Manuscripts in the electronic design and
design-automation context, including architecture, systems and HW/SW co-design.
Engineering Tracks, special sessions and WIP posters require their own context.
DAC 2026 submission/final profiles and 2027 submission are separate: ACM versus IEEE
template families must not leak across editions. Unknown font/class or AI details
stay unknown even when another stage supplies them.

## Rule precedence and verification

1. Exact current CFP and author instructions.
2. Official templates and submission instructions.
3. Official reviewer guidelines.
4. Publisher ethics/AI policies.
5. Common field methodology.
6. Observed practices from individual representative papers.

Open official sources when available. Confirm the heading, venue/year, track, cycle,
stage and last revision. Read linked policies if their content changes the action.
Never infer a page limit, font size, appendix allowance, anonymity exception or AI
permission from a similarly named conference or another year's template.

Each rule contains `value`, `source_url`, `source_type`, `verified_at`, `applies_to`,
`verification_status`, and `notes`. `verified` means the recorded source was checked
on that date, **not** perpetual or live certification. `unverified`, `outdated` and
`conflicting` rules cannot establish an official requirement; absent facts use
`value: null` (UNKNOWN). Record conflicting clauses and ask the venue's official
instructions to resolve them; do not silently choose a favorable interpretation.

Sources unavailable/offline: report current applicability UNKNOWN and show historical
provenance separately. The CLI never downloads policies, never uploads manuscripts,
and never declares complete submission compliance PASS. Its 90-day cache-use bound
is Paper Craft's conservative operational policy, not a venue rule. Even a fresh
cache still requires a live official check before submission.

## AI policy is an action constraint

Before drafting text for a named venue, verify its **current applicable AI policy**.
Distinguish permission to generate content, allowed language editing, disclosure,
authorship, and submission attestations. Missing/blocked policy: provide research
analysis, outlines, or proposed edits of researcher-written text; hold new
venue-targeted manuscript prose until the policy is known. Do not claim UNKNOWN is
permission. This gate concerns the manuscript, not ordinary review reports.

Historical examples show why the distinction matters:

- [NSDI 2027 CFP](https://www.usenix.org/conference/nsdi27/call-for-papers), “On the Use
  of Generative AI”: substantive generation, including an entire manuscript section,
  prohibited; grammar/clarity editing permitted; human-written attestation required.
- [OSDI 2026 CFP](https://www.usenix.org/conference/osdi26/call-for-papers), “Submission
  Policies”: wholly/largely AI-generated submissions prohibited; AI editing allowed.
- [ASPLOS 2027 CFP](https://www.asplos-conference.org/asplos2027/cfp/), “Using Generative
  AI”: disclose generative AI use under the cited ACM policy.

These are scoped cached examples, not a blanket rule for other venues or editions.
Never conceal AI use, falsify a human-written attestation, or send private text to a
remote model/service without the researcher's authorization.

## Official rules vs writing practice

`field_methodology` and `observed_style` are advisory sources and cannot establish
an official page/anonymity/AI rule. Independent guidance in profiles is labeled
`independent_guidance`, not attributed to the venue. No representative-paper style
study is currently claimed; `writing_style_observations` is empty in seeded profiles.

To add one, inspect named recent papers and record `paper_url`, `observation`, and
`scope_limit`. Cite section/figure locations within the observation and explicitly
limit the inference to the sampled papers. Compare information order, design
rationale, evaluation structure and limitation placement; do not copy sentences or
infer mandatory reviewer criteria. Keep sampled observations separate from official
guidance and Paper Craft's own recommendations.

## Tools and output interpretation

Run from the skill directory (all paths remain internal):

```sh
python3 scripts/validate_profiles.py --json
python3 scripts/venue_preflight.py /path/to/paper --venue ISCA --year 2026 --track research --stage submission --offline --json
python3 scripts/venue_preflight.py /path/to/paper.tex --venue CAL --track letter --stage submission --pdf /path/to/paper.pdf --json
```

`--profile-root /path/to/venues` selects another registry package. Validate it first.
`--year` omitted selects only a continuing journal profile. PDF page counting needs
Poppler's `pdfinfo`; absent executable or an omitted PDF gives SKIPPED with reason.
An explicitly supplied nonexistent PDF is a failed input check, not a passed inspection.
Total pages cannot determine main-content pages when references/appendices are
excluded. Font geometry, anonymity, citation formatting, artifact eligibility and
AI disclosure stay manual/agent UNKNOWN. Literal mandatory LaTeX class/options can
be compared with a fresh exact cached profile; they do not prove rendered compliance.

JSON uses `tool`, `status`, `findings`; each finding has `check`, `status`, `severity`,
`file`, `line`, and `message`. Exit codes: 0 = report produced without detected FAIL
(may contain UNKNOWN/SKIPPED), 1 = detected FAIL, 2 = invalid CLI usage. A validator
PASS proves package structure/provenance consistency, not manuscript acceptability.

Deliver Venue Compliance Report with target tuple, applied vs unresolved rules,
source URLs/check dates, technical review, separately labeled style advice, and
preflight findings. Keep historical evidence and live revalidation status distinct.
No acceptance prediction or invented score.

## Extend or refresh

Copy the shape of a matching profile and set a new exact identity. Start unsupported
rules at null/unverified. Check official source text, retain a short paraphrase and
its heading/location in `notes`, and record date and applicability for each verified
rule. Add official hosts and relative profile path to registry. Avoid copyrighted
template/source copies unless redistribution is authorized. Run validator and tests.
Refresh only the source-dependent rules; do not silently change other editions.

See [source inventory](sources.md) for scope, retrieval limitations and seeded targets.
