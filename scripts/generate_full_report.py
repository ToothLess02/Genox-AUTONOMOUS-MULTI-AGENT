#!/usr/bin/env python3
"""
GENOX B.Tech Live Project Report Generator
Department of Computer Science and Engineering, SRM University, Delhi-NCR
Formats and compiles a comprehensive 60-80 page report strictly matching
the official university thesis guidelines and formatting specifications.
"""

import os
import sys
import re

# Ensure scripts dir is in path to import parts
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CURRENT_DIR)

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.enum.section import WD_SECTION
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

import report_data_part1 as p1
import report_data_part2 as p2
import report_data_part3 as p3
import report_data_part4 as p4
import report_tables_and_figures as rtf

# Color Palette Constants
COLOR_PRIMARY_NAVY = RGBColor(15, 23, 42)      # #0F172A
COLOR_DARK_SLATE = RGBColor(30, 41, 59)        # #1E293B
COLOR_SUBTITLE = RGBColor(71, 85, 105)         # #475569
COLOR_BODY = RGBColor(15, 23, 42)              # #0F172A
COLOR_MUTED_GRAY = RGBColor(100, 116, 139)     # #64748B
COLOR_ACCENT_BLUE = RGBColor(2, 132, 199)      # #0284C7
COLOR_WHITE = RGBColor(255, 255, 255)

HEX_HEADER_BG = "1E293B"
HEX_ROW_ALT_BG = "F8FAFC"
HEX_BORDER = "CBD5E1"
HEX_CODE_BG = "F1F5F9"
HEX_CALLOUT_BG = "F8FAFC"


def set_cell_shading(cell, color_hex):
    """Applies background color shading to a table cell."""
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading)


def set_cell_margins(cell, top=120, bottom=120, left=160, right=160):
    """Sets inner cell padding in dxa units (20 dxa = 1 pt)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)


def set_table_borders(table, color="CBD5E1", sz="4"):
    """Applies clean horizontal borders to a table."""
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideH w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)


def set_box_borders(table, border_color="0284C7", bg_color="F8FAFC"):
    """Sets a left-accent border callout box style."""
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="none"/>'
        f'<w:bottom w:val="none"/>'
        f'<w:left w:val="single" w:sz="24" w:space="0" w:color="{border_color}"/>'
        f'<w:right w:val="none"/>'
        f'<w:insideH w:val="none"/>'
        f'<w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)
    set_cell_shading(table.cell(0, 0), bg_color)
    set_cell_margins(table.cell(0, 0), top=140, bottom=140, left=200, right=160)


def add_page_number_to_run(run):
    """Inserts a dynamic Word PAGE field into the run."""
    run._r.append(parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="begin"/>'))
    run._r.append(parse_xml(f'<w:instrText {nsdecls("w")} xml:space="preserve"> PAGE </w:instrText>'))
    run._r.append(parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="separate"/>'))
    run._r.append(parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="end"/>'))


def configure_section_geometry(section, top=1.0, bottom=1.0, left=1.25, right=1.0):
    """Sets exact page margins as mandated by SRM guidelines."""
    section.top_margin = Inches(top)
    section.bottom_margin = Inches(bottom)
    section.left_margin = Inches(left)
    section.right_margin = Inches(right)


def add_formatted_paragraph(doc, text, style='Normal', space_before=0, space_after=6, line_spacing=1.5, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    """Adds a paragraph with strict academic typography and markdown parsing (**bold**, *italic*, `code`)."""
    p = doc.add_paragraph()
    p.alignment = align
    pPr = p._p.get_or_add_pPr()
    pPr.append(parse_xml(
        f'<w:spacing {nsdecls("w")} w:before="{int(space_before * 20)}" w:after="{int(space_after * 20)}" w:line="{int(line_spacing * 240)}" w:lineRule="auto"/>'
    ))

    # Parse inline markdown formatting: **bold**, *italic*, `code`
    # Tokenize text while preserving tokens
    pattern = r'(\*\*.*?\*\*|\*.*?\*|`.*?`)'
    tokens = re.split(pattern, text)

    for token in tokens:
        if not token:
            continue
        run = p.add_run()
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        run.font.color.rgb = COLOR_BODY

        if token.startswith('**') and token.endswith('**'):
            run.text = token[2:-2]
            run.bold = True
        elif token.startswith('*') and token.endswith('*'):
            run.text = token[1:-1]
            run.italic = True
        elif token.startswith('`') and token.endswith('`'):
            run.text = token[1:-1]
            run.font.name = 'Courier New'
            run.font.size = Pt(10)
            run.font.color.rgb = COLOR_ACCENT_BLUE
        else:
            run.text = token

    return p


def add_heading_1(doc, text):
    """Chapter heading: 16 pt Bold, Centered, ALL CAPS, 18 pt before, 12 pt after."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pPr = p._p.get_or_add_pPr()
    pPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="360" w:after="240"/>'))
    pPr.append(parse_xml(f'<w:keepNext {nsdecls("w")}/>'))

    run = p.add_run(text.upper())
    run.font.name = 'Times New Roman'
    run.font.size = Pt(16)
    run.bold = True
    run.font.color.rgb = COLOR_PRIMARY_NAVY
    return p


def add_heading_2(doc, text):
    """Section heading: 14 pt Bold, Left, 14 pt before, 6 pt after."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    pPr = p._p.get_or_add_pPr()
    pPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="280" w:after="120"/>'))
    pPr.append(parse_xml(f'<w:keepNext {nsdecls("w")}/>'))

    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(14)
    run.bold = True
    run.font.color.rgb = COLOR_DARK_SLATE
    return p


def add_heading_3(doc, text):
    """Subsection heading: 12 pt Bold, Left, 10 pt before, 4 pt after."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    pPr = p._p.get_or_add_pPr()
    pPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="200" w:after="80"/>'))
    pPr.append(parse_xml(f'<w:keepNext {nsdecls("w")}/>'))

    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.bold = True
    run.font.color.rgb = COLOR_DARK_SLATE
    return p


