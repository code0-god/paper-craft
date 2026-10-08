from __future__ import annotations

import contextlib
import hashlib
import importlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / ".agents/skills/paper-craft/scripts"
sys.path.insert(0, str(SCRIPTS))
reader = importlib.import_module("pdf_reader")


def make_pdf(path: Path) -> None:
    objects = [b"<< /Type /Catalog /Pages 2 0 R >>",
               b"<< /Type /Pages /Kids [3 0 R 5 0 R] /Count 2 >>",
               b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 200] /Resources << /Font << /F1 7 0 R >> >> /Contents 4 0 R >>",
               b"", b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 200] /Resources << /Font << /F1 7 0 R >> >> /Contents 6 0 R >>",
               b"", b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
    for index, text in ((3, "Page one"), (5, "Page two")):
        stream = f"BT /F1 16 Tf 30 100 Td ({text}) Tj ET".encode()
        objects[index] = b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream"
    data = b"%PDF-1.4\n"
    offsets = [0]
    for index, content in enumerate(objects, 1):
        offsets.append(len(data))
        data += f"{index} 0 obj\n".encode() + content + b"\nendobj\n"
    xref = len(data)
    data += f"xref\n0 {len(offsets)}\n0000000000 65535 f \n".encode()
    data += b"".join(f"{offset:010d} 00000 n \n".encode() for offset in offsets[1:])
    data += f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    path.write_bytes(data)


class PDFReaderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.pdf = self.root / "input.pdf"
        make_pdf(self.pdf)
        self.env = {**os.environ, "PAPER_CRAFT_OUTPUT_DIR": str(self.root / "environment")}
        self.available: set[str] = set()
        self.failures: set[str] = set()
        self.failed_pages: set[int] = set()
        self.render_bytes = b"\x89PNG\r\n\x1a\nsynthetic"
        self.calls: list[list[str]] = []

    def tools(self) -> None:
        self.available.update(("pdfinfo", "pdftotext", "pdftoppm"))

    def invoke(self, *args: str) -> tuple[subprocess.CompletedProcess[str], dict]:
        arguments = [str(SCRIPTS / "pdf_reader.py"), str(self.pdf), "--backend", "poppler", *args]
        actual_run = subprocess.run

        def external_run(command: list[str], **kwargs):
            if command[0] == "git":
                return actual_run(command, **kwargs)
            if command[0] not in self.available:
                raise FileNotFoundError(command[0])
            self.calls.append(command)
            if command[0] in self.failures or (command[0] == "pdftotext" and int(command[2]) in self.failed_pages):
                return subprocess.CompletedProcess(command, 3, "", "Controlled reader failure")
            output = ""
            if command[0] == "pdfinfo":
                output = "Pages: 2\nTitle: Synthetic\n"
            elif command[0] == "pdftotext":
                output = "Text page " + command[2] + "\n"
            elif command[0] == "pdftoppm":
                Path(command[-1] + ".png").write_bytes(self.render_bytes)
            elif command[0] == "tesseract":
                output = "uncertain OCR\n"
            return subprocess.CompletedProcess(command, 0, output, "")

        output, errors = io.StringIO(), io.StringIO()
        with patch.object(sys, "argv", arguments), patch.dict(os.environ, self.env, clear=True), \
                patch.object(reader.shutil, "which", side_effect=lambda name: name if name in self.available else None), \
                patch.object(reader.subprocess, "run", side_effect=external_run), \
                contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            try:
                status = reader.main()
            except SystemExit as error:
                if not isinstance(error.code, int):
                    raise
                status = error.code
        result = subprocess.CompletedProcess(arguments, status, output.getvalue(), errors.getvalue())
        return result, json.loads(result.stdout) if result.stdout else {}

    def test_absent_backend_is_skipped_without_artifacts(self) -> None:
        result, report = self.invoke()
        self.assertEqual(result.returncode, 0)
        self.assertEqual(next(op["status"] for op in report["operations"] if op["operation"] == "page_count"), "SKIPPED")
        self.assertFalse((self.root / "environment").exists())
        self.assertEqual(report["artifacts"], [])

    def test_backend_failure_is_not_a_success(self) -> None:
        self.available.add("pdfinfo")
        self.failures.add("pdfinfo")
        result, report = self.invoke()
        self.assertEqual(result.returncode, 1)
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(report["operations"][0]["status"], "FAIL")

    def test_page_results_are_separate_and_input_is_unchanged(self) -> None:
        self.tools()
        self.failed_pages.add(2)
        before = self.pdf.read_bytes()
        result, report = self.invoke()
        self.assertEqual(result.returncode, 1)
        self.assertEqual([(op["page"], op["status"]) for op in report["operations"] if op["operation"] == "text"], [(1, "PASS"), (2, "FAIL")])
        self.assertEqual(before, self.pdf.read_bytes())
        self.assertEqual(report["input"]["sha256"], hashlib.sha256(before).hexdigest())
        self.assertEqual(report["visual_review"], "MANUAL_REQUIRED")

    def test_render_selection_bounds_and_output_precedence(self) -> None:
        self.tools()
        output = self.root / "explicit"
        result, report = self.invoke("--render-pages", "2,3", "--output-dir", str(output))
        self.assertEqual(result.returncode, 1)
        self.assertEqual([(op["page"], op["status"]) for op in report["operations"] if op["operation"] == "render"], [(2, "PASS"), (3, "FAIL")])
        self.assertEqual([path.name for path in output.iterdir()], ["page-2.png"])
        self.assertEqual(report["selection"], "explicit")
        self.assertFalse((self.root / "environment").exists())

    def test_existing_render_is_never_overwritten(self) -> None:
        self.tools()
        output = self.root / "existing"
        output.mkdir()
        target = output / "page-1.png"
        target.write_bytes(b"original")
        result, _ = self.invoke("--render-pages", "1", "--output-dir", str(output))
        self.assertEqual(result.returncode, 1)
        self.assertEqual(target.read_bytes(), b"original")

    def test_ocr_is_opt_in_and_uncertain(self) -> None:
        self.tools()
        self.available.add("tesseract")
        _, report = self.invoke("--render-pages", "1", "--ocr")
        self.assertEqual(next(op["status"] for op in report["operations"] if op["operation"] == "ocr"), "UNKNOWN")
        self.assertEqual(report["pages"][-1]["ocr_text"].strip(), "uncertain OCR")

    def test_missing_ocr_tool_is_skipped(self) -> None:
        self.tools()
        _, report = self.invoke("--render-pages", "1", "--ocr")
        self.assertEqual(next(op["status"] for op in report["operations"] if op["operation"] == "ocr"), "SKIPPED")

    def test_matching_title_does_not_establish_source_version(self) -> None:
        self.tools()
        source = self.root / "input.tex"
        source.write_text("\\title{Synthetic}", encoding="utf-8")
        _, report = self.invoke("--source-files", str(source))
        self.assertEqual(next(op["status"] for op in report["operations"] if op["operation"] == "source_version"), "UNKNOWN")

    def test_exact_manifest_binds_supplied_files(self) -> None:
        self.tools()
        source = self.root / "input.tex"
        source.write_text("supplied source", encoding="utf-8")
        manifest = self.root / "build.json"
        manifest.write_text(json.dumps({"pdf_sha256": hashlib.sha256(self.pdf.read_bytes()).hexdigest(),
                                       "sources": [{"path": "input.tex", "sha256": hashlib.sha256(source.read_bytes()).hexdigest()}]}), encoding="utf-8")
        _, report = self.invoke("--source-files", str(source), "--build-manifest", str(manifest))
        self.assertEqual(next(op["status"] for op in report["operations"] if op["operation"] == "source_version"), "PASS")

    def test_changed_source_invalidates_manifest_binding(self) -> None:
        source = self.root / "input.tex"
        source.write_text("new source", encoding="utf-8")
        manifest = self.root / "build.json"
        manifest.write_text(json.dumps({"pdf_sha256": hashlib.sha256(self.pdf.read_bytes()).hexdigest(),
                                       "sources": [{"path": "input.tex", "sha256": "0" * 64}]}), encoding="utf-8")
        result = reader.version_check(self.pdf, [source], manifest)
        self.assertEqual(result.status, "UNKNOWN")

    def test_no_ocr_request_never_runs_available_tesseract(self) -> None:
        self.tools()
        self.available.add("tesseract")
        _, report = self.invoke("--render-pages", "1")
        self.assertFalse(any(command[0] == "tesseract" for command in self.calls))
        self.assertEqual(next(op["status"] for op in report["operations"] if op["operation"] == "ocr"), "SKIPPED")

    def test_git_output_warning_is_reported(self) -> None:
        self.tools()
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        _, report = self.invoke("--output-dir", str(self.root / "tracked-risk"))
        self.assertTrue(report["warnings"])

    def test_invalid_render_is_a_failure(self) -> None:
        self.tools()
        self.render_bytes = b""
        result, report = self.invoke("--render-pages", "1")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(report["artifacts"], [])

    def test_page_ranges_are_bounded(self) -> None:
        result, _ = self.invoke("--render-pages", "1-999999999")
        self.assertEqual(result.returncode, 2)

    def test_private_os_default_does_not_create_storage(self) -> None:
        self.tools()
        self.env.pop("PAPER_CRAFT_OUTPUT_DIR")
        _, report = self.invoke()
        self.assertEqual(report["selection"], "os_default")
        self.assertFalse(Path(report["output_dir"]).is_relative_to(SCRIPTS.parents[3]))
        self.assertFalse(Path(report["output_dir"]).exists())

    @unittest.skipUnless(sys.platform == "darwin" and shutil.which("swift"), "PDFKit requires macOS Swift")
    def test_native_backend_works_from_unrelated_working_directory(self) -> None:
        self.env["PATH"] = os.environ["PATH"]
        isolated = self.root / "installed"
        isolated.mkdir()
        for name in ("pdf_reader.py", "pdfkit_reader.swift", "manuscript_common.py", "review_output.py"):
            shutil.copyfile(SCRIPTS / name, isolated / name)
        result = subprocess.run([sys.executable, str(isolated / "pdf_reader.py"), str(self.pdf),
                                 "--backend", "pdfkit", "--render-pages", "2"], env=self.env,
                                cwd=self.root, capture_output=True, text=True, check=False)
        report = json.loads(result.stdout)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertEqual(report["page_count"], 2)
        self.assertIn("Page one", report["pages"][0]["text"])
        self.assertIn("Page two", report["pages"][1]["text"])
        self.assertEqual(len(report["artifacts"]), 1)
        self.assertEqual(Path(report["artifacts"][0]).read_bytes()[:8], b"\x89PNG\r\n\x1a\n")


if __name__ == "__main__":
    unittest.main()
