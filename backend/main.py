from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import pdfplumber
import io
import os
import json
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Resume Enhancer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
client = genai.GenerativeModel("gemini-2.5-flash")


class ResumeTextRequest(BaseModel):
    resume_text: str
    job_role: str = ""
    experience_level: str = ""

SYSTEM_PROMPT = """You are an expert resume coach and ATS optimization specialist with 15+ years of experience in HR and recruiting across top tech companies. Your goal is to provide thorough, actionable resume improvement suggestions.

Analyze the provided resume and return a JSON response with the following structure:
{
  "ats_score": <number 0-100>,
  "ats_score_explanation": "<brief explanation of the score>",
  "overall_summary": "<2-3 sentence overall assessment>",
  "sections": [
    {
      "name": "<section name like Summary, Experience, Skills, Education, Formatting, Language>",
      "status": "<'good' | 'needs_improvement' | 'critical'>",
      "strengths": ["<strength 1>", "<strength 2>"],
      "improvements": ["<improvement 1>", "<improvement 2>"],
      "rewritten_example": "<optional: a rewritten version of a key bullet/section to demonstrate improvement>"
    }
  ],
  "quick_wins": ["<top 3-5 highest impact quick changes the person can make>"],
  "keywords_missing": ["<important industry keywords that seem to be missing>"],
  "ats_improvements": ["<specific action to raise the ATS score, e.g. add more keywords from job description>", "<format suggestion>", "<section restructuring tip>"]
}

Be specific and actionable. Reference actual content from the resume. Avoid generic advice. Focus on impact, quantification, ATS compatibility, and strong action verbs."""


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    text = ""
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


def analyze_resume(resume_text: str, job_role: str = "", experience_level: str = "") -> dict:
    if not resume_text or len(resume_text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Resume text is too short. Please provide more content.")

    role_context = f"The candidate is targeting a **{job_role}** role." if job_role else "The candidate has not specified a target role. Infer it from the resume content."

    level_context = ""
    if experience_level:
        level_map = {
            "student": "They are a student with no professional experience. Evaluate accordingly — focus on projects, academics, internships, and potential. Do NOT penalize for lack of work experience. ATS score should reflect expectations for this level.",
            "fresher": "They are a fresher with 0–1 years of experience. Focus on internships, projects, and foundational skills. Set ATS score expectations for entry-level roles.",
            "junior": "They have 1–3 years of experience. Evaluate growth trajectory, skill depth, and early impact. ATS score should reflect junior-level expectations.",
            "mid": "They have 3–6 years of experience. Evaluate leadership hints, ownership, measurable impact, and technical depth. ATS score should reflect mid-level expectations.",
            "senior": "They have 6–10 years of experience. Evaluate strategic thinking, system design, mentorship, and business impact. ATS score should reflect senior-level expectations.",
            "lead": "They are a lead or principal engineer with 10+ years. Evaluate organizational impact, architecture decisions, cross-team influence, and thought leadership. ATS score should reflect lead/principal-level expectations.",
        }
        level_context = level_map.get(experience_level, "")

    ats_instruction = ""
    if job_role and experience_level:
        ats_instruction = f"\n\nIMPORTANT: The ATS score MUST be calculated specifically for a **{job_role}** role at the **{experience_level}** level. A resume strong for a senior engineer would score poorly for a fresher, and vice versa. Weight the score based on how well this resume would pass ATS filters for this exact role and level."
    elif job_role:
        ats_instruction = f"\n\nIMPORTANT: The ATS score MUST reflect how well this resume would pass ATS filters specifically for a **{job_role}** role — relevant keywords, skills, and formatting for that domain."
    elif experience_level:
        ats_instruction = f"\n\nIMPORTANT: The ATS score MUST be benchmarked against **{experience_level}**-level expectations. Do not apply senior-level standards to a fresher or student."

    dynamic_prompt = SYSTEM_PROMPT + f"\n\n{role_context}" + (
        f"\n\n{level_context}" if level_context else "") + ats_instruction + "\n\nEvaluate and tailor all feedback specifically for this role and experience level — relevant skills, keywords, and industry expectations."
    response = client.generate_content(
        contents=f"{dynamic_prompt}\n\nHere is the resume:\n\n{resume_text}"
    )
    response_text = response.text

    # Parse JSON from response
    try:
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()

        return json.loads(response_text)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to parse AI response. Please try again.")


@app.get("/")
def root():
    return {"message": "Resume Enhancer API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze/text")
def analyze_text(request: ResumeTextRequest):
    result = analyze_resume(request.resume_text, request.job_role, request.experience_level)
    return result


@app.post("/analyze/pdf")
async def analyze_pdf(file: UploadFile = File(...), job_role: str = Form(""), experience_level: str = Form("")):

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    contents = await file.read()

    if len(contents) > 5 * 1024 * 1024:  # 5MB limit
        raise HTTPException(status_code=400, detail="File size exceeds 5MB limit.")

    try:
        resume_text = extract_text_from_pdf(contents)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract text from PDF: {str(e)}")

    if not resume_text:
        raise HTTPException(status_code=400, detail="Could not extract text from PDF. The file may be scanned or image-based.")

    result = analyze_resume(resume_text, job_role, experience_level)
    result["extracted_text"] = resume_text
    return result
