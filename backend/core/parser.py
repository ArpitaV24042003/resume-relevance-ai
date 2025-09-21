# core/parser.py
import pdfplumber
from docx import Document
import re
import io

def normalize_text(text):
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n+', '\n', text)
    return text

def extract_text_from_pdf(file):
    file.seek(0)
    text = ""
    with pdfplumber.open(io.BytesIO(file.read())) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return normalize_text(text)

def extract_text_from_docx(file):
    file.seek(0)
    doc = Document(io.BytesIO(file.read()))
    text = "\n".join([para.text for para in doc.paragraphs])
    return normalize_text(text)

def extract_skills(text, skill_list=None):
    if skill_list is None:
        skill_list = ["python", "sql", "java", "c++", "machine learning", "deep learning", "aws"]
    found = [skill for skill in skill_list if skill in text]
    return found
