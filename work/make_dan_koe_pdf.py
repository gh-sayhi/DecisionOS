from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "outputs" / "dan-koe-recent-hot-articles-cn.md"
OUTPUT = ROOT / "outputs" / "dan-koe-recent-hot-articles-cn.pdf"


FONT_NAME = "STHeiti-Light"
pdfmetrics.registerFont(TTFont(FONT_NAME, "/System/Library/Fonts/STHeiti Light.ttc"))


def clean_inline(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    return text


styles = getSampleStyleSheet()
base = {
    "fontName": "STHeiti-Light",
    "wordWrap": "CJK",
    "spaceAfter": 6,
}

styles.add(
    ParagraphStyle(
        name="CNTitle",
        parent=styles["Title"],
        fontName="STHeiti-Light",
        fontSize=24,
        leading=32,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1f2937"),
        spaceAfter=16,
    )
)
styles.add(
    ParagraphStyle(
        name="CNSubtle",
        parent=styles["Normal"],
        **base,
        fontSize=9.5,
        leading=15,
        textColor=colors.HexColor("#6b7280"),
    )
)
styles.add(
    ParagraphStyle(
        name="CNBody",
        parent=styles["BodyText"],
        **base,
        fontSize=10.5,
        leading=17,
        firstLineIndent=0,
        textColor=colors.HexColor("#111827"),
    )
)
styles.add(
    ParagraphStyle(
        name="CNH1",
        parent=styles["Heading1"],
        fontName="STHeiti-Light",
        fontSize=18,
        leading=24,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=12,
        spaceAfter=10,
        keepWithNext=True,
    )
)
styles.add(
    ParagraphStyle(
        name="CNH2",
        parent=styles["Heading2"],
        fontName="STHeiti-Light",
        fontSize=14,
        leading=20,
        textColor=colors.HexColor("#1f2937"),
        spaceBefore=10,
        spaceAfter=7,
        keepWithNext=True,
    )
)
styles.add(
    ParagraphStyle(
        name="CNList",
        parent=styles["BodyText"],
        fontName="STHeiti-Light",
        fontSize=10.5,
        leading=17,
        leftIndent=14,
        firstLineIndent=-10,
        wordWrap="CJK",
        textColor=colors.HexColor("#111827"),
        spaceAfter=4,
    )
)
styles.add(
    ParagraphStyle(
        name="CNTable",
        parent=styles["BodyText"],
        fontName="STHeiti-Light",
        fontSize=8.8,
        leading=12,
        wordWrap="CJK",
        textColor=colors.HexColor("#111827"),
    )
)
styles.add(
    ParagraphStyle(
        name="CNFooter",
        parent=styles["Normal"],
        fontName="STHeiti-Light",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#6b7280"),
    )
)


def page_canvas(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#e5e7eb"))
    canvas.line(22 * mm, 17 * mm, 188 * mm, 17 * mm)
    canvas.setFont("STHeiti-Light", 8)
    canvas.setFillColor(colors.HexColor("#6b7280"))
    canvas.drawString(22 * mm, 11 * mm, "Dan Koe 近期热门文章中文整理文档")
    canvas.drawRightString(188 * mm, 11 * mm, f"{doc.page}")
    canvas.restoreState()


def parse_table(lines, start):
    table_lines = []
    i = start
    while i < len(lines) and lines[i].strip().startswith("|"):
        table_lines.append(lines[i].strip())
        i += 1
    rows = []
    for line in table_lines:
        cells = [c.strip() for c in line.strip("|").split("|")]
        if all(set(c) <= {"-", ":", " "} for c in cells):
            continue
        rows.append([Paragraph(clean_inline(c), styles["CNTable"]) for c in cells])
    return rows, i


def build_story():
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    story = []

    title = lines[0].lstrip("# ").strip()
    story.append(Spacer(1, 18 * mm))
    story.append(Paragraph(title, styles["CNTitle"]))
    story.append(
        Paragraph(
            "PDF 版整理导读 - 包含中文归纳、结构化重写、行动计划与原文链接。",
            styles["CNSubtle"],
        )
    )
    story.append(
        Paragraph(
            "版权说明：本文档不包含 Dan Koe 文章的未经授权全文原文；如需阅读英文原文，请使用文末链接访问作者官网。",
            styles["CNSubtle"],
        )
    )
    story.append(Spacer(1, 8 * mm))
    story.append(PageBreak())

    i = 1
    while i < len(lines):
        raw = lines[i]
        line = raw.strip()
        if not line:
            i += 1
            continue
        if line.startswith("# "):
            story.append(Paragraph(clean_inline(line[2:]), styles["CNH1"]))
        elif line.startswith("## "):
            story.append(Paragraph(clean_inline(line[3:]), styles["CNH1"]))
        elif line.startswith("### "):
            story.append(Paragraph(clean_inline(line[4:]), styles["CNH2"]))
        elif line.startswith("|"):
            rows, i = parse_table(lines, i)
            if rows:
                widths = [50 * mm, 32 * mm, 82 * mm] if len(rows[0]) == 3 else None
                table = Table(rows, colWidths=widths, hAlign="LEFT", repeatRows=1)
                table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f3f4f6")),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#111827")),
                            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#d1d5db")),
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("LEFTPADDING", (0, 0), (-1, -1), 5),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                            ("TOPPADDING", (0, 0), (-1, -1), 5),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                        ]
                    )
                )
                story.append(table)
                story.append(Spacer(1, 5 * mm))
            continue
        elif re.match(r"^\d+\.\s+", line):
            story.append(Paragraph(clean_inline(re.sub(r"^(\d+\.)\s+", r"\1 ", line)), styles["CNList"]))
        elif line.startswith("- "):
            story.append(Paragraph("• " + clean_inline(line[2:]), styles["CNList"]))
        else:
            story.append(Paragraph(clean_inline(line), styles["CNBody"]))
        i += 1
    return story


def main():
    doc = BaseDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=22 * mm,
        rightMargin=22 * mm,
        topMargin=20 * mm,
        bottomMargin=23 * mm,
        title="Dan Koe 近期热门文章中文整理文档",
        author="Codex",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=page_canvas)])
    doc.build(build_story())
    print(OUTPUT)


if __name__ == "__main__":
    main()
