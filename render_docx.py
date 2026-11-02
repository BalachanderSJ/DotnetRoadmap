# -*- coding: utf-8 -*-
"""Render the tech-lead roadmap to a Word document."""

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor, Twips

NAVY = RGBColor(0x1B, 0x3A, 0x4B)
TEAL = RGBColor(0x1F, 0x6F, 0x5B)
INK = RGBColor(0x1F, 0x29, 0x37)
MUTED = RGBColor(0x3D, 0x4A, 0x57)
QUESTION = RGBColor(0x0B, 0x3D, 0x5C)


def _shade_paragraph(paragraph, fill):
    p_pr = paragraph._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    shd.set(qn("w:val"), "clear")
    p_pr.append(shd)


def _shade_cell(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    shd.set(qn("w:val"), "clear")
    tc_pr.append(shd)


def _set_cell_border(cell):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_borders = OxmlElement("w:tcBorders")
    for edge in ("top", "left", "bottom", "right"):
        element = OxmlElement(f"w:{edge}")
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), "4")
        element.set(qn("w:color"), "D0D7DE")
        tc_borders.append(element)
    tc_pr.append(tc_borders)


def _run(paragraph, text, size=11, bold=False, italic=False, color=INK, font="Calibri"):
    run = paragraph.add_run(text)
    run.font.name = font
    run._element.rPr.rFonts.set(qn("w:eastAsia"), font)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = color
    return run


def _para(doc, text="", size=11, bold=False, italic=False, color=INK, space_before=0, space_after=8, align=None, font="Calibri"):
    paragraph = doc.add_paragraph()
    paragraph.paragraph_format.space_before = Pt(space_before)
    paragraph.paragraph_format.space_after = Pt(space_after)
    paragraph.paragraph_format.line_spacing = 1.12
    if align:
        paragraph.alignment = align
    if text:
        _run(paragraph, text, size=size, bold=bold, italic=italic, color=color, font=font)
    return paragraph


def _keep_with_next(paragraph):
    p_pr = paragraph._p.get_or_add_pPr()
    kwn = OxmlElement("w:keepNext")
    p_pr.append(kwn)


def _add_page_number(paragraph):
    run = paragraph.add_run()
    run.font.name = "Calibri"
    run.font.size = Pt(9)
    run.font.color.rgb = MUTED

    def _fld(kind):
        el = OxmlElement("w:fldChar")
        el.set(qn("w:fldCharType"), kind)
        return el

    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    run._r.append(_fld("begin"))
    run._r.append(instr)
    run._r.append(_fld("end"))


def _footer(section):
    footer = section.footer
    footer.is_linked_to_previous = False
    paragraph = footer.paragraphs[0]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    paragraph.paragraph_format.space_before = Pt(4)
    _run(paragraph, ".NET Tech Lead  |  10-day interview roadmap  |  ", size=9, color=MUTED)
    _add_page_number(paragraph)

    header = section.header
    header.is_linked_to_previous = False
    hp = header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.LEFT
    _run(hp, "Backend Web API  ·  C#  ·  EF Core  ·  SQL  ·  Azure  ·  Microservices  ·  Migration", size=9, color=MUTED)


def _heading(doc, text, level):
    sizes = {1: 20, 2: 15, 3: 13}
    space_before = {1: 16, 2: 14, 3: 10}
    colors = {1: NAVY, 2: TEAL, 3: QUESTION}
    paragraph = _para(
        doc,
        text,
        size=sizes[level],
        bold=True,
        color=colors[level],
        space_before=space_before[level],
        space_after=6,
    )
    _keep_with_next(paragraph)
    return paragraph


def _bullets(doc, items, numbered=False):
    for index, item in enumerate(items, start=1):
        paragraph = doc.add_paragraph()
        paragraph.paragraph_format.left_indent = Cm(0.75)
        paragraph.paragraph_format.first_line_indent = Cm(-0.4)
        paragraph.paragraph_format.space_after = Pt(3)
        paragraph.paragraph_format.space_before = Pt(0)
        paragraph.paragraph_format.line_spacing = 1.08
        prefix = f"{index}. " if numbered else "• "
        _run(paragraph, prefix, size=11, bold=True, color=TEAL)
        _run(paragraph, item, size=11, color=INK)


