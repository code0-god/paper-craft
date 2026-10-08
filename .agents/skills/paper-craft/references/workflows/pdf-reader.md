# Optional local PDF reader

Use this helper when the user supplies a compiled PDF. It never compiles TeX,
executes manuscript commands, downloads documents, or uploads content. Python
3.10+ and the standard library are sufficient for orchestration. No dependency
is installed automatically.

```bash
python3 scripts/pdf_reader.py /absolute/path/paper.pdf --json
python3 scripts/pdf_reader.py /absolute/path/paper.pdf --render-pages 1,3-5 --output-dir /private/review/pages --json
python3 scripts/pdf_reader.py /absolute/path/paper.pdf --render-pages 2 --ocr --json
```

Paths above are relative to the installed Skill root. Run the script by its
absolute path when the working directory is elsewhere. Its bundled Swift helper
is resolved beside the script, not from the working directory.

## Capabilities and results

Auto selection prefers installed Poppler (`pdfinfo`, `pdftotext`, `pdftoppm`).
Otherwise macOS can use installed Swift with system PDFKit and AppKit. Explicit
`--backend poppler` and `--backend pdfkit` select one backend. Missing tools yield
`SKIPPED`; reader errors yield `FAIL`. An unavailable selected backend is not a
successful read. The helper does not promise equivalent text order across backends.

JSON includes a SHA256 input receipt, metadata, page count, page-by-page text,
per-operation `PASS`/`FAIL`/`SKIPPED`/`UNKNOWN`, requested artifact paths, output
storage selection and warnings. A blank extracted page is `UNKNOWN` (possibly
blank or scanned), not a successful text read. Exit 1 means an operation failed;
exit 0 can include `SKIPPED` and `UNKNOWN`. Argument errors exit 2. Overall status
remains `UNKNOWN` even when extraction succeeds because review remains manual.

Page selections are 1-based, accept comma-separated pages/ranges, and are bounded
to 100 requested pages per invocation. Invalid or out-of-document selections do
not render substitute pages. PDFKit renders at 120 DPI with a 40-million-pixel
limit; Poppler bounds the longest image dimension to 4096 pixels. These are
inspection images, not print-quality exports. Each external command has a
120-second timeout.

`--ocr` explicitly enables installed Tesseract on the requested rendered pages;
it requires `--render-pages`. Successful OCR is always `UNKNOWN`, with its text
separate from extracted PDF text. Missing Tesseract is `SKIPPED`. Mathematical
symbols, units, scripts, table structure and reading order need human checking.

**A render or text extraction is not visual review.** `visual_review` and
`equations_figures` remain `MANUAL_REQUIRED`. Open relevant rendered pages before
making layout, equation, figure, table or reference-placement claims, and record
which pages were actually inspected. Never mark the whole PDF visually reviewed
because one page rendered.

## Storage and provenance

Without render requests, the helper creates no output directories or artifacts;
its JSON is printed to stdout. Redirect stdout only to an intended private
review location because extracted manuscript text can be confidential. Render
storage uses `review_output.py`: explicit `--output-dir` takes precedence over
`PAPER_CRAFT_OUTPUT_DIR`, then a unique private OS user-state directory. Git
tracking/ignore risks appear in `warnings`. Outputs are created exclusively;
existing `page-N.png` files and symlinks are never overwritten. Choose a fresh
directory for reruns. The supplied PDF is read only, and its before/after SHA256
is compared. Source files are also only read.

`--source-files main.tex section.tex` records the exact supplied source inventory.
PDF title, filenames, metadata dates and filesystem times are at most clues;
without a supplied hash-binding build manifest, `source_version` is `UNKNOWN`.
An optional `--build-manifest build.json` accepts this schema:

```json
{
  "pdf_sha256": "64 hexadecimal characters for the compiled PDF",
  "sources": [
    {"path": "main.tex", "sha256": "64 hexadecimal characters for this source"},
    {"path": "section.tex", "sha256": "64 hexadecimal characters for this source"}
  ]
}
```

Manifest source paths are relative to the manifest directory (absolute paths
also work). Duplicate paths, malformed manifests, missing files, mismatches or
an incomplete match with the supplied source set cannot establish identity.
`source_version: PASS` means **the supplied manifest's exact PDF/source hash
binding was checked**. It does not independently prove build causality, establish
that all build dependencies were supplied, authenticate the manifest's creator,
or certify that the PDF represents every source change. Obtain trusted build
provenance for those stronger claims; do not fabricate a manifest after the fact
and describe it as build verification.

Native API references: Apple's [PDFDocument](https://developer.apple.com/documentation/pdfkit/pdfdocument),
[pageCount](https://developer.apple.com/documentation/pdfkit/pdfdocument/pagecount), and
[PDFPage](https://developer.apple.com/documentation/pdfkit/pdfpage).
