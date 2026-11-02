# -*- coding: utf-8 -*-
"""Build the 20-day further-study guide HTML and PDF."""

from pathlib import Path

import study20_a
import study20_b
import study20_c
import study20_d
from build_deep import print_pdf
from render_html import render

TITLE = ".NET Tech Lead — Next 20 Days"


def main():
    root = Path(__file__).resolve().parent
    html_path = root / "NET-Further-20-Day-Study.html"
    pdf_path = root / "NET-Further-20-Day-Study.pdf"
    blocks = []
    for module in (study20_a, study20_b, study20_c, study20_d):
        blocks.extend(module.blocks())
    render(blocks, html_path, title=TITLE)
    print(html_path)
    print(f"blocks={len(blocks)}")
    print_pdf(html_path, pdf_path)
    print(pdf_path)
    print(f"bytes={pdf_path.stat().st_size}")


if __name__ == "__main__":
    main()
