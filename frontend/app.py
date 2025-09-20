import streamlit as st
import requests

st.set_page_config(page_title="AI Resume Relevance Checker", page_icon="📄")

st.title("📄 AI Resume Relevance Checker")

# --- Backend URL ---
BACKEND_URL = "http://127.0.0.1:8000/evaluate"

# --- Check backend connectivity ---
try:
    r = requests.get("http://127.0.0.1:8000/")
    if r.status_code == 200:
        st.success("Backend connected ✅")
    else:
        st.error("Backend not reachable ❌")
except requests.exceptions.RequestException:
    st.error("Backend not reachable ❌")

# --- File upload ---
resume_file = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx"])
jd_file = st.file_uploader("Upload Job Description (PDF/DOCX)", type=["pdf", "docx"])

# --- Button action ---
if st.button("Check Relevance"):
    if not resume_file or not jd_file:
        st.warning("Please upload both Resume and Job Description.")
    else:
        try:
            files = {
                "resume": resume_file,
                "jd": jd_file
            }
            response = requests.post(BACKEND_URL, files=files)
            result = response.json()
            
            if "error" in result:
                st.error(f"Error from backend: {result['error']}")
                st.write(result.get("raw", ""))
            else:
                # Display score as progress bar
                score = result.get("score", 0)
                st.subheader(f"Relevance Score: {score}/100")
                st.progress(score / 100)

                # Matched Skills
                matched = result.get("matched_skills", [])
                st.subheader("✅ Matched Skills")
                if matched:
                    st.write(", ".join(matched))
                else:
                    st.write("No matched skills found.")

                # Missing Skills
                missing = result.get("missing_skills", [])
                st.subheader("⚠️ Missing Skills")
                if missing:
                    st.write(", ".join(missing))
                else:
                    st.write("No missing skills!")

                # Suggestions
                suggestions = result.get("suggestions", [])
                st.subheader("💡 Suggestions")
                for i, s in enumerate(suggestions, start=1):
                    st.write(f"{i}. {s}")

        except requests.exceptions.RequestException as e:
            st.error(f"Failed to connect to backend: {e}")