def add_heading_4(doc, text):
    """Sub-subsection heading: 12 pt Bold Italic, Left, 8 pt before, 4 pt after."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    pPr = p._p.get_or_add_pPr()
    pPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="160" w:after="80"/>'))
    pPr.append(parse_xml(f'<w:keepNext {nsdecls("w")}/>'))

    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.bold = True
    run.italic = True
    run.font.color.rgb = COLOR_DARK_SLATE
    return p


def add_code_block(doc, code_str, language="python"):
    """Adds a formatted monospace code listing in an shaded container."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_shading(cell, HEX_CODE_BG)
    set_cell_margins(cell, top=140, bottom=140, left=180, right=180)

    # Set light border
    tblPr = tbl._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/>'
        f'<w:bottom w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/>'
        f'<w:left w:val="single" w:sz="18" w:space="0" w:color="0284C7"/>'
        f'<w:right w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/>'
        f'<w:insideH w:val="none"/>'
        f'<w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

    # Format code lines
    p = cell.paragraphs[0]
    pPr = p._p.get_or_add_pPr()
    pPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="0" w:after="0" w:line="240" w:lineRule="auto"/>'))

    lines = code_str.strip().split('\n')
    for i, line in enumerate(lines):
        if i > 0:
            p = cell.add_paragraph()
            pPr = p._p.get_or_add_pPr()
            pPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="0" w:after="0" w:line="240" w:lineRule="auto"/>'))

        run = p.add_run(line)
        run.font.name = 'Courier New'
        run.font.size = Pt(8.5)
        run.font.color.rgb = RGBColor(30, 41, 59)

    # Add small spacing paragraph after table
    p_after = doc.add_paragraph()
    p_afterPr = p_after._p.get_or_add_pPr()
    p_afterPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="0" w:after="120"/>'))


