# ai_generator.py
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_resume_content(data):

    # ── Format Projects ──
    projects_text = ""
    for i, project in enumerate(data.get("projects", []), 1):
        projects_text += f"""
    Project {i}: {project.get('title', '')}
    Description: {project.get('desc', '')}
    """

    # ── Format Internships ──
    internships_text = ""
    for i, intern in enumerate(data.get("internships", []), 1):
        internships_text += f"""
    Internship {i}:
    Company : {intern.get('company', '')}
    Role    : {intern.get('role', '')}
    Duration: {intern.get('duration', '')}
    Details : {intern.get('desc', '')}
    """

    # ── Build Prompt ──
    prompt = f"""
    You are a professional resume writer for students.
    Based on the student details below, generate polished resume content.

    ── STUDENT DETAILS ──
    Name         : {data.get('name')}
    Email        : {data.get('email')}
    Phone        : {data.get('phone')}
    Location     : {data.get('location')}
    LinkedIn     : {data.get('linkedin')}
    GitHub       : {data.get('github')}
    Degree       : {data.get('degree')}
    College      : {data.get('college')}
    Grad Year    : {data.get('grad_year')}
    CGPA         : {data.get('percentage')}
    Skills       : {data.get('skills')}
    Achievements : {data.get('achievements')}
    Extra Info   : {data.get('extra')}
    Job Target   : {data.get('job_role')}

    ── PROJECTS ──
    {projects_text if projects_text else "No projects provided"}

    ── INTERNSHIPS ──
    {internships_text if internships_text else "No internships provided"}

    ── WHAT TO GENERATE ──
    Generate these sections professionally:

    1. PROFESSIONAL SUMMARY
       - 3-4 sentences tailored to the job role
       - Highlight their strongest points

    2. SKILLS
       - Clean comma separated list
       - Group if possible (Technical: ... | Soft Skills: ...)

    3. PROJECTS
       - For EACH project write 2-3 bullet points
       - Use action verbs (Developed, Built, Designed, Implemented)
       - Separate each project with [PROJECT_BREAK]

    4. INTERNSHIPS
       - For EACH internship write 2-3 bullet points
       - Use action verbs
       - Separate each internship with [INTERN_BREAK]
       - Write NONE if no internships

    5. ACHIEVEMENTS
       - Clean bullet points
       - Professional language

    6. EXTRA SECTION
       - Polish whatever extra info was provided
       - Write NONE if nothing provided

    ── STRICT RULES ──
    - Do NOT add fake information
    - Do NOT include section headers
    - Use action verbs always
    - Separate sections with: ---SECTION---

    ── OUTPUT FORMAT ──
    [Professional Summary]
    ---SECTION---
    [Skills]
    ---SECTION---
    [Projects - separated by PROJECT_BREAK]
    ---SECTION---
    [Internships - separated by INTERN_BREAK]
    ---SECTION---
    [Achievements]
    ---SECTION---
    [Extra Section]
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role"   : "system",
                    "content": "You are a professional resume writer. Always follow the exact output format given. Never add extra text outside the format."
                },
                {
                    "role"   : "user",
                    "content": prompt
                }
            ],
            max_tokens=2000,
            temperature=0.7,
        )

        raw_text = response.choices[0].message.content
        sections = raw_text.split("---SECTION---")
        sections = [s.strip() for s in sections]

        # ── Parse Projects ──
        projects_raw = sections[2] if len(sections) > 2 else ""
        project_descriptions = []
        for block in projects_raw.split("[PROJECT_BREAK]"):
            block = block.strip()
            if block:
                project_descriptions.append(block)

        # ── Parse Internships ──
        internships_raw = sections[3] if len(sections) > 3 else ""
        internship_descriptions = []
        if internships_raw.strip().upper() != "NONE":
            for block in internships_raw.split("[INTERN_BREAK]"):
                block = block.strip()
                if block:
                    internship_descriptions.append(block)

        result = {
            "summary"                 : sections[0] if len(sections) > 0 else "",
            "skills"                  : sections[1] if len(sections) > 1 else "",
            "project_descriptions"    : project_descriptions,
            "internship_descriptions" : internship_descriptions,
            "achievements"            : sections[4] if len(sections) > 4 else "",
            "extra"                   : sections[5] if len(sections) > 5 else "",
        }

        return result

    except Exception as e:
        print(f"AI Error: {e}")
        return None