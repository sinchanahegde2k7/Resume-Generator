# ai_generator.py
from groq import Groq
import os
import re
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def clean(text):
    """Remove all bracket labels and markdown bold"""
    text = re.sub(r'\[.*?\]', '', text)
    text = text.replace("**", "")
    lines = [
        l.strip() for l in text.strip().split('\n')
        if l.strip() and l.strip().lower() not in [
            'professional summary','skills','projects',
            'internships','achievements','extra',
            'additional information','none','n/a'
        ]
    ]
    return '\n'.join(lines)


def generate_resume_content(data):

    # Format projects
    proj_text = ""
    for i, p in enumerate(data.get("projects", []), 1):
        proj_text += f"\n  Project {i}: {p.get('title','')}\n  About: {p.get('desc','')}\n"

    # Format internships
    intern_text = ""
    for i, n in enumerate(data.get("internships", []), 1):
        intern_text += f"""
  Internship {i}:
  Company : {n.get('company','')}
  Role    : {n.get('role','')}
  Duration: {n.get('duration','')}
  Details : {n.get('desc','')}
"""

    # PG text
    pg_text = ""
    if data.get("pg_degree"):
        pg_text = f"Post Grad: {data['pg_degree']} from {data.get('pg_college','')} ({data.get('pg_year','')}), CGPA: {data.get('pg_percentage','')}"

    prompt = f"""
You are an expert professional resume writer for students in India.
Write polished, impressive resume content based on the student details below.

STUDENT DETAILS:
Name        : {data.get('name')}
Location    : {data.get('location')}
Degree      : {data.get('degree')} from {data.get('college')} ({data.get('grad_year')}), CGPA: {data.get('percentage')}
{pg_text}
Skills      : {data.get('skills')}
Achievements: {data.get('achievements')}
Extra Info  : {data.get('extra')}
Job Targets : {data.get('job_roles')}

PROJECTS:
{proj_text if proj_text else "None provided"}

INTERNSHIPS:
{intern_text if intern_text else "None provided"}

INSTRUCTIONS:
Write exactly 6 sections separated by ---SECTION--- divider.
Each section must contain ONLY the content, NO labels, NO headings, NO brackets.

Section order:
1. Professional Summary — 3 sentences, tailored to job targets
2. Skills — comma separated, clean list
3. Project descriptions — for each project write 2-3 bullet points starting with action verbs. Separate projects with [PROJECT_BREAK]
4. Internship descriptions — for each internship 2-3 bullet points. Write SKIP if none. Separate with [INTERN_BREAK]
5. Achievements — bullet points, professional
6. Extra info — polish it. Write SKIP if none provided.

RULES:
- NO bracket labels like [Professional Summary] anywhere
- NO section headings inside the content
- NO markdown bold like **text**
- Start writing content directly
- Use strong action verbs: Developed, Built, Designed, Implemented, Managed

OUTPUT FORMAT — follow exactly:
<summary text here>
---SECTION---
<skills text here>
---SECTION---
<project descriptions here>
---SECTION---
<internship descriptions here>
---SECTION---
<achievements here>
---SECTION---
<extra info here>
"""

    try:
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional resume writer. Output ONLY the 6 sections separated by ---SECTION---. No labels, no brackets, no headings inside content."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=2000,
            temperature=0.6,
        )

        raw      = resp.choices[0].message.content
        sections = [clean(s) for s in raw.split("---SECTION---")]

        # Parse project descriptions
        proj_raw  = sections[2] if len(sections) > 2 else ""
        proj_desc = [
            b.strip() for b in proj_raw.split("[PROJECT_BREAK]")
            if b.strip()
        ]

        # Parse internship descriptions
        intern_raw  = sections[3] if len(sections) > 3 else ""
        intern_desc = []
        if intern_raw.strip().upper() not in ["SKIP", "NONE", ""]:
            intern_desc = [
                b.strip() for b in intern_raw.split("[INTERN_BREAK]")
                if b.strip()
            ]

        extra = sections[5] if len(sections) > 5 else ""
        if extra.strip().upper() in ["SKIP", "NONE"]:
            extra = ""

        return {
            "summary"                : sections[0] if len(sections) > 0 else "",
            "skills"                 : sections[1] if len(sections) > 1 else "",
            "project_descriptions"   : proj_desc,
            "internship_descriptions": intern_desc,
            "achievements"           : sections[4] if len(sections) > 4 else "",
            "extra"                  : extra,
        }

    except Exception as e:
        print(f"AI Error: {e}")
        return None