def add_markdown_table(doc, md_table_str, caption=None):
    """Converts a standard Markdown table string into an academic Word table."""
    lines = [line.strip() for line in md_table_str.strip().split('\n') if line.strip()]
    if len(lines) < 2:
        return

    # Parse headers
    header_line = lines[0]
    headers = [col.strip() for col in header_line.strip('|').split('|')]
    num_cols = len(headers)

    # Check separator line
    data_lines = lines[2:] if len(lines) > 2 and '---' in lines[1] else lines[1:]

    # Add Table Caption if provided
    if caption:
        cap_p = doc.add_paragraph()
        cap_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap_pPr = cap_p._p.get_or_add_pPr()
        cap_pPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="180" w:after="80"/>'))
        cap_pPr.append(parse_xml(f'<w:keepNext {nsdecls("w")}/>'))
        crun = cap_p.add_run(caption)
        crun.font.name = 'Times New Roman'
        crun.font.size = Pt(10.5)
        crun.bold = True
        crun.font.color.rgb = COLOR_DARK_SLATE

    # Create table
    tbl = doc.add_table(rows=len(data_lines) + 1, cols=num_cols)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl)

    # Header Row
    hdr_row = tbl.rows[0]
    hdr_trPr = hdr_row._tr.get_or_add_trPr()
    hdr_trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
    hdr_trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

    for col_idx, header_text in enumerate(headers):
        cell = hdr_row.cells[col_idx]
        set_cell_shading(cell, HEX_HEADER_BG)
        set_cell_margins(cell, top=140, bottom=140, left=140, right=140)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pPr = p._p.get_or_add_pPr()
        pPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="0" w:after="0"/>'))
        run = p.add_run(header_text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(10)
        run.bold = True
        run.font.color.rgb = COLOR_WHITE

    # Data Rows
    for row_idx, line in enumerate(data_lines):
        row = tbl.rows[row_idx + 1]
        row_trPr = row._tr.get_or_add_trPr()
        row_trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

        cols = [c.strip() for c in line.strip('|').split('|')]
        # Pad columns if necessary
        while len(cols) < num_cols:
            cols.append("")

        is_alt = (row_idx % 2 == 1)
        bg_hex = HEX_ROW_ALT_BG if is_alt else "FFFFFF"

        for col_idx in range(num_cols):
            cell = row.cells[col_idx]
            if is_alt:
                set_cell_shading(cell, bg_hex)
            set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
            p = cell.paragraphs[0]
            pPr = p._p.get_or_add_pPr()
            pPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="0" w:after="0" w:line="240" w:lineRule="auto"/>'))

            # Check alignment (first column often left or center)
            cell_text = cols[col_idx]
            run = p.add_run(cell_text)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(9.5)
            run.font.color.rgb = COLOR_BODY

    # Add spacing after table
    p_after = doc.add_paragraph()
    p_afterPr = p_after._p.get_or_add_pPr()
    p_afterPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="0" w:after="140"/>'))


def add_figure_box(doc, fig_id, fig_title, diagram_str):
    """Inserts a structured visual diagram container with ASCII schematic and formal caption."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)

    # Shading and borders
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F8FAFC"/>')
    cell._tc.get_or_add_tcPr().append(shading)

    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="140" w:type="dxa"/><w:bottom w:w="140" w:type="dxa"/>'
        f'<w:left w:w="180" w:type="dxa"/><w:right w:w="180" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    cell._tc.get_or_add_tcPr().append(tcMar)

    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="12" w:space="0" w:color="0284C7"/>'
        f'<w:bottom w:val="single" w:sz="12" w:space="0" w:color="CBD5E1"/>'
        f'<w:left w:val="single" w:sz="18" w:space="0" w:color="0284C7"/>'
        f'<w:right w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/>'
        f'<w:insideH w:val="none"/><w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tbl._tbl.tblPr.append(borders)

    lines = diagram_str.strip().split('\n')
    for i, line in enumerate(lines):
        p = cell.paragraphs[0] if i == 0 else cell.add_paragraph()
        pPr = p._p.get_or_add_pPr()
        pPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="0" w:after="0" w:line="220" w:lineRule="auto"/>'))
        run = p.add_run(line)
        run.font.name = 'Courier New'
        run.font.size = Pt(8.0)
        run.font.color.rgb = RGBColor(30, 41, 59)

    cap_p = doc.add_paragraph()
    cap_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap_pPr = cap_p._p.get_or_add_pPr()
    cap_pPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="100" w:after="180"/>'))
    crun = cap_p.add_run(f"{fig_id}: {fig_title}")
    crun.font.name = 'Times New Roman'
    crun.font.size = Pt(10.5)
    crun.bold = True
    crun.font.color.rgb = COLOR_DARK_SLATE


TABLES_MAP = {
    "Table 1.1": rtf.TABLE_1_1,
    "Table 2.1": rtf.TABLE_2_1,
    "Table 2.2": rtf.TABLE_2_2,
    "Table 3.1": rtf.TABLE_3_1,
    "Table 3.2": rtf.TABLE_3_2,
    "Table 4.1": rtf.TABLE_4_1,
    "Table 5.1": rtf.TABLE_5_1,
    "Table 5.2": rtf.TABLE_5_2,
    "Table 6.1": rtf.TABLE_6_1,
    "Table 6.2": rtf.TABLE_6_2,
    "Table 6.3": rtf.TABLE_6_3,
    "Table 6.4": rtf.TABLE_6_4,
}

FIGURES_MAP = rtf.FIGURES_DATA

SECTION_ATTACHMENTS = {
    "1.2": [("fig", "Figure 1.2")],
    "1.6": [("fig", "Figure 1.1"), ("tbl", "Table 1.1")],
    "2.1": [("fig", "Figure 2.1"), ("tbl", "Table 2.1")],
    "2.2": [("fig", "Figure 2.2")],
    "2.4": [("tbl", "Table 2.2")],
    "3.2": [("fig", "Figure 3.2"), ("tbl", "Table 3.1")],
    "3.3": [("fig", "Figure 3.1")],
    "3.4": [("fig", "Figure 3.3"), ("tbl", "Table 3.2")],
    "3.5": [("fig", "Figure 3.4")],
    "4.2": [("fig", "Figure 4.1"), ("fig", "Figure 4.2"), ("fig", "Figure 4.3")],
    "4.3": [("fig", "Figure 4.4"), ("fig", "Figure 4.5"), ("fig", "Figure 4.6"), ("fig", "Figure 4.7")],
    "4.4": [("fig", "Figure 4.8"), ("tbl", "Table 4.1")],
    "5.1": [("tbl", "Table 5.1")],
    "5.2": [("fig", "Figure 5.1")],
    "5.3": [("tbl", "Table 5.2")],
    "5.4": [("fig", "Figure 5.2")],
    "5.7": [("fig", "Figure 5.3")],
    "6.2": [("tbl", "Table 6.1"), ("fig", "Figure 6.1")],
    "6.3": [("tbl", "Table 6.2"), ("fig", "Figure 6.2"), ("tbl", "Table 6.3"), ("fig", "Figure 6.3")],
    "6.6": [("tbl", "Table 6.4")]
}


def render_section_with_attachments(doc, sec_heading, sec_content):
    """Renders a section's text content, followed by any attached figures or tables."""
    add_heading_2(doc, sec_heading)
    render_content_blocks(doc, sec_content)

    prefix_match = re.match(r'^(\d+\.\d+)', sec_heading)
    if prefix_match:
        prefix = prefix_match.group(1)
        if prefix in SECTION_ATTACHMENTS:
            for kind, item_id in SECTION_ATTACHMENTS[prefix]:
                if kind == "fig" and item_id in FIGURES_MAP:
                    fig_info = FIGURES_MAP[item_id]
                    add_figure_box(doc, item_id, fig_info["title"], fig_info["diagram"])
                elif kind == "tbl" and item_id in TABLES_MAP:
                    tbl_info = TABLES_MAP[item_id]
                    add_markdown_table(doc, tbl_info["markdown"], caption=tbl_info["caption"])


def render_content_blocks(doc, content_str):
    """Parses raw section content with code blocks, tables, lists, and standard paragraphs."""
    paragraphs = content_str.split('\n\n')
    in_code = False
    code_lines = []

    for para in paragraphs:
        text = para.strip()
        if not text:
            continue

        # Check for code blocks
        if text.startswith('```'):
            code_lines = []
            lines = text.split('\n')
            lang = lines[0].replace('```', '').strip()
            for line in lines[1:]:
                if line.strip() == '```':
                    break
                code_lines.append(line)
            add_code_block(doc, '\n'.join(code_lines), lang)
            continue

        # Check for tables
        if text.startswith('|') and '|' in text[1:]:
            add_markdown_table(doc, text)
            continue

        # Check for subheadings inside text (e.g. ### or •)
        if text.startswith('### '):
            add_heading_3(doc, text[4:].strip())
            continue
        elif text.startswith('#### '):
            add_heading_4(doc, text[5:].strip())
            continue

        # Regular paragraph
        add_formatted_paragraph(doc, text)


def build_title_page(doc):
    """Builds the official SRM University Title/Cover Page strictly matching specifications."""
    tp = p1.FRONT_MATTER["title_page"]

    # Top Report Type
    p_top = doc.add_paragraph()
    p_top.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_topPr = p_top._p.get_or_add_pPr()
    p_topPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="240" w:after="80"/>'))
    r_top = p_top.add_run(tp["report_type"])
    r_top.font.name = 'Times New Roman'
    r_top.font.size = Pt(16)
    r_top.bold = True
    r_top.font.color.rgb = COLOR_PRIMARY_NAVY

    # ON
    p_on = doc.add_paragraph()
    p_on.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_onPr = p_on._p.get_or_add_pPr()
    p_onPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="0" w:after="120"/>'))
    r_on = p_on.add_run("ON")
    r_on.font.name = 'Times New Roman'
    r_on.font.size = Pt(12)
    r_on.bold = True

    # Title Box / Text
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_titlePr = p_title._p.get_or_add_pPr()
    p_titlePr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="0" w:after="160" w:line="280" w:lineRule="auto"/>'))
    r_title = p_title.add_run(tp["project_title"])
    r_title.font.name = 'Times New Roman'
    r_title.font.size = Pt(15)
    r_title.bold = True
    r_title.font.color.rgb = COLOR_PRIMARY_NAVY

    # Award Text
    p_award = doc.add_paragraph()
    p_award.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_awardPr = p_award._p.get_or_add_pPr()
    p_awardPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="80" w:after="40"/>'))
    r_award = p_award.add_run(tp["award_text"])
    r_award.font.name = 'Times New Roman'
    r_award.font.size = Pt(11)
    r_award.italic = True

    # Degree
    p_deg = doc.add_paragraph()
    p_deg.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_degPr = p_deg._p.get_or_add_pPr()
    p_degPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="40" w:after="180"/>'))
    r_deg = p_deg.add_run("Bachelor of Technology\nin\nComputer Science and Engineering\n[in specialization with DS and AI]")
    r_deg.font.name = 'Times New Roman'
    r_deg.font.size = Pt(13)
    r_deg.bold = True

    # SRM Logo
    logo_path = "/Users/sujaydey/Documents/Genox/srm_logo.png"
    if not os.path.exists(logo_path):
        logo_path = "/Users/sujaydey/Documents/Genox/srm_logo.jpg"
    if os.path.exists(logo_path):
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logoPr = p_logo._p.get_or_add_pPr()
        p_logoPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="80" w:after="200"/>'))
        r_logo = p_logo.add_run()
        r_logo.add_picture(logo_path, width=Inches(1.55))

    # Supervisor and Submitted by 2-Column Table
    sub_tbl = doc.add_table(rows=1, cols=2)
    sub_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    # Clear borders
    tblPr = sub_tbl._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="none"/><w:bottom w:val="none"/><w:left w:val="none"/><w:right w:val="none"/>'
        f'<w:insideH w:val="none"/><w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

    # Left cell (Supervisor)
    c_left = sub_tbl.cell(0, 0)
    p_sup = c_left.paragraphs[0]
    p_sup.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_supPr = p_sup._p.get_or_add_pPr()
    p_supPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="0" w:after="0" w:line="240" w:lineRule="auto"/>'))
    r1 = p_sup.add_run("Supervisor:\n")
    r1.font.name = 'Times New Roman'
    r1.font.size = Pt(11)
    r1.bold = True
    r2 = p_sup.add_run("Faculty Supervisor Name\nAssistant Professor / Associate Professor\nDepartment of CSE")
    r2.font.name = 'Times New Roman'
    r2.font.size = Pt(10.5)

    # Right cell (Submitted by)
    c_right = sub_tbl.cell(0, 1)
    p_sub = c_right.paragraphs[0]
    p_sub.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_subPr = p_sub._p.get_or_add_pPr()
    p_subPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="0" w:after="0" w:line="240" w:lineRule="auto"/>'))
    r3 = p_sub.add_run("Submitted by:\n")
    r3.font.name = 'Times New Roman'
    r3.font.size = Pt(11)
    r3.bold = True
    r4 = p_sub.add_run("Sujay Dey\nRoll No: 11021210071\nReg No: 210101120038")
    r4.font.name = 'Times New Roman'
    r4.font.size = Pt(10.5)

    # Department & University Footer
    p_bot = doc.add_paragraph()
    p_bot.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_botPr = p_bot._p.get_or_add_pPr()
    p_botPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="260" w:after="0" w:line="240" w:lineRule="auto"/>'))

    r_dept = p_bot.add_run("DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING\n")
    r_dept.font.name = 'Times New Roman'
    r_dept.font.size = Pt(12)
    r_dept.bold = True

    r_univ = p_bot.add_run("SRM UNIVERSITY, DELHI-NCR, SONEPAT, HARYANA\n")
    r_univ.font.name = 'Times New Roman'
    r_univ.font.size = Pt(13)
    r_univ.bold = True

    r_addr = p_bot.add_run("Plot No. 39, Rajiv Gandhi Education City, Sonepat, Haryana 131029\n")
    r_addr.font.name = 'Times New Roman'
    r_addr.font.size = Pt(10)

    r_date = p_bot.add_run("MAY 2026")
    r_date.font.name = 'Times New Roman'
    r_date.font.size = Pt(11.5)
    r_date.bold = True


def build_preliminary_pages(doc):
    """Builds Approval Page, Declaration, Certificate, Acknowledgements, Abstract, TOC, List of Figures, List of Tables."""
    # Section 2 for Preliminary Pages
    sec2 = doc.add_section(WD_SECTION.NEW_PAGE)
    configure_section_geometry(sec2)
    sec2.header.is_linked_to_previous = False
    sec2.footer.is_linked_to_previous = False

    # Lower Roman page numbering starting at ii
    sectPr2 = sec2._sectPr
    sectPr2.append(parse_xml(f'<w:pgNumType {nsdecls("w")} w:fmt="lowerRoman" w:start="2"/>'))

    # Preliminary Footer
    f2 = sec2.footer.paragraphs[0]
    f2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_f2 = f2.add_run()
    r_f2.font.name = 'Times New Roman'
    r_f2.font.size = Pt(10)
    add_page_number_to_run(r_f2)

    # 1. Project Approval Page
    app = p1.FRONT_MATTER["approval_page"]
    add_heading_1(doc, "PROJECT APPROVAL PAGE")
    add_formatted_paragraph(doc, f"**Programme:** {app['program']}")
    add_formatted_paragraph(doc, f"**{app['group_no']}** | **{app['session']}**")
    add_formatted_paragraph(doc, f"**Project Title:** {app['project_title']}")
    add_formatted_paragraph(doc, f"**Candidate Name:** {app['student_name']} (Enrolment No: {app['enrolment_no']})")
    add_formatted_paragraph(doc, app["cert_text"])

    # Signatures table
    sig_tbl = doc.add_table(rows=1, cols=3)
    sig_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    # Clear borders
    sig_tbl_Pr = sig_tbl._tbl.tblPr
    borders_xml = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="none"/><w:bottom w:val="none"/><w:left w:val="none"/><w:right w:val="none"/>'
        f'<w:insideH w:val="none"/><w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    sig_tbl_Pr.append(borders_xml)

    cols_text = [
        "(Name & Sign of Supervisor)\n\n\n___________________________\nFaculty Supervisor",
        "(Program Coordinator)\n\n\n___________________________\nDr. Mohd. Kaleem",
        "(External Examiner)\n\n\n___________________________\nSignature & Seal"
    ]
    for c_idx, txt in enumerate(cols_text):
        c = sig_tbl.cell(0, c_idx)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pPr = p._p.get_or_add_pPr()
        pPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="240" w:after="120" w:line="240" w:lineRule="auto"/>'))
        r = p.add_run(txt)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10)
        r.bold = True

    p_note = doc.add_paragraph()
    p_note.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_notePr = p_note._p.get_or_add_pPr()
    p_notePr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="240" w:after="120" w:line="240" w:lineRule="auto"/>'))
    r_n = p_note.add_run(app["note"])
    r_n.font.name = 'Times New Roman'
    r_n.font.size = Pt(9.5)
    r_n.font.italic = True
    r_n.font.color.rgb = COLOR_MUTED_GRAY

    # 2. Candidate's Declaration
    doc.add_page_break()
    dec = p1.FRONT_MATTER["declaration"]
    add_heading_1(doc, "CANDIDATE'S DECLARATION")
    for d_para in dec["text"].split("\n\n"):
        if d_para.strip():
            add_formatted_paragraph(doc, d_para.strip())

    p_dec_sig = doc.add_paragraph()
    p_dec_sig.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_dec_sigPr = p_dec_sig._p.get_or_add_pPr()
    p_dec_sigPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="240" w:after="0" w:line="240" w:lineRule="auto"/>'))
    r_dsig = p_dec_sig.add_run(
        f"\n\n\n___________________________\n"
        f"**{dec['student_name']}**\n"
        f"{dec['roll_no']}\n"
        f"{dec['reg_no']}\n"
        f"Date: MAY 2026\n"
        f"Place: SRM University, Sonepat\n"
    )
    r_dsig.font.name = 'Times New Roman'
    r_dsig.font.size = Pt(11)

    # 3. Certificate
    doc.add_page_break()
    cert = p1.FRONT_MATTER["certificate"]
    add_heading_1(doc, "CERTIFICATE")
    for c_para in cert["text"].split("\n\n"):
        if c_para.strip():
            add_formatted_paragraph(doc, c_para.strip())

    p_cert_sig = doc.add_paragraph()
    p_cert_sig.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_cert_sigPr = p_cert_sig._p.get_or_add_pPr()
    p_cert_sigPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="240" w:after="0" w:line="240" w:lineRule="auto"/>'))
    r_csig = p_cert_sig.add_run(
        f"\n\n\n___________________________\n"
        f"**{cert['supervisor_name']}**\n"
        f"{cert['supervisor_desig']}\n"
        f"Date: MAY 2026\n"
    )
    r_csig.font.name = 'Times New Roman'
    r_csig.font.size = Pt(11)

    # 4. Acknowledgements
    doc.add_page_break()
    ack = p1.FRONT_MATTER["acknowledgement"]
    add_heading_1(doc, "ACKNOWLEDGEMENTS")
    for ack_para in ack["paragraphs"]:
        add_formatted_paragraph(doc, ack_para)

    p_ack_sig = doc.add_paragraph()
    p_ack_sig.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_ack_sigPr = p_ack_sig._p.get_or_add_pPr()
    p_ack_sigPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="200" w:after="0" w:line="240" w:lineRule="auto"/>'))
    r_asig = p_ack_sig.add_run(
        f"\n**Sujay Dey**\n"
        f"B.Tech Computer Science and Engineering\n"
        f"Specialization: Data Science and Artificial Intelligence\n"
        f"Roll No: 11021210071 / Reg No: 210101120038\n"
        f"SRM University Delhi-NCR, Sonepat\n"
    )
    r_asig.font.name = 'Times New Roman'
    r_asig.font.size = Pt(10.5)

    # 5. Abstract
    doc.add_page_break()
    abst = p1.FRONT_MATTER["abstract"]
    add_heading_1(doc, "ABSTRACT")
    for abst_para in abst["paragraphs"]:
        add_formatted_paragraph(doc, abst_para)

    p_kw = doc.add_paragraph()
    p_kw.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_kwPr = p_kw._p.get_or_add_pPr()
    p_kwPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="160" w:after="0" w:line="240" w:lineRule="auto"/>'))
    r_kw = p_kw.add_run(
        "**Keywords:** Autonomous Agents, Desktop Automation, Large Language Models, Multi-Agent Systems, "
        "ReAct Prompting, Patient Listening, Fast-Path Routing, Human-in-the-Loop Safety, macOS CoreGraphics, "
        "AppleScript, Google Gemini 1.5, Asynchronous WebSocket, Zero-Cost System Architecture."
    )
    r_kw.font.name = 'Times New Roman'
    r_kw.font.size = Pt(11)

    # 6. Table of Contents
    doc.add_page_break()
    add_heading_1(doc, "TABLE OF CONTENTS")
    render_table_of_contents(doc)

    # 7. List of Figures
    doc.add_page_break()
    add_heading_1(doc, "LIST OF FIGURES")
    render_list_of_figures(doc)

    # 8. List of Tables
    doc.add_page_break()
    add_heading_1(doc, "LIST OF TABLES")
    render_list_of_tables(doc)


