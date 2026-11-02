# -*- coding: utf-8 -*-
"""Build the DSA and system-design study guide HTML and PDF."""

from pathlib import Path

import dsa_sd_design
import dsa_sd_design_b
import dsa_sd_dsa
import dsa_sd_dsa_b
import dsa_sd_front
from build_deep import print_pdf
from render_html import render

TITLE = ".NET Tech Lead — DSA and System Design"


def main():
    blocks = []
    for module in (
        dsa_sd_front,
        dsa_sd_dsa,
        dsa_sd_dsa_b,
        dsa_sd_design,
        dsa_sd_design_b,
    ):
        blocks.extend(module.blocks())

    root = Path(__file__).resolve().parent
    html_path = root / "NET-DSA-and-System-Design.html"
    pdf_path = root / "NET-DSA-and-System-Design.pdf"
    render(blocks, html_path, title=TITLE)
    print(html_path)
    print(f"blocks={len(blocks)}")
    print_pdf(html_path, pdf_path)
    print(pdf_path)
    print(f"bytes={pdf_path.stat().st_size}")


if __name__ == "__main__":
    main()
