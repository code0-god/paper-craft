#!/usr/bin/env python3
"""Inspect a supplied PDF locally; extraction and rendering are not visual review."""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

from manuscript_common import Status
from review_output import fingerprint, output_warnings, select_output


@dataclass(frozen=True, slots=True)
class Operation:
    operation: str
    status: Status
    detail: str
    page: int | None = None


def run(command: list[str]) -> str:
    """Execute only installed readers, with a bounded wait and explicit errors."""
    result = subprocess.run(command, capture_output=True, text=True, timeout=120, check=False,
                            env={**os.environ, "LC_ALL": "C"})
    if result.returncode:
        raise ValueError(result.stderr.strip() or f"Reader exited {result.returncode}")
    return result.stdout


def pages_arg(value: str) -> list[int]:
    """Parse bounded 1-based page selections without expanding arbitrary ranges."""
    result: set[int] = set()
    for item in value.split(","):
        if not re.fullmatch(r"[1-9][0-9]*(?:-[1-9][0-9]*)?", item):
            raise argparse.ArgumentTypeError("Use 1-based pages such as 1,3-5")
        bounds = [int(part) for part in item.split("-")]
        start, end = bounds[0], bounds[-1]
        if end < start or end - start >= 100 or len(result) + end - start + 1 > 100:
            raise argparse.ArgumentTypeError("Select at most 100 pages in ascending ranges")
        result.update(range(start, end + 1))
    return sorted(result)


def version_check(pdf: Path, sources: list[Path], manifest: Path | None) -> Operation:
    """Accept only supplied hash bindings; filenames, timestamps and titles are clues."""
    if not sources or manifest is None:
        return Operation("source_version", "UNKNOWN", "No source set and hash-binding build manifest supplied")
    try:
        if not manifest.is_file():
            raise ValueError("Build manifest must be a regular file")
        data = json.loads(manifest.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get("sources"), list):
            raise ValueError("Manifest requires pdf_sha256 and sources [{path, sha256}]")
        expected: dict[str, str] = {}
        for item in data["sources"]:
            if not isinstance(item, dict) or not isinstance(item.get("path"), str) or not isinstance(item.get("sha256"), str):
                raise ValueError("Malformed source hash binding")
            name = str((manifest.parent / item["path"]).resolve())
            if name in expected:
                raise ValueError("Duplicate source binding")
            expected[name] = item["sha256"]
        actual = {str(path.resolve()): fingerprint(path)["sha256"] for path in sources if path.is_file()}
        matched = (len(actual) == len(sources) and bool(actual) and expected == actual
                   and data.get("pdf_sha256") == fingerprint(pdf)["sha256"])
        return Operation("source_version", "PASS" if matched else "UNKNOWN",
                         "Supplied build manifest binds the exact supplied hashes; provenance is user-provided"
                         if matched else "Build manifest does not bind this PDF and exact supplied source set")
    except (OSError, ValueError) as error:
        return Operation("source_version", "UNKNOWN", str(error))