def render_table_of_contents(doc):
    """Renders a beautifully styled, high-density Table of Contents table with leader dots."""
    toc_entries = [
        ("PROJECT APPROVAL PAGE", "ii", True),
        ("CANDIDATE'S DECLARATION", "iii", True),
        ("CERTIFICATE", "iv", True),
        ("ACKNOWLEDGEMENTS", "v", True),
        ("ABSTRACT", "vi", True),
        ("LIST OF FIGURES", "ix", True),
        ("LIST OF TABLES", "x", True),
        ("CHAPTER 1: INTRODUCTION", "1", True),
        ("  1.1 Background and Evolution of Autonomous AI Agents", "1", False),
        ("  1.2 Motivation: Bridging the Cognitive-Execution Chasm in Desktop Workflows", "3", False),
        ("  1.3 Formal Problem Statement and Research Questions", "5", False),
        ("  1.4 Research Objectives", "6", False),
        ("  1.5 Scope and Delimitations of the System", "7", False),
        ("  1.6 Macro System Architectural Overview", "8", False),
        ("  1.7 Thesis Organization", "11", False),
        ("CHAPTER 2: LITERATURE REVIEW", "13", True),
        ("  2.1 Evolution of Conversational Interfaces and Autonomous Agent Frameworks", "13", False),
        ("  2.2 Large Language Model Reasoning, ReAct, and Toolformer Paradigms", "15", False),
        ("  2.3 Desktop Automation Paradigms and OS-Level Control Mechanisms", "18", False),
        ("  2.4 Voice Activity Detection, Turn-Taking, and Conversational Latency", "20", False),
        ("  2.5 Multi-Agent Orchestration and Specialized Subagent Architectures", "22", False),
        ("  2.6 Human-in-the-Loop Verification and Safe Agentic Autonomy", "23", False),
        ("  2.7 Critical Analysis and Identification of Research Gaps", "25", False),
        ("CHAPTER 3: METHODOLOGY AND ARCHITECTURAL FRAMEWORK", "27", True),
        ("  3.1 Research Methodology and Architectural Philosophy", "27", False),
        ("  3.2 Dual-Tier Hybrid Intent Routing Engine", "28", False),
        ("  3.3 Asynchronous Sliding-Window Patient Listening Voice Protocol", "30", False),
        ("  3.4 Multi-Agent Squad Specialization and Delegation Topology", "32", False),
        ("  3.5 Human-in-the-Loop Safety Boundary and Verification Protocols", "34", False),
        ("  3.6 Autonomous Function Calling with Zero-Cost Gemini 1.5 Flash", "35", False),
        ("  3.7 Context Compaction and SQLite Vector/Relational Memory Architecture", "36", False),
        ("CHAPTER 4: SYSTEM DESIGN AND DETAILED ARCHITECTURE", "38", True),
        ("  4.1 Macro Architecture & Operational Data Flow", "38", False),
        ("  4.2 Data Flow Diagrams (DFD Level 0, Level 1, Level 2)", "39", False),
        ("  4.3 Unified Modeling Language (UML) Behavioral & Structural Models", "44", False),
        ("  4.4 Database Design & Entity-Relationship Schema", "52", False),
        ("  4.5 Component & Interface Architecture", "54", False),
        ("  4.6 Security Architecture & Permission Sandbox", "55", False),
        ("CHAPTER 5: IMPLEMENTATION DETAILS AND CODE ENGINEERING", "57", True),
        ("  5.1 Technology Stack, Frameworks & Development Environment", "57", False),
        ("  5.2 Asynchronous Web Server & WebSocket Streaming Pipeline (`app.py`)", "58", False),
        ("  5.3 Dual-Tier Intent Engine Implementation (`fast_path.py`)", "61", False),
        ("  5.4 Native macOS Automation & HID Event Injection (`macos_automation.py`)", "63", False),
        ("  5.5 WhatsApp Catalyst Deep Automation (`whatsapp_tool.py`)", "65", False),
        ("  5.6 Human-in-the-Loop Modal Intercept Subsystem (`user_interaction.py`)", "67", False),
        ("  5.7 Persistent Relational & Context Memory Engine (`memory.py`)", "68", False),
        ("  5.8 Interactive Glassmorphic Canvas HUD & Voice Loop (`index.html`)", "69", False),
        ("CHAPTER 6: TESTING, EXPERIMENTAL EVALUATION, AND RESULTS", "71", True),
        ("  6.1 Experimental Setup & Quality Assurance Methodology", "71", False),
        ("  6.2 Latency & Execution Throughput Benchmarks", "72", False),
        ("  6.3 Speech Recognition Accuracy & Patient Listening Evaluation", "74", False),
        ("  6.4 End-to-End Real-World Task Verification (Case Studies)", "75", False),
        ("  6.5 Edge Case Resolution & Robustness Analysis", "76", False),
        ("  6.6 Performance Under Network Degraded & Offline Scenarios", "77", False),
        ("CHAPTER 7: CONCLUSION AND FUTURE SCOPE", "78", True),
        ("  7.1 Summary of Contributions", "78", False),
        ("  7.2 Innovation and Competitive Differentiation", "79", False),
        ("  7.3 Societal and Ethical Implications", "80", False),
        ("  7.4 Limitations of the Current System", "81", False),
        ("  7.5 Future Research Directions and Roadmap", "82", False),
        ("  7.6 Concluding Remarks", "83", False),
        ("REFERENCES & BIBLIOGRAPHY (75 IEEE CITATIONS)", "84", True),
        ("APPENDIX A: ENVIRONMENT SETUP AND INSTALLATION GUIDE", "89", True),
        ("APPENDIX B: COMPLETE 27-TOOL REGISTRY CATALOG AND SCHEMAS", "91", True),
        ("APPENDIX C: COMPLETE SYSTEM PROMPT AND BEHAVIORAL PROTOCOLS", "94", True),
    ]

    tbl = doc.add_table(rows=len(toc_entries), cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    # Clear borders
    tblPr = tbl._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="none"/><w:bottom w:val="none"/><w:left w:val="none"/><w:right w:val="none"/>'
        f'<w:insideH w:val="none"/><w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

    for i, (title, page, is_major) in enumerate(toc_entries):
        row = tbl.rows[i]
        c_left = row.cells[0]
        c_right = row.cells[1]

        # Padding
        top_pad = 60 if is_major else 20
        bottom_pad = 60 if is_major else 20
        set_cell_margins(c_left, top=top_pad, bottom=bottom_pad, left=40, right=40)
        set_cell_margins(c_right, top=top_pad, bottom=bottom_pad, left=40, right=40)

        p_l = c_left.paragraphs[0]
        p_l.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_lPr = p_l._p.get_or_add_pPr()
        p_lPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="0" w:after="0"/>'))

        r_l = p_l.add_run(title)
        r_l.font.name = 'Times New Roman'
        r_l.font.size = Pt(10.5 if is_major else 10)
        if is_major:
            r_l.bold = True
            r_l.font.color.rgb = COLOR_PRIMARY_NAVY
        else:
            r_l.font.color.rgb = COLOR_DARK_SLATE

        p_r = c_right.paragraphs[0]
        p_r.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_rPr = p_r._p.get_or_add_pPr()
        p_rPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="0" w:after="0"/>'))

        r_r = p_r.add_run(page)
        r_r.font.name = 'Times New Roman'
        r_r.font.size = Pt(10 if is_major else 9.5)
        if is_major:
            r_r.bold = True
            r_r.font.color.rgb = COLOR_PRIMARY_NAVY
        else:
            r_r.font.color.rgb = COLOR_MUTED_GRAY


def render_list_of_figures(doc):
    """Renders the official List of Figures."""
    figs = p4.LIST_OF_FIGURES
    tbl = doc.add_table(rows=len(figs) + 1, cols=3)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl)

    # Header
    hdr = tbl.rows[0]
    for c, text in enumerate(["Figure No.", "Figure Title & Description", "Page No."]):
        cell = hdr.cells[c]
        set_cell_shading(cell, HEX_HEADER_BG)
        set_cell_margins(cell, top=120, bottom=120, left=120, right=120)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pPr = p._p.get_or_add_pPr()
        pPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="0" w:after="0"/>'))
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(10)
        run.bold = True
        run.font.color.rgb = COLOR_WHITE

    # Rows
    for r_idx, fig in enumerate(figs):
        row = tbl.rows[r_idx + 1]
        is_alt = (r_idx % 2 == 1)
        bg_hex = HEX_ROW_ALT_BG if is_alt else "FFFFFF"

        for col_idx, val in enumerate([fig["num"], fig["caption"], fig["page"]]):
            cell = row.cells[col_idx]
            if is_alt:
                set_cell_shading(cell, bg_hex)
            set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
            p = cell.paragraphs[0]
            pPr = p._p.get_or_add_pPr()
            pPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="0" w:after="0"/>'))
            run = p.add_run(val)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(9.5)
            if col_idx == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run.bold = True
            elif col_idx == 2:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT


