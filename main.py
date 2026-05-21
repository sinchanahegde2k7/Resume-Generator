# main.py
from flask import Flask, render_template, request, send_file
from ai_generator import generate_resume_content
from resume_builder import build_resume_pdf
import os

app = Flask(__name__)

OUTPUT_FOLDER = "generated_resumes"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# ── HOME PAGE ──
@app.route("/")
def home():
    return render_template("index.html")


# ── GENERATE RESUME ──
@app.route("/generate", methods=["POST"])
def generate():

    # ── Personal Info ──
    student_data = {
        "name"         : request.form.get("name", "").strip(),
        "email"        : request.form.get("email", "").strip(),
        "phone"        : request.form.get("phone", "").strip(),
        "location"     : request.form.get("location", "").strip(),
        "linkedin"     : request.form.get("linkedin", "").strip(),
        "github"       : request.form.get("github", "").strip(),
        "degree"       : request.form.get("degree", "").strip(),
        "college"      : request.form.get("college", "").strip(),
        "grad_year"    : request.form.get("grad_year", "").strip(),
        "percentage"   : request.form.get("percentage", "").strip(),
        "pg_degree"    : request.form.get("pg_degree", "").strip(),
        "pg_college"   : request.form.get("pg_college", "").strip(),
        "pg_year"      : request.form.get("pg_year", "").strip(),
        "pg_percentage": request.form.get("pg_percentage", "").strip(),
        "skills"       : request.form.get("skills", "").strip(),
        "achievements" : request.form.get("achievements", "").strip(),
        "extra"        : request.form.get("extra", "").strip(),
        "job_roles"    : request.form.get("job_roles", "").strip(),
    }

    # ── Dynamic Projects ──
    project_titles = request.form.getlist("project_title[]")
    project_descs  = request.form.getlist("project_desc[]")
    projects = []
    for title, desc in zip(project_titles, project_descs):
        title = title.strip()
        desc  = desc.strip()
        if title:
            projects.append({
                "title": title,
                "desc" : desc
            })
    student_data["projects"] = projects

    # ── Dynamic Internships ──
    internship_companies = request.form.getlist("internship_company[]")
    internship_roles     = request.form.getlist("internship_role[]")
    internship_durations = request.form.getlist("internship_duration[]")
    internship_descs     = request.form.getlist("internship_desc[]")
    internships = []
    for company, role, duration, desc in zip(
        internship_companies,
        internship_roles,
        internship_durations,
        internship_descs
    ):
        company = company.strip()
        if company:
            internships.append({
                "company" : company,
                "role"    : role.strip(),
                "duration": duration.strip(),
                "desc"    : desc.strip()
            })
    student_data["internships"] = internships

    # ── Send to AI ──
    print("🤖 Sending data to Groq AI...")
    ai_content = generate_resume_content(student_data)

    if not ai_content:
        return """
            <h2 style='color:red; font-family:sans-serif;
            text-align:center; margin-top:50px;'>
            ❌ AI generation failed. Please check your API key.
            </h2>
        """, 500

    # ── Build PDF ──
    print("📄 Building PDF resume...")
    student_name = student_data.get("name", "resume").replace(" ", "_")
    output_path  = os.path.join(
        OUTPUT_FOLDER, f"{student_name}_resume.pdf"
    )
    build_resume_pdf(student_data, ai_content, output_path)

    # ── Send to Browser ──
    print("✅ Resume ready!")
    return send_file(
        output_path,
        as_attachment=True,
        download_name=f"{student_name}_resume.pdf",
        mimetype="application/pdf"
    )


# ── RUN ──
if __name__ == "__main__":
    print("🚀 Starting AI Resume Generator...")
    print("🌐 Open: http://127.0.0.1:5000")
    print("⏹️  Press CTRL+C to stop\n")
    app.run(debug=True) 