from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import gc

from core.parser import extract_skills, extract_text_from_pdf, extract_text_from_docx
from core.scoring import hard_match, semantic_match, calculate_score, fit_verdict
from core.suggestions import generate_suggestions

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

def extract_resume_text(file: UploadFile):
    if file.filename.endswith(".pdf"):
        return extract_text_from_pdf(file.file)
    else:
        return extract_text_from_docx(file.file)

@app.get("/")
def root():
    return {"message": "Resume Relevance API is running ✅"}

@app.post("/evaluate_batch")
async def evaluate_batch(
    resumes: List[UploadFile] = File(...),
    jd: UploadFile = File(...)
):
    jd_text = extract_resume_text(jd)
    jd_skills = extract_skills(jd_text)

    results = []

    for resume in resumes:
        resume_text = extract_resume_text(resume)
        resume_skills = extract_skills(resume_text)

        matched_skills, missing_skills = hard_match(resume_skills, jd_skills)
        semantic_score = semantic_match(resume_text, jd_text)
        score = calculate_score(matched_skills, len(jd_skills), semantic_score)
        verdict = fit_verdict(score)
        suggestions = generate_suggestions(resume_text, jd_text, missing_skills)

        results.append({
            "resume_filename": resume.filename,
            "score": score,
            "fit_verdict": verdict,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "suggestions": suggestions
        })

        # Free memory after processing each resume
        del resume_text, resume_skills, matched_skills, missing_skills, suggestions
        gc.collect()

    del jd_text, jd_skills
    gc.collect()

    return {"jd_filename": jd.filename, "jd_skills": jd_skills, "results": results}
