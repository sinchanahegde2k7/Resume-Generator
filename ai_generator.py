# ai_generator.py
# Uses Groq API (Free & Fast!)

from groq import Groq
import os
from dotenv import load_dotenv

# Load API key
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_resume_content(data):
    """
    Takes student data dictionary
    Returns AI-generated resume content as a dictionary
    """

    prompt = f"""
    You are a professional resume writer for students.
    Based on the student details below, generate polished resume content.

    Student Details:
    - Name            : {data.get('name')}
    - Email           : {data.get('email')}
    - Phone           : {data.get('phone')}
    - Location        : {data.get('location')}
    - LinkedIn        : {data.get('linkedin')}
    - Degree          : {data.get('degree')}
    - College         : {data.get('college')}
    - Graduation Year : {data.get('grad_year')}
    - Percentage/CGPA : {data.get('percentage')}
    - Skills          : {data.get('skills')}
    - Project 1       : {data.get('project1')}
    - Project 2       : {data.get('project2')}
    - Experience      : {data.get('experience')}
    - Achievements    : {data.get('achievements')}
    - Job Role Target : {data.get('job_role')}

    Generate the following sections professionally:

    1. PROFESSIONAL SUMMARY (3-4 sentences, tailored to the job role)
    2. SKILLS (format as clean comma-separated list, grouped if possible)
    3. PROJECT 1 DESCRIPTION (2-3 bullet points, action verbs, impressive)
    4. PROJECT 2 DESCRIPTION (2-3 bullet points, skip if no project 2)
    5. EXPERIENCE DESCRIPTION (2-3 bullet points, skip if no experience)
    6. ACHIEVEMENTS (clean bullet points)

    STRICT RULES:
    - Use action verbs (Developed, Built, Designed, Implemented, etc.)
    - Keep it student-friendly but professional
    - Do NOT add fake information
    - Do NOT include section headers in your response
    - Separate each section with this exact divider: ---SECTION---

    Output format (strictly follow this):
    [Professional Summary]
    ---SECTION---
    [Skills]
    ---SECTION---
    [Project 1 Description]
    ---SECTION---
    [Project 2 Description]
    ---SECTION---
    [Experience Description]
    ---SECTION---
    [Achievements]
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional resume writer. Always follow the exact output format given."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=1500,
            temperature=0.7,
        )

        raw_text = response.choices[0].message.content

        # Split by our divider
        sections = raw_text.split("---SECTION---")

        # Clean each section
        sections = [s.strip() for s in sections]

        # Map to dictionary
        result = {
            "summary"      : sections[0] if len(sections) > 0 else "",
            "skills"       : sections[1] if len(sections) > 1 else "",
            "project1_desc": sections[2] if len(sections) > 2 else "",
            "project2_desc": sections[3] if len(sections) > 3 else "",
            "experience"   : sections[4] if len(sections) > 4 else "",
            "achievements" : sections[5] if len(sections) > 5 else "",
        }

        return result

    except Exception as e:
        print(f"AI Error: {e}")
        return None 