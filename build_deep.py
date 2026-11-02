# -*- coding: utf-8 -*-
"""Build the deep-dive study guide HTML and PDF. Does not touch the roadmap."""

import subprocess
import tempfile
from pathlib import Path

import deep_d1
import deep_d10
import deep_d2
import deep_d3
import deep_d4
import deep_d5
import deep_d6
import deep_d7
import deep_d8
import deep_d9
import deep_front
from render_html import render

TITLE = ".NET Tech Lead — 10-Day Deep Dive"


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
    with tempfile.TemporaryDirectory(prefix="deep-dive-edge-") as profile:
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
    blocks = []
    for module in (
        deep_front,
        deep_d1,
        deep_d2,
        deep_d3,
        deep_d4,
        deep_d5,
        deep_d6,
        deep_d7,
        deep_d8,
        deep_d9,
        deep_d10,
    ):
        blocks.extend(module.blocks())

    root = Path(__file__).resolve().parent
    html_path = root / "NET-Tech-Lead-10-Day-Deep-Dive.html"
    pdf_path = root / "NET-Tech-Lead-10-Day-Deep-Dive.pdf"
    render(blocks, html_path, title=TITLE)
    print(html_path)
    print(f"blocks={len(blocks)}")
    print_pdf(html_path, pdf_path)
    print(pdf_path)
    print(f"bytes={pdf_path.stat().st_size}")


if __name__ == "__main__":
    main()
