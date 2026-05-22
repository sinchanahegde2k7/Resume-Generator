# resume_builder.py
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph,
    Spacer, HRFlowable, Table, TableStyle
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import Image as RLImage
import os

# ── Palette ──
PURPLE = colors.HexColor("#5C6BC0")
DARK   = colors.HexColor("#1a1a2e")
GRAY   = colors.HexColor("#555555")
LGRAY  = colors.HexColor("#888888")
ACCENT = colors.HexColor("#EEF0FF")
WHITE  = colors.white


def build_resume_pdf(student_data, ai_content, output_path):

    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        rightMargin=12*mm, leftMargin=12*mm,
        topMargin=10*mm,   bottomMargin=12*mm,
    )

    # ── Styles ──
    def S(name, **kw):
        return ParagraphStyle(name, **kw)

    NAME = S("NAME",
        fontSize=22, textColor=WHITE,
        fontName="Helvetica-Bold",
        alignment=TA_LEFT, leading=26)

    CONTACT = S("CONTACT",
        fontSize=8, textColor=WHITE,
        fontName="Helvetica",
        alignment=TA_LEFT, leading=13, spaceBefore=2)

    SEC_HEAD = S("SEC_HEAD",
        fontSize=9.5, textColor=PURPLE,
        fontName="Helvetica-Bold",
        spaceBefore=10, spaceAfter=2)

    BODY = S("BODY",
        fontSize=9, textColor=DARK,
        fontName="Helvetica",
        leading=14, spaceAfter=2)

    BULLET = S("BULLET",
        fontSize=9, textColor=DARK,
        fontName="Helvetica",
        leading=14, spaceAfter=2,
        leftIndent=8)

    LABEL = S("LABEL",
        fontSize=9.5, textColor=DARK,
        fontName="Helvetica-Bold",
        spaceAfter=1, spaceBefore=5)

    SUBLABEL = S("SUBLABEL",
        fontSize=8, textColor=LGRAY,
        fontName="Helvetica",
        spaceAfter=2)

    R_HEAD = S("R_HEAD",
        fontSize=8.5, textColor=PURPLE,
        fontName="Helvetica-Bold",
        spaceBefore=8, spaceAfter=2)

    R_BODY = S("R_BODY",
        fontSize=8, textColor=DARK,
        fontName="Helvetica",
        leading=12, spaceAfter=2)

    # ── Helpers ──
    def divider():
        return HRFlowable(
            width="100%", thickness=0.8,
            color=PURPLE, spaceAfter=4
        )

    def sec(title):
        return [Paragraph(title.upper(), SEC_HEAD), divider()]

    def bullets(text):
        out = []
        for line in text.strip().split("\n"):
            line = line.strip().lstrip("•*-–▸■ ").strip()
            if line:
                out.append(Paragraph(f"• {line}", BULLET))
        return out

    def r_sec(title):
        return [Paragraph(title.upper(), R_HEAD), divider()]

    def r_bullets(text):
        out = []
        for line in text.strip().split("\n"):
            line = line.strip().lstrip("•*-–▸■ ").strip()
            if line:
                out.append(Paragraph(f"▸ {line}", R_BODY))
        return out

    story = []

    # ════════════════════════════════════
    # HEADER
    # ════════════════════════════════════
    name = student_data.get("name", "").upper()

    contacts = []
    if student_data.get("email"):
        contacts.append(student_data["email"])
    if student_data.get("phone"):
        contacts.append(student_data["phone"])
    if student_data.get("location"):
        contacts.append(student_data["location"])

    links = []
    if student_data.get("linkedin"):
        links.append(f"in/ {student_data['linkedin']}")
    if student_data.get("github"):
        links.append(f"gh/ {student_data['github']}")

    left_header = [
        Paragraph(name, NAME),
        Paragraph("  |  ".join(contacts), CONTACT),
    ]
    if links:
        left_header.append(Paragraph("  |  ".join(links), CONTACT))

    # Photo
    photo_path = student_data.get("photo_path")
    if photo_path and os.path.exists(photo_path):
        try:
            photo_cell = RLImage(photo_path, width=24*mm, height=24*mm)
        except:
            photo_cell = Paragraph("", CONTACT)
    else:
        photo_cell = Paragraph("", CONTACT)

    hdr = Table(
        [[left_header, photo_cell]],
        colWidths=[148*mm, 26*mm]
    )
    hdr.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), PURPLE),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("ALIGN",         (1,0), (1,-1),  "CENTER"),
        ("TOPPADDING",    (0,0), (-1,-1), 14),
        ("BOTTOMPADDING", (0,0), (-1,-1), 14),
        ("LEFTPADDING",   (0,0), (0,-1),  14),
        ("RIGHTPADDING",  (1,0), (1,-1),   8),
    ]))
    story.append(hdr)
    story.append(Spacer(1, 8))

    # ════════════════════════════════════
    # LEFT COLUMN
    # ════════════════════════════════════
    L = []

    # Summary
    L += sec("Professional Summary")
    summary = ai_content.get("summary", "").strip()
    if summary:
        L.append(Paragraph(summary, BODY))
    L.append(Spacer(1, 4))

    # Projects
    projects  = student_data.get("projects", [])
    p_descs   = ai_content.get("project_descriptions", [])
    if projects:
        L += sec("Projects")
        for i, p in enumerate(projects):
            L.append(Paragraph(f"<b>{p.get('title','')}</b>", LABEL))
            desc = p_descs[i] if i < len(p_descs) else p.get("desc","")
            if desc:
                L += bullets(desc)
            L.append(Spacer(1, 4))

    # Internships
    internships = student_data.get("internships", [])
    i_descs     = ai_content.get("internship_descriptions", [])
    if internships:
        L += sec("Internship / Experience")
        for i, n in enumerate(internships):
            role     = n.get("role", "")
            company  = n.get("company", "")
            duration = n.get("duration", "")
            if role or company:
                L.append(
                    Paragraph(
                        f"<b>{role}</b>" + (f" — {company}" if company else ""),
                        LABEL
                    )
                )
            if duration:
                L.append(Paragraph(duration, SUBLABEL))
            desc = i_descs[i] if i < len(i_descs) else n.get("desc","")
            if desc:
                L += bullets(desc)
            L.append(Spacer(1, 4))

    # Extra
    extra = ai_content.get("extra", "").strip()
    if extra:
        L += sec("Additional Information")
        L += bullets(extra)
        L.append(Spacer(1, 4))

    # ════════════════════════════════════
    # RIGHT COLUMN
    # ════════════════════════════════════
    R = []

    # Education
    R += r_sec("Education")
    R.append(Paragraph(f"<b>{student_data.get('degree','')}</b>", R_BODY))
    R.append(Paragraph(student_data.get("college",""), R_BODY))
    if student_data.get("grad_year"):
        R.append(Paragraph(f"Year: {student_data['grad_year']}", R_BODY))
    if student_data.get("percentage"):
        R.append(Paragraph(f"CGPA: {student_data['percentage']}", R_BODY))

    # PG
    if student_data.get("pg_degree"):
        R.append(Spacer(1, 6))
        R.append(Paragraph("<b>Post Graduation</b>", R_BODY))
        R.append(Paragraph(f"<b>{student_data['pg_degree']}</b>", R_BODY))
        if student_data.get("pg_college"):
            R.append(Paragraph(student_data["pg_college"], R_BODY))
        if student_data.get("pg_year"):
            R.append(Paragraph(f"Year: {student_data['pg_year']}", R_BODY))
        if student_data.get("pg_percentage"):
            R.append(Paragraph(f"CGPA: {student_data['pg_percentage']}", R_BODY))

    R.append(Spacer(1, 4))

    # Skills
    skills = ai_content.get("skills", "").strip()
    if skills:
        R += r_sec("Skills")
        for sk in skills.replace(";",",").split(","):
            sk = sk.strip()
            if sk:
                R.append(Paragraph(f"▸ {sk}", R_BODY))
        R.append(Spacer(1, 4))

    # Achievements
    ach_raw = student_data.get("achievements","").strip()
    ach_ai  = ai_content.get("achievements","").strip()
    if ach_raw:
        R += r_sec("Achievements")
        src = ach_ai if ach_ai else ach_raw
        R += r_bullets(src)
        R.append(Spacer(1, 4))

    # GitHub
    github = student_data.get("github","").strip()
    if github:
        R += r_sec("GitHub")
        R.append(Paragraph(f"▸ {github}", R_BODY))
        R.append(Spacer(1, 4))

    # Job Targets
    job_roles = student_data.get("job_roles","").strip()
    if job_roles:
        R += r_sec("Job Targets")
        for role in job_roles.split(","):
            role = role.strip()
            if role:
                R.append(Paragraph(f"▸ {role}", R_BODY))
        R.append(Spacer(1, 4))

    # ── Pad shorter column ──
    mx = max(len(L), len(R))
    L += [Spacer(1,1)] * (mx - len(L))
    R += [Spacer(1,1)] * (mx - len(R))

    # ── Two Column Table ──
    body = Table([[L, R]], colWidths=[124*mm, 56*mm])
    body.setStyle(TableStyle([
        ("VALIGN",       (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING",  (0,0), (0,-1),  0),
        ("RIGHTPADDING", (0,0), (0,-1),  10),
        ("LEFTPADDING",  (1,0), (1,-1),  10),
        ("RIGHTPADDING", (1,0), (1,-1),  0),
        ("BACKGROUND",   (1,0), (1,-1),  ACCENT),
    ]))
    story.append(body)

    doc.build(story)
    return output_path