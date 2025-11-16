#!/usr/bin/env python3
# make_pdf_report.py (Corporate Theme)

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime

# === Paths ===
REPORT_OUTPUT = "liverpool_fan_report.pdf"
WORDCLOUD_LFC = "liverpool_player_wordcloud.png"
WORDCLOUD_OPP = "opponent_player_wordcloud.png"
ANALYSIS_TEXT_FILE = "final_fan_report.txt"

# === Corporate Styles ===
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="TitleCorporate",
    fontSize=28,
    leading=32,
    alignment=1,  # center
    spaceAfter=20
))
styles.add(ParagraphStyle(
    name="SubTitleCorporate",
    fontSize=16,
    leading=20,
    alignment=1,  # center
    textColor=colors.grey,
    spaceAfter=10
))
styles.add(ParagraphStyle(
    name="SectionHeader",
    fontSize=18,
    leading=22,
    spaceBefore=16,
    spaceAfter=8,
    textColor=colors.HexColor("#333333")
))
styles.add(ParagraphStyle(
    name="BodyTextCorporate",
    fontSize=11,
    leading=15,
    spaceAfter=6
))

# Footer with page numbers
def add_page_number(canvas, doc):
    page_num = canvas.getPageNumber()
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.grey)
    canvas.drawRightString(
        A4[0] - 40,
        20,
        f"Page {page_num}"
    )

# === Build PDF ===
def build_pdf():
    date_str = datetime.now().strftime("%B %d, %Y")

    doc = SimpleDocTemplate(
        REPORT_OUTPUT,
        pagesize=A4,
        leftMargin=50,
        rightMargin=50,
        topMargin=60,
        bottomMargin=50
    )
    story = []

    # --- Title Page ---
    story.append(Paragraph("FootyPulse", styles["TitleCorporate"]))
    story.append(Paragraph("Liverpool FC Matchday Fan Report", styles["SubTitleCorporate"]))
    story.append(Paragraph(date_str, styles["SubTitleCorporate"]))
    story.append(Spacer(1, 0.6 * inch))

    # Divider line
    table = Table([['']], colWidths=[450])
    table.setStyle(TableStyle([('LINEBELOW', (0,0), (-1,-1), 1, colors.grey)]))
    story.append(table)
    story.append(Spacer(1, 1.2 * inch))

    story.append(Paragraph(
        "<font size=12 color='grey'>Generated automatically with the FootyPulse analytics pipeline.</font>",
        styles["BodyTextCorporate"]
    ))
    story.append(PageBreak())

    # --- Load final report text ---
    try:
        with open(ANALYSIS_TEXT_FILE, "r", encoding="utf-8") as f:
            analysis_html = f.read().replace("\n", "<br/>")
    except:
        analysis_html = "<b>ERROR:</b> Could not load final_fan_report.txt"

    story.append(Paragraph("Final Fanbase Report", styles["SectionHeader"]))
    story.append(Paragraph(analysis_html, styles["BodyTextCorporate"]))
    story.append(PageBreak())

    # --- Liverpool Word Cloud ---
    story.append(Paragraph("Liverpool Player Mentions", styles["SectionHeader"]))
    story.append(Spacer(1, 0.2 * inch))

    try:
        img1 = Image(WORDCLOUD_LFC)
        img1._restrictSize(6 * inch, 7.5 * inch)
        story.append(img1)
    except:
        story.append(Paragraph("Missing Liverpool wordcloud image.", styles["BodyTextCorporate"]))

    story.append(PageBreak())

    # --- Opponent Word Cloud ---
    story.append(Paragraph("Opponent Player Mentions", styles["SectionHeader"]))
    story.append(Spacer(1, 0.2 * inch))

    try:
        img2 = Image(WORDCLOUD_OPP)
        img2._restrictSize(6 * inch, 7.5 * inch)
        story.append(img2)
    except:
        story.append(Paragraph("Missing opponent wordcloud image.", styles["BodyTextCorporate"]))

    # Build PDF with page numbers
    doc.build(story, onLaterPages=add_page_number, onFirstPage=add_page_number)

    print("PDF SAVED:", REPORT_OUTPUT)


if __name__ == "__main__":
    build_pdf()
