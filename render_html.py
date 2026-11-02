# -*- coding: utf-8 -*-
"""Render the roadmap to print-ready HTML."""

import html


CSS = """
@page { size: letter; margin: 0.7in 0.72in 0.75in 0.72in; }
* { box-sizing: border-box; }
body { font-family: Calibri, "Segoe UI", sans-serif; color: #1f2937; font-size: 11.5pt; line-height: 1.38; margin: 0; }
h1 { color: #1b3a4b; font-size: 20pt; margin: 18pt 0 8pt; page-break-after: avoid; }
h2 { color: #1f6f5b; font-size: 14.5pt; margin: 14pt 0 6pt; page-break-after: avoid; }
h3 { color: #0b3d5c; font-size: 12.5pt; margin: 12pt 0 4pt; page-break-after: avoid; }
p { margin: 0 0 8pt; }
.center { text-align: center; }
.muted { color: #3d4a57; }
.kicker { letter-spacing: 0.12em; font-weight: 700; color: #3d4a57; }
ul, ol { margin: 0 0 8pt; padding-left: 1.2em; }
li { margin: 0 0 3pt; }
table.data { width: 100%; border-collapse: collapse; margin: 4pt 0 10pt; page-break-inside: avoid; }
table.data th { background: #1b3a4b; color: white; text-align: left; font-size: 10pt; padding: 5px 6px; }
table.data td { border: 1px solid #d0d7de; font-size: 10pt; padding: 4px 6px; vertical-align: top; }
table.data tr:nth-child(even) td { background: #f7f9fb; }
.callout { border-radius: 4px; padding: 8px 10px; margin: 6pt 0 10pt; page-break-inside: avoid; }
.callout .t { font-weight: 700; margin-bottom: 3px; }
.callout.note { background: #e7f1f8; }
.callout.note .t { color: #1b3a4b; }
.callout.lead { background: #e8f6f1; }
.callout.lead .t { color: #1f6f5b; }
.callout.warn { background: #fdf2f2; }
.callout.warn .t { color: #8c2f2f; }
.q { margin: 10pt 0 2pt; page-break-after: avoid; }
.q .n { color: #1f6f5b; font-weight: 700; }
.q .text { color: #0b3d5c; font-weight: 700; }
pre { background: #f4f6f8; padding: 8px 10px; font-family: Consolas, monospace; font-size: 9pt; white-space: pre-wrap; margin: 2pt 0 8pt; }
.break { page-break-before: always; }
"""


def _p(text, **kwargs):
    classes = []
    if kwargs.get("center"):
        classes.append("center")
    if kwargs.get("muted"):
        classes.append("muted")
    style = []
    if kwargs.get("size"):
        style.append(f"font-size:{kwargs['size']}pt")
    if kwargs.get("bold"):
        style.append("font-weight:700")
    if kwargs.get("italic"):
        style.append("font-style:italic")
    attr = ""
    if classes:
        attr += f' class="{" ".join(classes)}"'
    if style:
        attr += f' style="{";".join(style)}"'
    return f"<p{attr}>{html.escape(text)}</p>"


def render(blocks, output_path, title=".NET Tech Lead — 10-Day Interview Roadmap"):
    parts = [
        "<!DOCTYPE html><html><head><meta charset='utf-8'>",
        f"<title>{html.escape(title)}</title>",
        f"<style>{CSS}</style></head><body>",
    ]
    q_counter = 0
    for block in blocks:
        kind = block["t"]
        if kind == "h1":
            q_counter = 0
            parts.append(f"<h1>{html.escape(block['text'])}</h1>")
        elif kind == "h2":
            parts.append(f"<h2>{html.escape(block['text'])}</h2>")
        elif kind == "h3":
            parts.append(f"<h3>{html.escape(block['text'])}</h3>")
        elif kind == "p":
            fields = {k: v for k, v in block.items() if k not in ("t", "text")}
            parts.append(_p(block["text"], **fields))
        elif kind == "b":
            tag = "ol" if block.get("numbered") else "ul"
            items = "".join(f"<li>{html.escape(item)}</li>" for item in block["items"])
            parts.append(f"<{tag}>{items}</{tag}>")
        elif kind in ("note", "lead", "warn"):
            title = block.get("title") or {"note": "Note", "lead": "Lead judgment", "warn": "Interview trap"}[kind]
            parts.append(
                f"<div class='callout {kind}'><div class='t'>{html.escape(title)}</div>"
                f"<div>{html.escape(block['text'])}</div></div>"
            )
        elif kind == "qa":
            q_counter += 1
            parts.append(
                f"<p class='q'><span class='n'>Q{q_counter}.  </span>"
                f"<span class='text'>{html.escape(block['q'])}</span></p>"
            )
            parts.append(f"<p><b>Answer.  </b>{html.escape(block['a'])}</p>")
            if block.get("lead"):
                lead_title = block.get("lead_title") or "Say this as a tech lead"
                parts.append(
                    f"<div class='callout lead'><div class='t'>{html.escape(lead_title)}</div>"
                    f"<div>{html.escape(block['lead'])}</div></div>"
                )
        elif kind == "code":
            parts.append(f"<pre>{html.escape(block['text'])}</pre>")
        elif kind == "table":
            headers = "".join(f"<th>{html.escape(h)}</th>" for h in block["headers"])
            rows = []
            for row in block["rows"]:
                cells = "".join(f"<td>{html.escape(c)}</td>" for c in row)
                rows.append(f"<tr>{cells}</tr>")
            parts.append(f"<table class='data'><tr>{headers}</tr>{''.join(rows)}</table>")
        elif kind == "break":
            parts.append("<div class='break'></div>")
        else:
            raise ValueError(kind)
    parts.append("</body></html>")
    output_path.write_text("".join(parts), encoding="utf-8")
