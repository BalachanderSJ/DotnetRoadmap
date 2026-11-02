# -*- coding: utf-8 -*-
"""Build the 10-day .NET tech-lead interview roadmap."""

from pathlib import Path

import content_d1
import content_d10
import content_d2
import content_d3
import content_d4
import content_d5
import content_d6
import content_d7
import content_d8
import content_d9
import content_front
from render_docx import render

def main():
    blocks = []
    for module in (
        content_front,
        content_d1,
        content_d2,
        content_d3,
        content_d4,
        content_d5,
        content_d6,
        content_d7,
        content_d8,
        content_d9,
        content_d10,
    ):
        blocks.extend(module.blocks())

    out = Path(__file__).with_name("NET-Tech-Lead-10-Day-Interview-Roadmap.docx")
    render(blocks, out)
    print(out)
    print(f"blocks={len(blocks)}")


if __name__ == "__main__":
    main()