def render_list_of_tables(doc):
    """Renders the official List of Tables."""
    tables = p4.LIST_OF_TABLES
    tbl = doc.add_table(rows=len(tables) + 1, cols=3)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl)

    # Header
    hdr = tbl.rows[0]
    for c, text in enumerate(["Table No.", "Table Title & Context", "Page No."]):
        cell = hdr.cells[c]
        set_cell_shading(cell, HEX_HEADER_BG)
        set_cell_margins(cell, top=120, bottom=120, left=120, right=120)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pPr = p._p.get_or_add_pPr()
        pPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="0" w:after="0"/>'))
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(10)
        run.bold = True
        run.font.color.rgb = COLOR_WHITE

    # Rows
    for r_idx, t in enumerate(tables):
        row = tbl.rows[r_idx + 1]
        is_alt = (r_idx % 2 == 1)
        bg_hex = HEX_ROW_ALT_BG if is_alt else "FFFFFF"

        for col_idx, val in enumerate([t["num"], t["caption"], t["page"]]):
            cell = row.cells[col_idx]
            if is_alt:
                set_cell_shading(cell, bg_hex)
            set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
            p = cell.paragraphs[0]
            pPr = p._p.get_or_add_pPr()
            pPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="0" w:after="0"/>'))
            run = p.add_run(val)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(9.5)
            if col_idx == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run.bold = True
            elif col_idx == 2:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT


