import streamlit as st
import requests
import pandas as pd
import os

# -------------------------------
# Configuration
# -------------------------------
# Use the correct IP address for your new server!
BACKEND_URL = os.getenv("BACKEND_URL", "http://34.221.106.207:8000")

# Page configuration
st.set_page_config(
    page_title="Automated Resume Relevance Dashboard",
    page_icon="📄",
    layout="wide"
)

# Main title
st.markdown("<h1 style='text-align:center;color:#4B0082;'>📄 Automated Resume Relevance Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Upload a job description and resumes to evaluate their relevance and view historical data.</p>", unsafe_allow_html=True)

# -------------------------------
# Tabs for navigation
# -------------------------------
tab1, tab2 = st.tabs(["🚀 Evaluate Resumes", "📊 Evaluation Dashboard"])

# -------------------------------
# Tab 1: Evaluate Resumes
# -------------------------------
with tab1:
    st.header("Upload Files for Evaluation")
    col1, col2 = st.columns(2)
    with col1:
        jd_file = st.file_uploader("1. Upload Job Description (Single PDF/DOCX)", type=["pdf", "docx"], key="jd_uploader")
    with col2:
        resume_files = st.file_uploader("2. Upload Resumes (Multiple PDF/DOCX)", type=["pdf", "docx"], accept_multiple_files=True, key="resume_uploader")

    if st.button("✨ Evaluate Resumes", use_container_width=True):
        if not jd_file or not resume_files:
            st.warning("⚠️ Please upload a Job Description and at least one resume to proceed.")
        else:
            with st.spinner("⏳ Evaluating resumes... This may take a moment depending on the number of files."):
                # Prepare files for the multipart/form-data request
                files = [("resumes", (r.name, r.getvalue(), r.type)) for r in resume_files]
                files.append(("jd", (jd_file.name, jd_file.getvalue(), jd_file.type)))

                try:
                    # Make the API call to the backend with a longer timeout
                    response = requests.post(f"{BACKEND_URL}/evaluate_batch", files=files, timeout=300)
                    response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

                    result = response.json()
                    st.success("✅ Evaluation complete!")
                    
                    if "jd_skills" in result:
                        st.subheader("Extracted Job Description Skills")
                        st.info(", ".join(result.get("jd_skills", ["No skills extracted."])))

                    st.subheader("Evaluation Results")
                    for res in result.get("results", []):
                        with st.expander(f"📝 **{res.get('resume_filename', 'Unknown Resume')}** - Final Score: **{res.get('score', 'N/A')}%**"):
                            st.markdown(f"**Verdict:** `{res.get('fit_verdict', 'N/A')}`")
                            
                            res_col1, res_col2 = st.columns(2)
                            with res_col1:
                                st.markdown("**✅ Matched Skills:**")
                                st.success(", ".join(res.get("matched_skills", ["None"])))
                            with res_col2:
                                st.markdown("**❌ Missing Skills:**")
                                st.warning(", ".join(res.get("missing_skills", ["None"])))
                            
                            st.markdown("**💡 Suggestions for Improvement:**")
                            suggestions = res.get("suggestions", [])
                            if suggestions:
                                for suggestion in suggestions:
                                    st.write(f"- {suggestion}")
                            else:
                                st.write("- No suggestions available.")
                
                except requests.exceptions.HTTPError as e:
                    st.error(f"❌ Backend Error: The server returned a {e.response.status_code} error. Please check the backend logs for details.")
                    st.code(e.response.text)
                except requests.exceptions.Timeout:
                    st.error("❌ Request Timed Out: The evaluation took too long. Please try with fewer resumes or check the backend server's performance.")
                except requests.exceptions.RequestException as e:
                    st.error(f"❌ Connection Failed: Could not connect to the backend at {BACKEND_URL}. Please ensure the backend is running and accessible. Details: {e}")

# -------------------------------
# Tab 2: Dashboard
# -------------------------------
with tab2:
    st.header("Historical Evaluation Data")
    
    # Add a refresh button
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()

    @st.cache_data(ttl=60) # Cache data for 60 seconds
    def get_evaluation_data():
        try:
            resp = requests.get(f"{BACKEND_URL}/evaluations", timeout=60)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Could not fetch evaluations from the backend: {e}")
            return None

    raw_data = get_evaluation_data()

    if raw_data is not None:
        if isinstance(raw_data, dict) and "error" in raw_data:
             st.error(f"Backend returned an error: {raw_data['error']}")
        elif isinstance(raw_data, list) and raw_data:
            df = pd.DataFrame(raw_data)
            
            st.dataframe(df)
            
            st.subheader("Score Distribution")
            scores = df['weighted_score'].dropna()
            if not scores.empty:
                st.bar_chart(scores)
            else:
                st.info("No score data available to display.")
        else:
            st.info("No evaluation data found. Evaluate some resumes in the first tab to see results here.")
