# resume_builder.py - Final Version
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    HRFlowable, Table, TableStyle
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import os

# ── Colors ──
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

    sub_label_style = ParagraphStyle(
        "SubLabelStyle",
        fontSize=8.5,
        textColor=MED_GRAY,
        fontName="Helvetica",
        spaceAfter=2,
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
            HRFlowable(
                width="100%", thickness=1,
                color=PURPLE, spaceAfter=4
            ),
        ]

    def format_bullets(text):
        items = []
        for line in text.strip().split("\n"):
            line = line.strip().lstrip("•*-– ").strip()
            line = line.replace("**", "")
            if line:
                items.append(Paragraph(f"• {line}", bullet_style))
        return items

    story = []

    # ════════════════════════════
    # HEADER
    # ════════════════════════════
    name = student_data.get("name", "Your Name").upper()

    contact_parts = []
    if student_data.get("email"):
        contact_parts.append(student_data["email"])
    if student_data.get("phone"):
        contact_parts.append(student_data["phone"])
    if student_data.get("location"):
        contact_parts.append(student_data["location"])
    contact_line = "   |   ".join(contact_parts)

    # Links line
    links_parts = []
    if student_data.get("linkedin"):
        links_parts.append(f"LinkedIn: {student_data['linkedin']}")
    if student_data.get("github"):
        links_parts.append(f"GitHub: {student_data['github']}")
    links_line = "   |   ".join(links_parts)

    header_rows = [
        [Paragraph(name, name_style)],
        [Paragraph(contact_line, contact_style)],
    ]
    if links_line:
        header_rows.append(
            [Paragraph(links_line, contact_style)]
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
    # ════════════════════════════

    # ── LEFT COLUMN ──
    left = []

    # Professional Summary
    left += section_title("Professional Summary")
    summary = ai_content.get("summary", "").strip()
    if summary:
        summary = summary.replace("**", "")
        left.append(Paragraph(summary, body_style))
    left.append(Spacer(1, 4))

    # Projects
    projects      = student_data.get("projects", [])
    project_descs = ai_content.get("project_descriptions", [])

    if projects:
        left += section_title("Projects")
        for i, project in enumerate(projects):
            left.append(
                Paragraph(f"<b>{project.get('title', '')}</b>", label_style)
            )
            # Get matching AI description
            if i < len(project_descs):
                left += format_bullets(project_descs[i])
            elif project.get("desc"):
                left += format_bullets(project["desc"])
            left.append(Spacer(1, 4))

    # Internships
    internships      = student_data.get("internships", [])
    internship_descs = ai_content.get("internship_descriptions", [])

    if internships:
        left += section_title("Internship / Experience")
        for i, intern in enumerate(internships):
            # Company & Role
            company  = intern.get("company", "")
            role     = intern.get("role", "")
            duration = intern.get("duration", "")

            left.append(
                Paragraph(f"<b>{role}</b> — {company}", label_style)
            )
            if duration:
                left.append(
                    Paragraph(duration, sub_label_style)
                )
            # AI description
            if i < len(internship_descs):
                left += format_bullets(internship_descs[i])
            elif intern.get("desc"):
                left += format_bullets(intern["desc"])
            left.append(Spacer(1, 4))

    # Extra Section
    extra     = student_data.get("extra", "").strip()
    extra_ai  = ai_content.get("extra", "").strip()
    if extra and extra_ai.upper() != "NONE" and extra_ai:
        left += section_title("Additional Information")
        left += format_bullets(extra_ai)
        left.append(Spacer(1, 4))

    # ── RIGHT COLUMN (Sidebar) ──
    right = []

    # Education
    right.append(Paragraph("EDUCATION", side_heading))
    right.append(HRFlowable(
        width="100%", thickness=1,
        color=PURPLE, spaceAfter=4
    ))
    degree  = student_data.get("degree", "")
    college = student_data.get("college", "")
    if degree:
        right.append(Paragraph(f"<b>{degree}</b>", side_body))
    if college:
        right.append(Paragraph(college, side_body))
    if student_data.get("grad_year"):
        right.append(
            Paragraph(
                f"Graduating: {student_data['grad_year']}", side_body
            )
        )
    if student_data.get("percentage"):
        right.append(
            Paragraph(
                f"CGPA: {student_data['percentage']}", side_body
            )
        )
    right.append(Spacer(1, 6))

    # Skills
    right.append(Paragraph("SKILLS", side_heading))
    right.append(HRFlowable(
        width="100%", thickness=1,
        color=PURPLE, spaceAfter=4
    ))
    skills = ai_content.get("skills", "").strip()
    if skills:
        skill_list = [
            s.strip()
            for s in skills.replace(";", ",").split(",")
        ]
        for skill in skill_list:
            skill = skill.replace("**", "").strip()
            if skill:
                right.append(Paragraph(f"▸ {skill}", side_body))
    right.append(Spacer(1, 6))

    # Achievements
    ach_raw = student_data.get("achievements", "").strip()
    ach_ai  = ai_content.get("achievements", "").strip()
    if ach_raw:
        right.append(Paragraph("ACHIEVEMENTS", side_heading))
        right.append(HRFlowable(
            width="100%", thickness=1,
            color=PURPLE, spaceAfter=4
        ))
        if ach_ai:
            for line in ach_ai.strip().split("\n"):
                line = line.strip().lstrip("•*-– ").strip()
                line = line.replace("**", "")
                if line:
                    right.append(Paragraph(f"▸ {line}", side_body))
        else:
            right.append(Paragraph(f"▸ {ach_raw}", side_body))
        right.append(Spacer(1, 6))

    # GitHub on Sidebar
    github = student_data.get("github", "").strip()
    if github:
        right.append(Paragraph("GITHUB", side_heading))
        right.append(HRFlowable(
            width="100%", thickness=1,
            color=PURPLE, spaceAfter=4
        ))
        right.append(Paragraph(f"▸ {github}", side_body))
        right.append(Spacer(1, 6))

    # ── PAD COLUMNS ──
    max_len = max(len(left), len(right))
    while len(left)  < max_len:
        left.append(Spacer(1, 1))
    while len(right) < max_len:
        right.append(Spacer(1, 1))

    # ── TWO COLUMN TABLE ──
    two_col = Table(
        [[left, right]],
        colWidths=[125 * mm, 55 * mm],
    )
    two_col.setStyle(TableStyle([
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",  (0, 0), (0, -1), 0),
        ("RIGHTPADDING", (0, 0), (0, -1), 8),
        ("LEFTPADDING",  (1, 0), (1, -1), 8),
        ("RIGHTPADDING", (1, 0), (1, -1), 0),
        ("BACKGROUND",   (1, 0), (1, -1), ACCENT),
    ]))
    story.append(two_col)

    # ── BUILD PDF ──
    doc.build(story)
    return output_path 