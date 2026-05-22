# main.py
from flask import Flask, render_template, request, send_file
from ai_generator import generate_resume_content
from resume_builder import build_resume_pdf
import os

app = Flask(__name__)

OUTPUT_FOLDER = "generated_resumes"
UPLOAD_FOLDER = "uploaded_photos"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():

    # Personal Info
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

    # Photo
    photo_path = None
    if "photo" in request.files:
        photo = request.files["photo"]
        if photo and photo.filename != "":
            ext        = os.path.splitext(photo.filename)[1].lower()
            safe_name  = student_data["name"].replace(" ", "_")
            photo_path = os.path.join(UPLOAD_FOLDER, f"{safe_name}_photo{ext}")
            photo.save(photo_path)
    student_data["photo_path"] = photo_path

    # Projects
    p_titles = request.form.getlist("project_title[]")
    p_descs  = request.form.getlist("project_desc[]")
    projects = []
    for title, desc in zip(p_titles, p_descs):
        title = title.strip()
        if title:
            projects.append({"title": title, "desc": desc.strip()})
    student_data["projects"] = projects

    # Internships
    i_companies = request.form.getlist("internship_company[]")
    i_roles     = request.form.getlist("internship_role[]")
    i_durations = request.form.getlist("internship_duration[]")
    i_descs     = request.form.getlist("internship_desc[]")
    internships = []
    for company, role, duration, desc in zip(
            i_companies, i_roles, i_durations, i_descs):
        company = company.strip()
        if company:
            internships.append({
                "company" : company,
                "role"    : role.strip(),
                "duration": duration.strip(),
                "desc"    : desc.strip()
            })
    student_data["internships"] = internships

    # AI
    print("🤖 Sending to Groq AI...")
    ai_content = generate_resume_content(student_data)
    if not ai_content:
        return "<h2 style='color:red;text-align:center;margin-top:60px'>❌ AI failed. Check API key.</h2>", 500

    # PDF
    print("📄 Building PDF...")
    safe = student_data.get("name","resume").replace(" ","_")
    out  = os.path.join(OUTPUT_FOLDER, f"{safe}_resume.pdf")
    build_resume_pdf(student_data, ai_content, out)

    print("✅ Done!")
    return send_file(
        out,
        as_attachment=True,
        download_name=f"{safe}_resume.pdf",
        mimetype="application/pdf"
    )


if __name__ == "__main__":
    print("🚀 http://127.0.0.1:5000")
    app.run(debug=True)