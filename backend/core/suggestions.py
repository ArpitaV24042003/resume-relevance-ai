import os
from openai import OpenAI

def generate_suggestions(resume_text, jd_text, missing_skills, openai_api_key):
    # Check if the key is provided and valid
    if not openai_api_key or not openai_api_key.startswith("sk-"):
        return ["OpenAI API key is not set or invalid. Suggestions are unavailable."]

    try:
        # Modern way to initialize the client
        client = OpenAI(api_key=openai_api_key)

        prompt = f"""
        You are an expert career coach providing feedback on a resume compared to a job description.
        The candidate's resume text is:
        --- RESUME ---
        {resume_text[:2000]}
        --- END RESUME ---

        The job description is:
        --- JOB DESCRIPTION ---
        {jd_text[:2000]}
        --- END JOB DESCRIPTION ---

        Based on the comparison, the candidate is missing the following skills: {', '.join(missing_skills)}.

        Provide 3 to 5 concise, actionable suggestions for how the candidate can improve their resume to be a better fit for this job. Focus on highlighting relevant experience and tailoring the skills section.
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful career coach."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=200
        )
        
        suggestions_text = response.choices[0].message.content
        # Split suggestions by newline and clean them up
        suggestions = suggestions_text.split('\n')
        return [s.strip('-•* ').strip() for s in suggestions if s.strip()]

    except Exception as e:
        # Return a helpful error message if the API call fails
        return [f"Could not generate suggestions due to an API error: {str(e)}"]
