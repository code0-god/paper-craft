# Local reference-material input

This directory accepts privately supplied Reference A and B. Original files and generated local receipts are input data, not distributed skill resources. The repository ignores contents other than this README; check `git status --ignored source-materials` before publication. Do not put manuscripts or attachments into the public package without permission.

The installed `.agents/skills/paper-craft/` directory is self-contained and works without this input directory. Its short source guide contains verified metadata, paraphrased interpretation, and original-location anchors, not full lecture copies.

## Current source status

- **A:** website [Motivation ≠ Novelty](https://gisbi-kim.github.io/motivation-is-not-novelty/) actually read on 2026-10-08; a separate user attachment was not supplied during implementation. Website pedagogy was adapted with explicit limitations.
- **B:** user file `논문_논리적_글쓰기.html` actually read statically on 2026-10-08. SHA-256 `8b7a3ac5746b44810f2fe7d86c3aab29f0c9aa6cb21846fb20cf3fb589ca43f9`, 38,963 bytes. Footer attributes the lecture summary to Thread `@snuwrlab`; authorship, underlying thread, and redistribution license remain unverified. The original and its private absolute path are not distributed with the repository or package.

The original B path remains in the local acquisition receipt, not a runtime dependency. Updated source receipts should remain local. See the installed skill's `references/core/source-guides.md` for section IDs and line anchors matching the observed hash.

## Attach or replace a source

1. Place your permitted local input here, e.g. `reference-a.html` or `reference-b.html`, without replacing an existing file unintentionally. Leaving it in another private location is equally supported; no symlink is required.
2. Inspect without executing scripts:

   ```bash
   python3 .agents/skills/paper-craft/scripts/source_material.py inspect source-materials/reference-b.html --source-id B --json
   ```

   Run `--help` for supported formats. Static HTML extraction is not a browser session and does not execute scripts, request remote assets, or upload the source. For unsupported/unreadable formats, record the failure and use a trusted reader only when available; do not claim extraction succeeded.

3. Record the original path, format, title, asserted author, rights status, byte count, SHA-256, acquisition date, section ID/heading, and original line/page anchors in a local receipt. Distinguish `source observation`, `source-based interpretation`, and `independently added guidance`.
4. Read actual extracted sections and compare them to the existing guide. A changed hash invalidates old line anchors until rechecked. If a source is absent, keep the source status absent/unverified and use the standalone core rules.
5. Update only the short attributed guide and relevant procedures. Do not mirror the original or promote pedagogical heuristics to universal acceptance criteria. Then run package/profile validators and tests documented in the root README.
6. Inspect `git status --short --untracked-files=all` before distribution. Original attachments require explicit compatible redistribution permission. Core procedures, provenance metadata, and concise paraphrases are sufficient for ordinary use.

## Interpretation boundaries

Reference A informs motivation-versus-novelty reasoning; its reference counts, component quotas, tier labels, acceptance arithmetic, and sole-principle framing are not adopted as scientific rules. Systems integration, implementation, measurement, and experience can contribute without algorithmic novelty.

Reference B informs argument maps, critical comparison, paragraphs, figure interpretation, precise language, and researcher verification. Its illustrative sentence counts/line lengths are not hard formatting requirements. Domain evaluation checklists, six evidence states, static checks, and venue metadata are independently added Paper Craft guidance.
