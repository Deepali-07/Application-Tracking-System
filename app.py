from flask import Flask, render_template, request
from dotenv import load_dotenv
import os
import openai
import PyPDF2
import docx

# Load environment variables
load_dotenv()
API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize Flask app
app = Flask(__name__)

def extract_text_from_file(file):
    """Extract text from uploaded file."""
    if file.filename.endswith('.pdf'):
        pdf_reader = PyPDF2.PdfReader(file)
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    elif file.filename.endswith('.docx'):
        doc = docx.Document(file)
        return '\n'.join([p.text for p in doc.paragraphs])
    else:
        raise ValueError("Unsupported file format. Please upload a .pdf or .docx file.")

def get_ats_score_and_feedback(resume_text, api_key):
    """Call OpenAI to calculate ATS score and generate feedback."""
    openai.api_key = api_key

    prompt = f"""
    You are an ATS scoring assistant. Critically evaluate the following resume for a professional role. Provide the following:
    1. Extracted Skills: List all skills found in the resume as a comma-separated list.
    2. Missing Skills: List all relevant skills missing from the resume as a comma-separated list.
    3. ATS Score: Provide a numeric score (0-100) reflecting the resume's quality and relevance.
    4. Feedback: Provide actionable suggestions for improvement under these categories:
       - Skills
       - Sections
       - Formatting

    Use this format:
    - Extracted Skills: skill1, skill2, skill3, etc.
    - Missing Skills: skill1, skill2, skill3, etc.
    - ATS Score: XX.XX
    - Feedback:
       - Skills: <feedback>
       - Sections: <feedback>
       - Formatting: <feedback>
    Resume content:
    {resume_text}
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        content = response['choices'][0]['message']['content']

        ats_score = None
        extracted_skills = []
        missing_skills = []
        feedback_sections = {"Skills": "", "Sections": "", "Formatting": ""}

        for line in content.splitlines():
            if "ATS Score:" in line:
                ats_score = round(float(line.split(":")[1].strip()), 2)
            elif "Extracted Skills:" in line:
                extracted_skills = [skill.strip() for skill in line.split(":")[1].split(",")]
            elif "Missing Skills:" in line:
                missing_skills = [skill.strip() for skill in line.split(":")[1].split(",")]
            elif "- Skills:" in line:
                feedback_sections["Skills"] = line.split(":", 1)[1].strip()
            elif "- Sections:" in line:
                feedback_sections["Sections"] = line.split(":", 1)[1].strip()
            elif "- Formatting:" in line:
                feedback_sections["Formatting"] = line.split(":", 1)[1].strip()

        # Calibration: Additional metrics
        extracted_count = len(extracted_skills)
        missing_count = len(missing_skills)
        skill_match_rate = extracted_count / (extracted_count + missing_count) if extracted_count + missing_count > 0 else 0

        # Formatting Quality
        formatting_quality = 1 if feedback_sections["Formatting"].lower() == "good" else 0

        # Critical Sections Presence
        critical_sections = ["Work Experience", "Education", "Skills", "Certifications"]
        missing_sections_count = sum(1 for section in critical_sections if section.lower() not in resume_text.lower())
        section_completeness = 1 - (missing_sections_count / len(critical_sections))

        # Penalty for Missing Sections
        section_penalty = missing_sections_count * 5  # Heavier penalty for each missing section

        # Weighted final score calculation
        if ats_score is not None:
            final_score = (
                (ats_score * 0.5) +  # 50% from OpenAI ATS Score
                (skill_match_rate * 100 * 0.2) +  # 20% from skill match rate
                (section_completeness * 100 * 0.2) +  # 20% from section completeness
                (formatting_quality * 100 * 0.1)  # 10% from formatting quality
            )
            final_score -= section_penalty  # Subtract penalty for missing sections
            ats_score = max(0, min(100, round(final_score, 2)))  # Ensure score is between 0-100

        return ats_score, extracted_skills, missing_skills, feedback_sections
    except Exception as e:
        return None, [], [], {"Error": str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'resume' not in request.files:
            return render_template('result.html', score=None, error="No file part")
        file = request.files['resume']
        if file.filename == '':
            return render_template('result.html', score=None, error="No selected file")
        try:
            resume_text = extract_text_from_file(file)
            ats_score, extracted_skills, missing_skills, feedback_sections = get_ats_score_and_feedback(resume_text, API_KEY)
            return render_template(
                'result.html',
                score=ats_score if ats_score is not None else 0,  # Default to 0 if None
                extracted_skills=extracted_skills,
                missing_skills=missing_skills,
                feedback_sections=feedback_sections,
                error=None
            )
        except Exception as e:
            return render_template('result.html', score=None, error=str(e))
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