def _callout(doc, title, text, fill, bar):
    table = doc.add_table(rows=1, cols=1)
    table.autofit = True
    cell = table.cell(0, 0)
    _shade_cell(cell, fill)
    cell.text = ""
    p1 = cell.paragraphs[0]
    p1.paragraph_format.space_after = Pt(2)
    p1.paragraph_format.space_before = Pt(2)
    _run(p1, title, size=11, bold=True, color=bar)
    p2 = cell.add_paragraph()
    p2.paragraph_format.space_after = Pt(2)
    p2.paragraph_format.space_before = Pt(0)
    p2.paragraph_format.line_spacing = 1.1
    _run(p2, text, size=11, color=INK)
    spacer = _para(doc, "", space_after=6)
    return table


def _qa(doc, number, question, answer, lead=None):
    q = _para(doc, "", space_before=8, space_after=2)
    _keep_with_next(q)
    _run(q, f"Q{number}.  ", size=12, bold=True, color=TEAL)
    _run(q, question, size=12, bold=True, color=QUESTION)
    a = _para(doc, "", space_before=1, space_after=4)
    _run(a, "Answer.  ", size=11, bold=True, color=NAVY)
    _run(a, answer, size=11, color=INK)
    if lead:
        _callout(doc, "Say this as a tech lead", lead, "E8F6F1", TEAL)


def _code(doc, text):
    paragraph = doc.add_paragraph()
    paragraph.paragraph_format.space_before = Pt(2)
    paragraph.paragraph_format.space_after = Pt(8)
    paragraph.paragraph_format.line_spacing = 1.0
    _shade_paragraph(paragraph, "F4F6F8")
    _run(paragraph, text, size=9, color=INK, font="Consolas")


def _table(doc, headers, rows):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    table.autofit = True
    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ""
        _shade_cell(cell, "1B3A4B")
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.space_before = Pt(2)
        _run(p, header, size=10, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF))
        _set_cell_border(cell)
    for r_index, row in enumerate(rows):
        for c_index, value in enumerate(row):
            cell = table.rows[r_index + 1].cells[c_index]
            cell.text = ""
            if r_index % 2 == 1:
                _shade_cell(cell, "F7F9FB")
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.space_before = Pt(2)
            _run(p, value, size=10, color=INK)
            _set_cell_border(cell)
    _para(doc, "", space_after=6)


def render(blocks, output_path):
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.75)
    section.bottom_margin = Inches(0.75)
    section.left_margin = Inches(0.8)
    section.right_margin = Inches(0.8)
    section.header_distance = Cm(0.4)
    section.footer_distance = Cm(0.4)
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.different_first_page_header_footer = True
    _footer(section)

    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(11)
    normal.font.color.rgb = INK

    q_counter = 0
    for block in blocks:
        kind = block["t"]
        if kind == "h1":
            q_counter = 0
            _heading(doc, block["text"], 1)
        elif kind == "h2":
            _heading(doc, block["text"], 2)
        elif kind == "h3":
            _heading(doc, block["text"], 3)
        elif kind == "p":
            _para(
                doc,
                block["text"],
                size=block.get("size", 11),
                bold=block.get("bold", False),
                italic=block.get("italic", False),
                color=MUTED if block.get("muted") else INK,
                space_before=block.get("before", 0),
                space_after=block.get("after", 8),
                align=WD_ALIGN_PARAGRAPH.CENTER if block.get("center") else None,
            )
        elif kind == "b":
            _bullets(doc, block["items"], numbered=block.get("numbered", False))
        elif kind == "note":
            _callout(doc, block["title"], block["text"], block.get("fill", "E7F1F8"), NAVY)
        elif kind == "lead":
            _callout(doc, block.get("title", "Lead judgment"), block["text"], "E8F6F1", TEAL)
        elif kind == "warn":
            _callout(doc, block.get("title", "Interview trap"), block["text"], "FDF2F2", RGBColor(0x8C, 0x2F, 0x2F))
        elif kind == "qa":
            q_counter += 1
            _qa(doc, q_counter, block["q"], block["a"], block.get("lead"))
        elif kind == "code":
            _code(doc, block["text"])
        elif kind == "table":
            _table(doc, block["headers"], block["rows"])
        elif kind == "break":
            doc.add_page_break()
        else:
            raise ValueError(kind)

    core = doc.core_properties
    core.title = ".NET Tech Lead — 10-Day Interview Roadmap"
    core.subject = "Backend Web API interview preparation"
    core.category = "Interview preparation"
    core.comments = "Study guide for a .NET backend developer moving into a tech lead role."

    doc.save(output_path)