def build_main_body(doc):
    """Builds Chapters 1 through 7, References, and Appendices A-C with decimal page numbering starting at 1."""
    sec3 = doc.add_section(WD_SECTION.NEW_PAGE)
    configure_section_geometry(sec3)
    sec3.header.is_linked_to_previous = False
    sec3.footer.is_linked_to_previous = False

    # Decimal page numbering starting at 1
    sectPr3 = sec3._sectPr
    sectPr3.append(parse_xml(f'<w:pgNumType {nsdecls("w")} w:fmt="decimal" w:start="1"/>'))

    # Header: Running title
    h3 = sec3.header.paragraphs[0]
    h3.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_h3 = h3.add_run("GENOX: Omni-Capable Autonomous Desktop Agent")
    r_h3.font.name = 'Times New Roman'
    r_h3.font.size = Pt(8.5)
    r_h3.font.italic = True
    r_h3.font.color.rgb = COLOR_MUTED_GRAY

    # Footer: Center-aligned Arabic page numbers
    f3 = sec3.footer.paragraphs[0]
    f3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_f3 = f3.add_run()
    r_f3.font.name = 'Times New Roman'
    r_f3.font.size = Pt(10)
    add_page_number_to_run(r_f3)

    # ---------------- CHAPTER 1 ----------------
    add_heading_1(doc, p1.CHAPTER_1["title"])
    for sec in p1.CHAPTER_1["sections"]:
        render_section_with_attachments(doc, sec["heading"], sec["content"])

    # ---------------- CHAPTER 2 ----------------
    doc.add_page_break()
    add_heading_1(doc, p1.CHAPTER_2["title"])
    for sec in p1.CHAPTER_2["sections"]:
        render_section_with_attachments(doc, sec["heading"], sec["content"])

    # ---------------- CHAPTER 3 ----------------
    doc.add_page_break()
    add_heading_1(doc, p2.CHAPTER_3["title"])
    for sec in p2.CHAPTER_3["sections"]:
        render_section_with_attachments(doc, sec["heading"], sec["content"])

    # ---------------- CHAPTER 4 ----------------
    doc.add_page_break()
    add_heading_1(doc, p2.CHAPTER_4["title"])
    for sec in p2.CHAPTER_4["sections"]:
        render_section_with_attachments(doc, sec["heading"], sec["content"])

    # ---------------- CHAPTER 5 ----------------
    doc.add_page_break()
    add_heading_1(doc, p3.CHAPTER_5["title"])
    for sec in p3.CHAPTER_5["sections"]:
        render_section_with_attachments(doc, sec["heading"], sec["content"])

    # ---------------- CHAPTER 6 ----------------
    doc.add_page_break()
    add_heading_1(doc, p3.CHAPTER_6["title"])
    for sec in p3.CHAPTER_6["sections"]:
        render_section_with_attachments(doc, sec["heading"], sec["content"])

    # ---------------- CHAPTER 7 ----------------
    doc.add_page_break()
    add_heading_1(doc, p4.CHAPTER_7["title"])
    for sec in p4.CHAPTER_7["sections"]:
        render_section_with_attachments(doc, sec["heading"], sec["content"])

    # ---------------- REFERENCES & BIBLIOGRAPHY ----------------
    doc.add_page_break()
    add_heading_1(doc, "REFERENCES & BIBLIOGRAPHY")
    p_ref_intro = doc.add_paragraph()
    p_ref_intro.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r_ref_intro = p_ref_intro.add_run(
        "The following bibliography documents 75 foundational papers, technical standards, conference proceedings, "
        "and industrial software architectures in IEEE bibliographic citation format, substantiating the theoretical, "
        "algorithmic, and empirical foundations of the GENOX autonomous agent architecture:"
    )
    r_ref_intro.font.name = 'Times New Roman'
    r_ref_intro.font.size = Pt(11)
    r_ref_intro.font.italic = True

    for ref_str in p4.REFERENCES:
        p_ref = doc.add_paragraph()
        p_ref.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_refPr = p_ref._p.get_or_add_pPr()
        p_refPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="60" w:after="60" w:line="240" w:lineRule="auto"/>'))
        p_refPr.append(parse_xml(f'<w:ind {nsdecls("w")} w:left="360" w:hanging="360"/>'))

        r = p_ref.add_run(ref_str)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10)
        r.font.color.rgb = COLOR_BODY

    # ---------------- APPENDIX A ----------------
    doc.add_page_break()
    add_heading_1(doc, p4.APPENDIX_A["title"])
    render_content_blocks(doc, p4.APPENDIX_A["content"])

    # ---------------- APPENDIX B ----------------
    doc.add_page_break()
    add_heading_1(doc, p4.APPENDIX_B["title"])
    render_content_blocks(doc, p4.APPENDIX_B["content"])

    # ---------------- APPENDIX C ----------------
    doc.add_page_break()
    add_heading_1(doc, p4.APPENDIX_C["title"])
    render_content_blocks(doc, p4.APPENDIX_C["content"])


