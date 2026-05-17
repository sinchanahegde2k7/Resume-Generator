# main.py
# This is the heart of the app — connects everything together

from flask import Flask, render_template, request, send_file
from ai_generator import generate_resume_content
from resume_builder import build_resume_pdf
import os

app = Flask(__name__)

# Folder to save generated resumes
OUTPUT_FOLDER = "generated_resumes"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# ── HOME PAGE ──
@app.route("/")
def home():
    return render_template("index.html")


# ── GENERATE RESUME ──
@app.route("/generate", methods=["POST"])
def generate():

    # Step 1: Collect form data
    student_data = {
        "name"        : request.form.get("name", "").strip(),
        "email"       : request.form.get("email", "").strip(),
        "phone"       : request.form.get("phone", "").strip(),
        "location"    : request.form.get("location", "").strip(),
        "linkedin"    : request.form.get("linkedin", "").strip(),
        "degree"      : request.form.get("degree", "").strip(),
        "college"     : request.form.get("college", "").strip(),
        "grad_year"   : request.form.get("grad_year", "").strip(),
        "percentage"  : request.form.get("percentage", "").strip(),
        "skills"      : request.form.get("skills", "").strip(),
        "project1"    : request.form.get("project1", "").strip(),
        "project2"    : request.form.get("project2", "").strip(),
        "experience"  : request.form.get("experience", "").strip(),
        "achievements": request.form.get("achievements", "").strip(),
        "job_role"    : request.form.get("job_role", "").strip(),
    }

    # Step 2: Send to Gemini AI
    print("🤖 Sending data to Gemini AI...")
    ai_content = generate_resume_content(student_data)

    if not ai_content:
        return """
            <h2 style='color:red; font-family:sans-serif; text-align:center; margin-top:50px;'>
            ❌ AI generation failed. Please check your API key and try again.
            </h2>
        """, 500

    # Step 3: Build the PDF
    print("📄 Building PDF resume...")
    student_name = student_data.get("name", "resume").replace(" ", "_")
    output_path  = os.path.join(OUTPUT_FOLDER, f"{student_name}_resume.pdf")
    build_resume_pdf(student_data, ai_content, output_path)

    # Step 4: Send PDF to browser for download
    print("✅ Resume ready! Sending to browser...")
    return send_file(
        output_path,
        as_attachment=True,
        download_name=f"{student_name}_resume.pdf",
        mimetype="application/pdf"
    )


# ── RUN THE APP ──
if __name__ == "__main__":
    print("🚀 Starting AI Resume Generator...")
    print("🌐 Open your browser and go to: http://127.0.0.1:5000")
    print("⏹️  Press CTRL+C to stop the server\n")
    app.run(debug=True) 