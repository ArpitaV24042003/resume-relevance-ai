import pdfplumber
import docx
import re

def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return normalize_text(text)

def extract_text_from_docx(file):
    doc = docx.Document(file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return normalize_text(text)

def normalize_text(text):
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n+', '\n', text)
    return text

def extract_skills(text, skill_list=None):
    if skill_list is None:
        skill_list = ["python", "sql", "java", "c++", "machine learning", "deep learning", "aws"]
    found = [skill for skill in skill_list if skill in text]
    return found