def generate_markdown_companion(output_md_path):
    """Compiles the entire report into an exhaustive Markdown companion document."""
    lines = []

    # Front Matter
    lines.append("# " + p1.FRONT_MATTER["title_page"]["project_title"])
    lines.append("## " + p1.FRONT_MATTER["title_page"]["report_type"])
    lines.append(f"**Submitted by:** {p1.FRONT_MATTER['title_page']['student_name']} (Roll: {p1.FRONT_MATTER['title_page']['roll_no']}, Reg: {p1.FRONT_MATTER['title_page']['reg_no']})")
    lines.append(f"**Institution:** {p1.FRONT_MATTER['title_page']['institution_name']}")
    lines.append(f"**Department:** {p1.FRONT_MATTER['title_page']['department']}")
    lines.append(f"**Submission Date:** {p1.FRONT_MATTER['title_page']['submission_date']}\n")

    lines.append("## Project Approval Page\n" + p1.FRONT_MATTER["approval_page"]["cert_text"] + "\n")
    lines.append("## Candidate's Declaration\n" + p1.FRONT_MATTER["declaration"]["text"] + "\n")
    lines.append("## Certificate\n" + p1.FRONT_MATTER["certificate"]["text"] + "\n")
    lines.append("## Acknowledgements\n" + "\n\n".join(p1.FRONT_MATTER["acknowledgement"]["paragraphs"]) + "\n")
    lines.append("## Abstract\n" + "\n\n".join(p1.FRONT_MATTER["abstract"]["paragraphs"]) + "\n")

    # Chapters
    chapters = [
        p1.CHAPTER_1,
        p1.CHAPTER_2,
        p2.CHAPTER_3,
        p2.CHAPTER_4,
        p3.CHAPTER_5,
        p3.CHAPTER_6,
        p4.CHAPTER_7
    ]

    for ch in chapters:
        lines.append(f"# {ch['title']}\n")
        for sec in ch["sections"]:
            lines.append(f"## {sec['heading']}\n")
            lines.append(f"{sec['content']}\n")
            prefix_match = re.match(r'^(\d+\.\d+)', sec['heading'])
            if prefix_match:
                prefix = prefix_match.group(1)
                if prefix in SECTION_ATTACHMENTS:
                    for kind, item_id in SECTION_ATTACHMENTS[prefix]:
                        if kind == "fig" and item_id in FIGURES_MAP:
                            fig_info = FIGURES_MAP[item_id]
                            lines.append(f"\n### {item_id}: {fig_info['title']}\n```text\n{fig_info['diagram']}\n```\n")
                        elif kind == "tbl" and item_id in TABLES_MAP:
                            tbl_info = TABLES_MAP[item_id]
                            lines.append(f"\n### {tbl_info['caption']}\n\n{tbl_info['markdown']}\n")

    # References
    lines.append("# REFERENCES & BIBLIOGRAPHY\n")
    for ref in p4.REFERENCES:
        lines.append(f"{ref}\n")

    # Appendices
    lines.append(f"# {p4.APPENDIX_A['title']}\n{p4.APPENDIX_A['content']}\n")
    lines.append(f"# {p4.APPENDIX_B['title']}\n{p4.APPENDIX_B['content']}\n")
    lines.append(f"# {p4.APPENDIX_C['title']}\n{p4.APPENDIX_C['content']}\n")

    full_md = '\n'.join(lines)
    with open(output_md_path, 'w', encoding='utf-8') as f:
        f.write(full_md)
    print(f"Companion Markdown report successfully written to: {output_md_path}")


