from fuzzywuzzy import fuzz
from sentence_transformers import SentenceTransformer, util

# Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

def hard_match(resume_skills, jd_skills):
    matched = [s for s in resume_skills if s in jd_skills]
    missing = [s for s in jd_skills if s not in resume_skills]
    return matched, missing

def semantic_match(resume_text, jd_text):
    # Compute cosine similarity (0-100)
    embeddings = model.encode([resume_text, jd_text])
    sim = util.cos_sim(embeddings[0], embeddings[1]).item()
    return round(sim * 100, 2)

def calculate_score(matched_skills, total_skills, semantic_score, hard_weight=0.6, soft_weight=0.4):
    hard_score = (len(matched_skills) / total_skills) * 100 if total_skills else 0
    return round(hard_score * hard_weight + semantic_score * soft_weight, 2)

def fit_verdict(score):
    if score >= 80:
        return "High"
    elif score >= 50:
        return "Medium"
    else:
        return "Low"
