# -*- coding: utf-8 -*-
"""Build the India high-pay job search guide HTML and PDF."""

from pathlib import Path

import job_front
import job_interview
import job_linkedin
import job_market
import job_naukri
import job_profile
import job_sites
from build_deep import print_pdf
from render_html import render

TITLE = ".NET Tech Lead — India High-Pay Job Search"


def main():
    blocks = []
    for module in (
        job_front,
        job_market,
        job_profile,
        job_linkedin,
        job_naukri,
        job_sites,
        job_interview,
    ):
        blocks.extend(module.blocks())

    root = Path(__file__).resolve().parent
    html_path = root / "India-High-Pay-Job-Search.html"
    pdf_path = root / "India-High-Pay-Job-Search.pdf"
    render(blocks, html_path, title=TITLE)
    print(html_path)
    print(f"blocks={len(blocks)}")
    print_pdf(html_path, pdf_path)
    print(pdf_path)
    print(f"bytes={pdf_path.stat().st_size}")


if __name__ == "__main__":
    main()
