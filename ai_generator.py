# ai_generator.py
from groq import Groq
import os
import re
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def clean(text):
    text = re.sub(r'\[.*?\]', '', text)
    text = text.replace("**", "").replace("##", "")
    lines = [
        l.strip() for l in text.strip().split('\n')
        if l.strip() and l.strip().lower() not in [
            'professional summary', 'skills', 'projects',
            'internships', 'achievements', 'extra',
            'additional information', 'none', 'n/a',
            'skip', 'project description', 'description'
        ]
    ]
    return '\n'.join(lines) 


def ai_call(system_msg, user_msg):
    """Single reusable AI call"""
    resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user",   "content": user_msg}
        ],
        max_tokens=300,
        temperature=0.4,
    )
    return clean(resp.choices[0].message.content)


def generate_resume_content(data):
    try:
        job_roles = data.get('job_roles', '')
        name      = data.get('name', '')

        # ── 1. SUMMARY ──
        summary = ai_call(
            "You are a resume writer. Write only the content, no labels or headings.",
            f"""Write a 3 sentence professional summary for:
Name    : {name}
Degree  : {data.get('degree')} from {data.get('college')}
Skills  : {data.get('skills')}
Job Target: {job_roles}
Rules: No brackets, no bold, no labels. Start directly with the summary."""
        )

        # ── 2. SKILLS ──
        skills = ai_call(
            "You are a resume writer. Output only a clean comma separated list.",
            f"""Format these skills as a clean comma separated list:
{data.get('skills')}
Rules: No brackets, no bold, no labels, just the skill list."""
        )

        # ── 3. PROJECTS — one by one ──
        project_descriptions = []
        for p in data.get("projects", []):
            desc = ai_call(
                "You are a resume writer. Write exactly 2 bullet points only.",
                f"""Write exactly 2 bullet points for this project only:
Project Title: {p.get('title', '')}
Project Info : {p.get('desc', '')}

Rules:
- Write ONLY about this specific project
- Exactly 2 bullets, each starting with an action verb
- Each bullet maximum 1 line
- No brackets, no bold, no project title in bullets
- Start each bullet with •"""
            )
            project_descriptions.append(desc)

        # ── 4. INTERNSHIPS — one by one ──
        internship_descriptions = []
        for n in data.get("internships", []):
            if not n.get("company"):
                continue
            desc = ai_call(
                "You are a resume writer. Write exactly 2 bullet points only.",
                f"""Write exactly 2 bullet points for this internship only:
Company : {n.get('company', '')}
Role    : {n.get('role', '')}
Duration: {n.get('duration', '')}
Details : {n.get('desc', '')}

Rules:
- Write ONLY about this internship
- Exactly 2 bullets starting with action verbs
- Each bullet maximum 1 line
- No brackets, no bold
- Start each bullet with •"""
            )
            internship_descriptions.append(desc)

        # ── 5. ACHIEVEMENTS ──
        achievements = ""
        if data.get("achievements"):
            achievements = ai_call(
                "You are a resume writer. Write clean bullet points only.",
                f"""Format these achievements as professional bullet points:
{data.get('achievements')}
Rules: No brackets, no bold, start each bullet with •"""
            )

        # ── 6. EXTRA ──
        extra = ""
        if data.get("extra"):
            extra = ai_call(
                "You are a resume writer. Write clean bullet points only.",
                f"""Format this additional information professionally:
{data.get('extra')}
Rules: No brackets, no bold, start each bullet with •"""
            )

        return {
            "summary"                : summary,
            "skills"                 : skills,
            "project_descriptions"   : project_descriptions,
            "internship_descriptions": internship_descriptions,
            "achievements"           : achievements,
            "extra"                  : extra,
        }

    except Exception as e:
        print(f"AI Error: {e}")
        return None