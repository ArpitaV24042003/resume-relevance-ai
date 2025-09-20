from fastapi import FastAPI, UploadFile
import uvicorn
from PyPDF2 import PdfReader
import docx
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# ✅ Root endpoint (add here)
@app.get("/")
def root():
    return {"message": "Resume Relevance API is running ✅"}

# --- Helper functions ---
def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def extract_text_from_docx(file):
    doc = docx.Document(file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

# --- LLM setup ---
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

prompt = PromptTemplate(
    input_variables=["resume", "jd"],
    template="""
    You are an expert ATS system.

    Compare the following RESUME with the JOB DESCRIPTION and return output as strict JSON with this structure:

    {{
      "score": <int 0-100>,
      "matched_skills": [list of skills found in both],
      "missing_skills": [list of skills missing in resume],
      "suggestions": [3 short suggestions to improve resume relevance]
    }}

    RESUME: {resume}
    JOB DESCRIPTION: {jd}
    """
)

@app.post("/evaluate")
async def evaluate(resume: UploadFile, jd: UploadFile):
    # Extract resume text
    if resume.filename.endswith(".pdf"):
        resume_text = extract_text_from_pdf(resume.file)
    else:
        resume_text = extract_text_from_docx(resume.file)

    # Extract JD text
    if jd.filename.endswith(".pdf"):
        jd_text = extract_text_from_pdf(jd.file)
    else:
        jd_text = extract_text_from_docx(jd.file)

    # Run chain
    chain = prompt | llm
    result = chain.invoke({"resume": resume_text, "jd": jd_text})

    import json
    try:
        parsed = json.loads(result.content)
    except Exception:
        parsed = {"error": "Failed to parse LLM output", "raw": result.content}

    return parsed


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
