# -*- coding: utf-8 -*-
"""Build the auth, scalability, Azure, and SQL study guide. Does not touch the roadmap or the architect set."""

import subprocess
import tempfile
from pathlib import Path

import prep_auth_a
import prep_auth_b
import prep_azure
import prep_front
import prep_scale
import prep_sql
from render_html import render

TITLE = ".NET Tech Lead — Auth, Scalability, Azure, and SQL"


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
    with tempfile.TemporaryDirectory(prefix="prep-depth-edge-") as profile:
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
        prep_front,
        prep_auth_a,
        prep_auth_b,
        prep_scale,
        prep_azure,
        prep_sql,
    ):
        blocks.extend(module.blocks())

    root = Path(__file__).resolve().parent
    html_path = root / "NET-Auth-Scale-Azure-SQL.html"
    pdf_path = root / "NET-Auth-Scale-Azure-SQL.pdf"
    render(blocks, html_path, title=TITLE)
    print(html_path)
    print(f"blocks={len(blocks)}")
    print_pdf(html_path, pdf_path)
    print(pdf_path)
    print(f"bytes={pdf_path.stat().st_size}")


if __name__ == "__main__":
    main()
