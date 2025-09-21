from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uvicorn
import os

from backend.core.parser import extract_skills, extract_text_from_pdf, extract_text_from_docx
from backend.core.scoring import hard_match, semantic_match, calculate_score, fit_verdict
from backend.core.suggestions import generate_suggestions
from backend.db import init_db, save_evaluation, get_evaluations

app = FastAPI()

init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_text_from_file(file: UploadFile):
    content_type = file.content_type
    file_content = file.file
    if "pdf" in content_type:
        return extract_text_from_pdf(file_content)
    elif "vnd.openxmlformats-officedocument.wordprocessingml.document" in content_type:
        return extract_text_from_docx(file_content)
    else:
        raise ValueError(f"Unsupported file type: {content_type}")

@app.get("/")
def root():
    return {"message": "Resume Relevance API is running ✅"}

@app.post("/evaluate_batch")
async def evaluate_batch(
    resumes: List[UploadFile] = File(...),
    jd: UploadFile = File(...)
):
    try:
        jd_text = extract_text_from_file(jd)
        jd_skills = extract_skills(jd_text)
        
        results = []

        for resume in resumes:
            resume_text = extract_text_from_file(resume)
            resume_skills = extract_skills(resume_text)

            matched_skills, missing_skills = hard_match(resume_skills, jd_skills)
            semantic_score = semantic_match(resume_text, jd_text)
            score = calculate_score(matched_skills, len(jd_skills), semantic_score)
            verdict = fit_verdict(score)

            suggestions = generate_suggestions(
                resume_text,
                jd_text,
                missing_skills,
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
            
            evaluation_data = {
                "resume_filename": resume.filename,
                "score": score,
                "fit_verdict": verdict,
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
                "suggestions": suggestions,
            }

            save_evaluation(
                resume_filename=resume.filename,
                jd_filename=jd.filename,
                hard_score=len(matched_skills),
                semantic_score=semantic_score,
                weighted_score=score,
                verdict=verdict,
                matched_skills=",".join(matched_skills),
                missing_skills=",".join(missing_skills),
                suggestions=";".join(suggestions)
            )

            results.append(evaluation_data)

        return {"jd_filename": jd.filename, "jd_skills": jd_skills, "results": results}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}, 500

@app.get("/evaluations")
def all_evaluations():
    try:
        evals = get_evaluations()
        results = []
        for e in evals:
            results.append({
                "id": e[0],
                "resume_filename": e[1],
                "jd_filename": e[2],
                "hard_score": e[3],
                "semantic_score": e[4],
                "weighted_score": e[5],
                "verdict": e[6],
                "matched_skills": e[7].split(",") if e[7] else [],
                "missing_skills": e[8].split(",") if e[8] else [],
                "suggestions": e[9].split(";") if e[9] else []
            })
        return results
    except Exception as e:
        return {"error": f"Could not retrieve evaluations: {str(e)}"}, 500

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

