import os
from datetime import date
from dotenv import load_dotenv

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)

load_dotenv()


def _parse_ai_sections(ai_report: str) -> dict[str, str]:
    """Split AI report string by ## headers into a dict."""
    sections = {}
    current_key = None
    current_lines = []

    for line in ai_report.split("\n"):
        if line.startswith("## "):
            if current_key:
                sections[current_key] = "\n".join(current_lines).strip()
            current_key = line[3:].strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_key:
        sections[current_key] = "\n".join(current_lines).strip()

    return sections


def _add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.grey)
    canvas.drawRightString(
        letter[0] - 0.5 * inch,
        0.4 * inch,
        f"Page {doc.page}"
    )
    canvas.restoreState()


def generate_pdf(kpi_summary: dict, ai_report: str, output_path: str) -> str:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    company = os.getenv("COMPANY_NAME", "Your Company")
    today = date.today().strftime("%B %d, %Y")

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    styles = getSampleStyleSheet()
    header_style = ParagraphStyle(
        "Header",
        parent=styles["Heading1"],
        fontSize=20,
        textColor=colors.HexColor("#2c3e50"),
        spaceAfter=6,
    )
    subheader_style = ParagraphStyle(
        "SubHeader",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#2c3e50"),
        spaceBefore=16,
        spaceAfter=8,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontSize=10,
        leading=14,
        spaceAfter=6,
    )
    caption_style = ParagraphStyle(
        "Caption",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.grey,
        spaceAfter=20,
    )

    story = []
    ai_sections = _parse_ai_sections(ai_report)

    # ── Cover / Header ─────────────────────────────────────────────────────────
    story.append(Paragraph("AI Executive Portfolio Report", header_style))
    story.append(Paragraph(f"{company} &nbsp;·&nbsp; {today}", caption_style))
    story.append(Spacer(1, 0.2 * inch))

    # ── Executive Summary ──────────────────────────────────────────────────────
    story.append(Paragraph("Executive Summary", subheader_style))
    summary_text = ai_sections.get("Executive Summary", "Not available.")
    for para in summary_text.split("\n\n"):
        if para.strip():
            story.append(Paragraph(para.strip(), body_style))
    story.append(Spacer(1, 0.1 * inch))

    # ── KPI Dashboard ──────────────────────────────────────────────────────────
    story.append(Paragraph("KPI Dashboard", subheader_style))

    kpi_data = [
        ["Metric", "Value"],
        ["Total Projects", str(kpi_summary["total_projects"])],
        ["On Track", f"{kpi_summary['pct_on_track']:.1f}%"],
        ["At Risk", f"{kpi_summary['pct_at_risk']:.1f}%"],
        ["Delayed", f"{kpi_summary['pct_delayed']:.1f}%"],
        ["Completed", f"{kpi_summary['pct_completed']:.1f}%"],
        ["Total Budget Variance",
         f"${kpi_summary['total_budget_variance']:,.0f} ({kpi_summary['total_budget_variance_pct']:+.1f}%)"],
        ["Avg Schedule Delay (late projects)",
         f"{kpi_summary['avg_schedule_delay_days']:.1f} days"],
    ]

    kpi_table = Table(kpi_data, colWidths=[3.5 * inch, 3.5 * inch])
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND",     (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
        ("TEXTCOLOR",      (0, 0), (-1, 0), colors.white),
        ("FONTNAME",       (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",       (0, 0), (-1, 0), 11),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")]),
        ("FONTSIZE",       (0, 1), (-1, -1), 10),
        ("GRID",           (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
        ("TOPPADDING",     (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 6),
        ("LEFTPADDING",    (0, 0), (-1, -1), 10),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 0.2 * inch))

    # ── Risk Analysis ──────────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("Risk Analysis", subheader_style))

    risk_headers = ["Project", "Dept", "Budget Var %", "Delay (days)", "Risk", "Over Budget", "Late"]
    risk_rows = [risk_headers]

    for p in kpi_summary["all_projects"]:
        risk_rows.append([
            str(p.get("project_name", "")),
            str(p.get("department", "")),
            f"{p.get('budget_variance_pct', 0):+.1f}%",
            str(p.get("schedule_delay_days", 0)),
            str(p.get("risk_level", "")).upper(),
            "Yes" if p.get("is_over_budget") else "No",
            "Yes" if p.get("is_late") else "No",
        ])

    col_widths = [2.2 * inch, 1.0 * inch, 0.9 * inch, 0.9 * inch, 0.7 * inch, 0.75 * inch, 0.6 * inch]
    risk_table = Table(risk_rows, colWidths=col_widths, repeatRows=1)
    risk_table.setStyle(TableStyle([
        ("BACKGROUND",     (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
        ("TEXTCOLOR",      (0, 0), (-1, 0), colors.white),
        ("FONTNAME",       (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",       (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")]),
        ("GRID",           (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
        ("TOPPADDING",     (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 4),
        ("LEFTPADDING",    (0, 0), (-1, -1), 6),
    ]))
    story.append(risk_table)

    # ── AI Recommendations ─────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("AI Recommendations", subheader_style))

    for section_name in ["Key Risks", "Budget Concerns", "Schedule Delays", "Recommended Actions"]:
        text = ai_sections.get(section_name, "")
        if text:
            story.append(Paragraph(section_name, ParagraphStyle(
                "SectionTitle", parent=styles["Heading3"],
                fontSize=11, textColor=colors.HexColor("#495057"), spaceBefore=12
            )))
            for para in text.split("\n\n"):
                if para.strip():
                    story.append(Paragraph(para.strip().replace("\n", "<br/>"), body_style))

    doc.build(story, onLaterPages=_add_page_number, onFirstPage=_add_page_number)
    return output_path
