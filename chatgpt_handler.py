import openai

def get_ats_score_and_feedback(resume_text, api_key):
    """Call ChatGPT to calculate ATS score and generate feedback."""
    openai.api_key = api_key

    prompt = f"""
You are a highly advanced ATS (Applicant Tracking System) scoring assistant. Your task is to analyze resumes for job readiness and provide structured feedback.

Tasks:
1. **Skills Analysis**:
   - Extract all skills mentioned in the resume and list them under the header "- Extracted Skills:".
   - Identify critical skills that are commonly required but missing, and list them under "- Missing Skills:".
   - Ensure skill extraction is accurate and comprehensive.

2. **ATS Score**:
   - Assign a score out of 100 under the header "- ATS Score:".
   - The score should reflect the strength, relevance, and completeness of the resume.

3. **Improvement Suggestions**:
   - Provide actionable recommendations under "- Feedback:".
   - Focus on:
     - Enhancing the resume format (e.g., layout, sections).
     - Adding or elaborating on missing critical details (e.g., projects, metrics, or achievements).
     - Improving the language and style for better clarity and impact.

**Expected Output Format**:
- Extracted Skills: [List of skills]
- Missing Skills: [List of skills]
- ATS Score: [Score out of 100]
- Feedback: [Detailed suggestions]

Here is the resume content:
{resume_text}
"""
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an ATS scoring assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        # Extract the response content
        content = response['choices'][0]['message']['content']

        # Parse the response
        ats_score = None
        feedback = None
        ats_score_line = [line for line in content.splitlines() if "ATS Score:" in line]
        if ats_score_line:
            ats_score = ats_score_line[0].split(":")[1].strip()

        feedback = content.strip()

        return ats_score, feedback

    except Exception as e:
        print(f"Error with OpenAI API call or response parsing: {e}")
        return None, f"Error: {e}"
