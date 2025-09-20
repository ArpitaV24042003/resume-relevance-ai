# Requires OpenAI key: export OPENAI_API_KEY="your_key"
import openai

openai.api_key = "YOUR_OPENAI_API_KEY"

def generate_suggestions(resume_text, jd_text, missing_skills):
    """
    Generate personalized improvement suggestions using GPT.
    """
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
        # Clean empty lines
        return [s.strip('-• ').strip() for s in suggestions if s.strip()]
    except Exception:
        return [f"Consider improving: {s}" for s in missing_skills]
