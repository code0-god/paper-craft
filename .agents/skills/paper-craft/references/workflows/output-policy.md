# Private output and manuscript receipts

Chat-only reviews do not require files. When a report, graph, proposal, patch or rendered page is requested, use the user's explicit output directory first, then `PAPER_CRAFT_OUTPUT_DIR`, otherwise the OS user storage selected by [review_output.py](../../scripts/review_output.py). Do not default to the Skill checkout or a manuscript repository's `output/reviews/`.

Default bases are `~/Library/Application Support/PaperCraft/reviews` on macOS, `$XDG_STATE_HOME/paper-craft/reviews` (normally `~/.local/state/paper-craft/reviews`) on Linux, and `%LOCALAPPDATA%/PaperCraft/reviews` on Windows. Default runs have separate timestamped directories. If a Git-managed home contains the normal default, the helper selects a private temporary base outside the source repository. Existing paths and files are never deleted by path selection.

```bash
python3 scripts/review_output.py --json
python3 scripts/review_output.py --create --inputs /path/to/main.tex /path/to/refs.bib --json
python3 scripts/review_output.py --output-dir /chosen/private/review --create --json
python3 scripts/review_output.py --inputs /path/to/original.tex --proposals /path/to/proposed.tex --json
```

Without `--create`, selection and hashing are read-only and create no directories. `--create` makes storage, not manuscript edits. Use the returned directory for subsequent artifacts; do not overwrite an existing proposal/report unless that replacement was authorized. A user-selected in-repository path is honored but Git-tracked/unignored output warnings must be shown. The helper does not edit another repository's ignore rules. Repository-local `output/`, temporary products and backups are ignored in this Skill source checkout; these ignores do not automatically protect unrelated manuscript repositories.

Record actual source and proposal SHA-256 receipts, relevant scope and current locations. Check source hashes before reusing graph/review conclusions and before applying approved edits. A hash confirms byte identity, not scientific validity or authenticity. Missing/unreadable sources are explicitly UNREADABLE; never describe them as read.

Review Only and Suggest Edits keep originals unchanged. Store proposals, manifests and snapshots privately; technical changes retain the existing approval requirement. Do not upload a manuscript, graph, extracted text or rendered derivative to an additional service without explicit authorization. Host model/data policies still apply to the selected Agent environment.