def main():
    print("=" * 70)
    print("GENOX: Academic B.Tech Live Project Report Compilation Engine")
    print("Department of Computer Science & Engineering, SRM University Delhi-NCR")
    print("=" * 70)

    doc = docx.Document()

    # Configure Section 1 (Cover Page)
    sec1 = doc.sections[0]
    configure_section_geometry(sec1)
    sec1.header.is_linked_to_previous = False
    sec1.footer.is_linked_to_previous = False

    print("[1/4] Building Title / Cover Page...")
    build_title_page(doc)

    print("[2/4] Building Preliminary Pages (Approval, Declaration, Certificate, Acknowledgements, Abstract, TOC, Lists)...")
    build_preliminary_pages(doc)

    print("[3/4] Building Chapters 1 through 7, References, and Appendices A-C...")
    build_main_body(doc)

    output_docx_path = "/Users/sujaydey/Documents/Genox/GENOX_BTECH_PROJECT_REPORT_80_PAGES.docx"
    output_md_path = "/Users/sujaydey/Documents/Genox/GENOX_BTECH_PROJECT_REPORT_80_PAGES.md"

    print(f"[4/4] Saving production-grade Word document to {output_docx_path}...")
    doc.save(output_docx_path)

    print("Generating Companion Markdown report...")
    generate_markdown_companion(output_md_path)

    file_size_bytes = os.path.getsize(output_docx_path)
    print("=" * 70)
    print(f"REPORT COMPILATION COMPLETED SUCCESSFULLY!")
    print(f"Docx Output: {output_docx_path} ({file_size_bytes / 1024:.1f} KB)")
    print(f"Markdown Output: {output_md_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
