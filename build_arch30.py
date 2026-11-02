# -*- coding: utf-8 -*-
"""Build the 30-day technical architect roadmap HTML and PDF."""

import subprocess
import tempfile
from pathlib import Path

import arch30_front
import arch30_w1
import arch30_w2
import arch30_w3
import arch30_w4
from render_html import render

TITLE = ".NET and Angular — 30 Days to Technical Architect"


def edge_executable():
    candidates = [
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("Microsoft Edge was not found. Install Edge to print the PDF.")


def print_pdf(html_path: Path, pdf_path: Path):
    if pdf_path.exists():
        pdf_path.unlink()
    with tempfile.TemporaryDirectory(prefix="arch30-edge-") as profile:
        command = [
            str(edge_executable()),
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            "--no-pdf-header-footer",
            f"--user-data-dir={profile}",
            f"--print-to-pdf={pdf_path}",
            html_path.resolve().as_uri(),
        ]
        completed = subprocess.run(command, capture_output=True, text=True, timeout=180)
        if completed.returncode != 0 or not pdf_path.is_file() or pdf_path.stat().st_size < 10_000:
            raise RuntimeError(
                "Edge did not write a PDF.\n"
                f"code={completed.returncode}\n"
                f"stdout={completed.stdout[-2000:]}\n"
                f"stderr={completed.stderr[-2000:]}"
            )


def main():
    root = Path(__file__).resolve().parent
    html_path = root / "NET-Angular-Technical-Architect-30-Day.html"
    pdf_path = root / "NET-Angular-Technical-Architect-30-Day.pdf"
    blocks = []
    for module in (arch30_front, arch30_w1, arch30_w2, arch30_w3, arch30_w4):
        blocks.extend(module.blocks())
    for block in blocks:
        if block.get("t") == "qa" and block.get("lead"):
            block["lead_title"] = "Say this as an architect"
    render(blocks, html_path, title=TITLE)
    print(html_path)
    print(f"blocks={len(blocks)}")
    print_pdf(html_path, pdf_path)
    print(pdf_path)
    print(f"bytes={pdf_path.stat().st_size}")


if __name__ == "__main__":
    main()
