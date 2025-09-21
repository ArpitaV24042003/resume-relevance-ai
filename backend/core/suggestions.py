# core/suggestions.py
import os
import openai
import gc

# Use environment variable, do NOT hardcode your key
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_suggestions(resume_text, jd_text, missing_skills):
    if not openai.api_key:
        return ["OpenAI API key not set. Suggestions not available."]
    
    prompt = f"""
You are a career mentor. 
The student resume is: {resume_text}
The Job Description is: {jd_text}
Missing skills are: {', '.join(missing_skills)}.

Provide 3-5 concise actionable suggestions for improvement.
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role":"user","content":prompt}],
            temperature=0.6,
            max_tokens=150
        )
        suggestions = response['choices'][0]['message']['content'].split('\n')
        return [s.strip('-• ').strip() for s in suggestions if s.strip()]
    finally:
        gc.collect()