def inspect(args: argparse.Namespace) -> tuple[dict, int]:
    """Read operations independently, retaining failures and explicit missing tools."""
    pdf = Path(args.pdf).resolve()
    if any(not path.is_file() for path in args.source_files):
        raise ValueError("Supplied source inputs must be regular files")
    if not pdf.is_file():
        raise ValueError("PDF must be a supplied regular file")
    receipt = fingerprint(pdf)
    if receipt["status"] != "HASHED":
        raise ValueError("PDF is unreadable")
    with pdf.open("rb") as stream:
        if not stream.read(1024).lstrip().startswith(b"%PDF-"):
            raise ValueError("Input does not have a PDF header")
    backend = args.backend
    if backend == "auto":
        backend = "poppler" if shutil.which("pdfinfo") else "pdfkit"
    swift = shutil.which("swift") if sys.platform == "darwin" else None
    native = [swift, str(Path(__file__).resolve().with_name("pdfkit_reader.swift"))] if swift else []
    operations: list[Operation] = []
    count: int | None = None
    metadata: dict[str, str] = {}
    texts: list[str] = []
    available = bool(shutil.which("pdfinfo")) if backend == "poppler" else bool(native)
    if available:
        try:
            if backend == "poppler":
                info = run(["pdfinfo", str(pdf)])
                metadata = dict(line.split(":", 1) for line in info.splitlines() if ":" in line)
                metadata = {key: value.strip() for key, value in metadata.items()}
                count = int(metadata["Pages"])
            else:
                data = json.loads(run([*native, "inspect", str(pdf)]))
                if (not isinstance(data, dict) or type(data.get("page_count")) is not int
                        or not isinstance(data.get("metadata"), dict) or not isinstance(data.get("pages"), list)
                        or not all(isinstance(text, str) for text in data["pages"])
                        or not all(isinstance(k, str) and isinstance(v, str) for k, v in data["metadata"].items())
                        or len(data["pages"]) != data["page_count"]):
                    raise ValueError("Invalid native reader response")
                count, metadata, texts = data["page_count"], data["metadata"], data["pages"]
            if count is None or count <= 0:
                raise ValueError("PDF has no readable pages")
            operations.extend([Operation("page_count", "PASS", str(count)), Operation("metadata", "PASS", "Read")])
        except (OSError, ValueError, KeyError, subprocess.TimeoutExpired) as error:
            count = None
            missing_native = backend == "pdfkit" and any(marker in str(error) for marker in (
                "no such module 'PDFKit'", "no such module 'AppKit'", "invalid active developer path"))
            operations.extend(Operation(name, "SKIPPED" if missing_native else "FAIL", str(error)) for name in ("page_count", "metadata"))
    else:
        operations.extend(Operation(name, "SKIPPED", f"{backend} reader unavailable") for name in ("page_count", "metadata"))
    page_results: list[dict] = []
    if count is None:
        operations.append(Operation("text", "SKIPPED", "Page count unavailable"))
    else:
        for page in range(1, count + 1):
            try:
                if backend == "poppler" and not shutil.which("pdftotext"):
                    operations.append(Operation("text", "SKIPPED", "pdftotext unavailable", page))
                    continue
                text = run(["pdftotext", "-f", str(page), "-l", str(page), str(pdf), "-"]) if backend == "poppler" else texts[page - 1]
                operations.append(Operation("text", "PASS" if text.strip() else "UNKNOWN",
                                            "Extracted; reading order and math fidelity unverified" if text.strip() else "No text layer; blank or scanned page", page))
                page_results.append({"page": page, "text": text})
            except (OSError, ValueError, subprocess.TimeoutExpired) as error:
                operations.append(Operation("text", "FAIL", str(error), page))
    output, origin = select_output(args.output_dir)
    warnings = output_warnings(output)
    artifacts: list[str] = []
    for page in args.render_pages:
        if count is None or page > count:
            operations.append(Operation("render", "SKIPPED" if count is None else "FAIL", "Page count unavailable or page out of bounds", page))
            continue
        if backend == "poppler" and not shutil.which("pdftoppm"):
            operations.append(Operation("render", "SKIPPED", "pdftoppm unavailable", page))
            continue
        try:
            output.mkdir(parents=True, exist_ok=True, mode=0o700)
            target = output / f"page-{page}.png"
            # Render in a private staging directory; exclusive copy prevents overwrites, including symlinks.
            with tempfile.TemporaryDirectory(prefix=".pdf-reader-", dir=output) as temporary:
                staged = Path(temporary) / "page.png"
                command = (["pdftoppm", "-f", str(page), "-l", str(page), "-scale-to", "4096", "-singlefile", "-png", str(pdf), str(staged.with_suffix(""))]
                           if backend == "poppler" else [*native, "render", str(pdf), str(page), str(staged), "120"])
                run(command)
                with staged.open("rb") as source:
                    if source.read(8) != b"\x89PNG\r\n\x1a\n":
                        raise ValueError("Reader did not produce a PNG")
                with staged.open("rb") as source, target.open("xb") as destination:
                    shutil.copyfileobj(source, destination)
            artifacts.append(str(target))
            operations.append(Operation("render", "PASS", str(target), page))
            if args.ocr:
                if shutil.which("tesseract"):
                    text = run(["tesseract", str(target), "stdout"])
                    operations.append(Operation("ocr", "UNKNOWN", "OCR is uncertain; verify against the page image", page))
                    page_results.append({"page": page, "ocr_text": text})
                else:
                    operations.append(Operation("ocr", "SKIPPED", "tesseract unavailable", page))
        except (OSError, ValueError, subprocess.TimeoutExpired) as error:
            operations.append(Operation("ocr" if args.ocr and str(output / f"page-{page}.png") in artifacts else "render", "FAIL", str(error), page))
    if not args.render_pages:
        operations.append(Operation("render", "SKIPPED", "No render pages requested"))
    if not args.ocr:
        operations.append(Operation("ocr", "SKIPPED", "OCR requires explicit opt-in"))
    else:
        for page in args.render_pages:
            if not any(item.operation == "ocr" and item.page == page for item in operations):
                operations.append(Operation("ocr", "SKIPPED", "No rendered page available", page))
    operations.append(version_check(pdf, args.source_files, args.build_manifest))
    unchanged = fingerprint(pdf)["sha256"] == receipt["sha256"]
    operations.append(Operation("input_unchanged", "PASS" if unchanged else "FAIL", "Compared SHA256 before and after reading"))
    failed = any(item.status == "FAIL" for item in operations)
    report = {"tool": "pdf_reader", "status": "FAIL" if failed else "UNKNOWN", "backend": backend,
              "input": receipt, "source_inputs": [fingerprint(path) for path in args.source_files],
              "page_count": count, "metadata": metadata, "pages": page_results,
              "operations": [asdict(item) for item in operations], "artifacts": artifacts,
              "output_dir": str(output), "selection": origin, "warnings": warnings,
              "visual_review": "MANUAL_REQUIRED", "equations_figures": "MANUAL_REQUIRED"}
    return report, int(failed)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--backend", choices=("auto", "poppler", "pdfkit"), default="auto")
    parser.add_argument("--render-pages", type=pages_arg, default=[])
    parser.add_argument("--ocr", action="store_true", help="Opt in to uncertain OCR on requested rendered pages")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--source-files", type=Path, nargs="+", default=[])
    parser.add_argument("--build-manifest", type=Path)
    parser.add_argument("--json", action="store_true", help="JSON is also the default")
    args = parser.parse_args()
    if args.ocr and not args.render_pages:
        parser.error("--ocr requires --render-pages")
    try:
        report, code = inspect(args)
    except (OSError, ValueError, RuntimeError) as error:
        print(json.dumps({"tool": "pdf_reader", "status": "FAIL", "error": str(error)}))
        return 1
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
