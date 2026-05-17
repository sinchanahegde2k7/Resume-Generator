# resume_builder.py - Premium Version
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    HRFlowable, Table, TableStyle, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
import os

# ── Color Theme ──
PURPLE      = colors.HexColor("#5C6BC0")
DARK_PURPLE = colors.HexColor("#3949AB")
DARK_GRAY   = colors.HexColor("#212121")
MED_GRAY    = colors.HexColor("#616161")
LIGHT_GRAY  = colors.HexColor("#F5F5F5")
ACCENT      = colors.HexColor("#E8EAF6")
WHITE       = colors.white


def build_resume_pdf(student_data, ai_content, output_path="resume_output.pdf"):

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=12 * mm,
        leftMargin=12 * mm,
        topMargin=10 * mm,
        bottomMargin=10 * mm,
    )

    # ── Styles ──
    name_style = ParagraphStyle(
        "NameStyle",
        fontSize=24,
        textColor=WHITE,
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
        spaceAfter=0,
        spaceBefore=0,
    )

    contact_style = ParagraphStyle(
        "ContactStyle",
        fontSize=8.5,
        textColor=WHITE,
        alignment=TA_CENTER,
        fontName="Helvetica",
        spaceAfter=0,
        spaceBefore=2,
    )

    section_heading = ParagraphStyle(
        "SectionHeading",
        fontSize=10,
        textColor=PURPLE,
        fontName="Helvetica-Bold",
        spaceBefore=8,
        spaceAfter=3,
    )

    body_style = ParagraphStyle(
        "BodyStyle",
        fontSize=9,
        textColor=DARK_GRAY,
        fontName="Helvetica",
        spaceAfter=2,
        leading=13,
    )

    bullet_style = ParagraphStyle(
        "BulletStyle",
        fontSize=9,
        textColor=DARK_GRAY,
        fontName="Helvetica",
        spaceAfter=2,
        leading=13,
        leftIndent=10,
    )

    label_style = ParagraphStyle(
        "LabelStyle",
        fontSize=9.5,
        textColor=DARK_GRAY,
        fontName="Helvetica-Bold",
        spaceAfter=2,
        spaceBefore=4,
    )

    side_heading = ParagraphStyle(
        "SideHeading",
        fontSize=9,
        textColor=PURPLE,
        fontName="Helvetica-Bold",
        spaceAfter=3,
        spaceBefore=6,
    )

    side_body = ParagraphStyle(
        "SideBody",
        fontSize=8.5,
        textColor=DARK_GRAY,
        fontName="Helvetica",
        spaceAfter=2,
        leading=12,
    )

    # ── Helpers ──
    def section_title(title):
        return [
            Paragraph(title.upper(), section_heading),
            HRFlowable(width="100%", thickness=1,
                       color=PURPLE, spaceAfter=4),
        ]

    def format_bullets(text):
        items = []
        for line in text.strip().split("\n"):
            line = line.strip().lstrip("•*-– ").strip()
            if line:
                items.append(Paragraph(f"• {line}", bullet_style))
        return items

    story = []

    # ════════════════════════════
    # HEADER
    # ════════════════════════════
    name = student_data.get("name", "Your Name").upper()

    # Build contact line smartly
    contact_parts = []
    if student_data.get("email"):
        contact_parts.append(student_data["email"])
    if student_data.get("phone"):
        contact_parts.append(student_data["phone"])
    if student_data.get("location"):
        contact_parts.append(student_data["location"])
    contact_line = "   |   ".join(contact_parts)

    linkedin = student_data.get("linkedin", "").strip()

    # Header rows
    header_rows = [
        [Paragraph(name, name_style)],
        [Paragraph(contact_line, contact_style)],
    ]
    if linkedin:
        header_rows.append(
            [Paragraph(f"LinkedIn: {linkedin}", contact_style)]
        )

    header_table = Table(header_rows, colWidths=["100%"])
    header_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), PURPLE),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING",    (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 6))

    # ════════════════════════════
    # TWO COLUMN LAYOUT
    # LEFT: Main Content
    # RIGHT: Sidebar
    # ════════════════════════════

    # ── LEFT COLUMN ──
    left = []

    # Professional Summary
    left += section_title("Professional Summary")
    summary = ai_content.get("summary", "").strip()
    if summary:
        # Remove any leading asterisks or bold markers
        summary = summary.replace("**", "")
        left.append(Paragraph(summary, body_style))

    left.append(Spacer(1, 4))

    # Projects
    left += section_title("Projects")

    p1_raw  = student_data.get("project1", "").strip()
    p1_name = p1_raw.split("—")[0].split("-")[0].strip()
    if p1_name:
        left.append(Paragraph(f"<b>{p1_name}</b>", label_style))
    p1_desc = ai_content.get("project1_desc", "")
    if p1_desc:
        left += format_bullets(p1_desc)

    p2_raw = student_data.get("project2", "").strip()
    if p2_raw:
        p2_name = p2_raw.split("—")[0].split("-")[0].strip()
        left.append(Spacer(1, 4))
        left.append(Paragraph(f"<b>{p2_name}</b>", label_style))
        p2_desc = ai_content.get("project2_desc", "")
        if p2_desc:
            left += format_bullets(p2_desc)

    left.append(Spacer(1, 4))

    # Experience
    exp_raw  = student_data.get("experience", "").strip()
    exp_desc = ai_content.get("experience", "").strip()
    if exp_raw and exp_desc:
        left += section_title("Experience")
        left.append(Paragraph(f"<b>{exp_raw}</b>", label_style))
        left += format_bullets(exp_desc)
        left.append(Spacer(1, 4))

    # ── RIGHT COLUMN (Sidebar) ──
    right = []

    # Education
    right.append(Paragraph("EDUCATION", side_heading))
    right.append(HRFlowable(width="100%", thickness=1,
                             color=PURPLE, spaceAfter=4))
    degree  = student_data.get("degree", "")
    college = student_data.get("college", "")
    if degree:
        right.append(Paragraph(f"<b>{degree}</b>", side_body))
    if college:
        right.append(Paragraph(college, side_body))
    if student_data.get("grad_year"):
        right.append(
            Paragraph(f"Graduating: {student_data['grad_year']}", side_body)
        )
    if student_data.get("percentage"):
        right.append(
            Paragraph(f"CGPA: {student_data['percentage']}", side_body)
        )

    right.append(Spacer(1, 6))

    # Skills
    right.append(Paragraph("SKILLS", side_heading))
    right.append(HRFlowable(width="100%", thickness=1,
                             color=PURPLE, spaceAfter=4))
    skills = ai_content.get("skills", "").strip()
    if skills:
        # Split skills into individual items for sidebar
        skill_list = [s.strip() for s in skills.replace(";", ",").split(",")]
        for skill in skill_list:
            if skill:
                right.append(Paragraph(f"▸ {skill}", side_body))

    right.append(Spacer(1, 6))

    # Achievements
    ach_raw  = student_data.get("achievements", "").strip()
    ach_desc = ai_content.get("achievements", "").strip()
    if ach_raw:
        right.append(Paragraph("ACHIEVEMENTS", side_heading))
        right.append(HRFlowable(width="100%", thickness=1,
                                 color=PURPLE, spaceAfter=4))
        if ach_desc:
            for line in ach_desc.strip().split("\n"):
                line = line.strip().lstrip("•*-– ").strip()
                if line:
                    right.append(Paragraph(f"▸ {line}", side_body))
        else:
            right.append(Paragraph(f"▸ {ach_raw}", side_body))

    # ── COMBINE INTO TWO COLUMNS ──
    # Pad shorter column
    max_len = max(len(left), len(right))
    while len(left)  < max_len:
        left.append(Spacer(1, 1))
    while len(right) < max_len:
        right.append(Spacer(1, 1))

    # Build two-column table
    two_col = Table(
        [[left, right]],
        colWidths=[125 * mm, 55 * mm],
    )
    two_col.setStyle(TableStyle([
        ("VALIGN",      (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",  (0, 0), (0, -1), 0),
        ("RIGHTPADDING", (0, 0), (0, -1), 8),
        ("LEFTPADDING",  (1, 0), (1, -1), 8),
        ("RIGHTPADDING", (1, 0), (1, -1), 0),
        ("BACKGROUND",   (1, 0), (1, -1), ACCENT),
        ("ROUNDEDCORNERS", [4]),
    ]))

    story.append(two_col)

    # ── BUILD PDF ──
    doc.build(story)
    return output_path 