# -*- coding: utf-8 -*-
"""Build the Angular 2-year interview guide HTML and PDF."""

from pathlib import Path

import angular_qa
from build_deep import print_pdf
from render_html import render

TITLE = "Angular — Interview Questions for 2 Years of Experience"


def main():
    root = Path(__file__).resolve().parent
    html_path = root / "Angular-Interview-2-Years.html"
    pdf_path = root / "Angular-Interview-2-Years.pdf"
    blocks = angular_qa.blocks()
    render(blocks, html_path, title=TITLE)
    print(html_path)
    print(f"blocks={len(blocks)}")
    print_pdf(html_path, pdf_path)
    print(pdf_path)
    print(f"bytes={pdf_path.stat().st_size}")


if __name__ == "__main__":
    main()
