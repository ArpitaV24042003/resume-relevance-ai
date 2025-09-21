import streamlit as st
import requests
import pandas as pd
import os

# -------------------------------
# Config
# -------------------------------
BACKEND_URL = os.getenv("BACKEND_URL", "http://44.251.109.205:8000")

st.set_page_config(
    page_title="Automated Resume Relevance Check & Dashboard",
    page_icon="📄",
    layout="wide"
)

st.markdown("<h1 style='text-align:center;color:#6A0DAD;'>📄 Automated Resume Relevance Check & Dashboard</h1>", unsafe_allow_html=True)

# -------------------------------
# Tabs
# -------------------------------
tab1, tab2 = st.tabs(["Evaluate Resumes", "Dashboard"])

# -------------------------------
# Tab 1: Evaluate Resumes
# -------------------------------
with tab1:
    st.subheader("Upload Job Description and Resumes")
    col1, col2 = st.columns(2)
    with col1:
        jd_file = st.file_uploader("Upload Job Description (PDF/DOCX)", type=["pdf", "docx"])
    with col2:
        resume_files = st.file_uploader("Upload Resumes (PDF/DOCX)", type=["pdf","docx"], accept_multiple_files=True)

    if st.button("🚀 Evaluate Resumes"):
        if not jd_file or not resume_files:
            st.warning("⚠ Please upload a JD and at least one resume.")
        else:
            with st.spinner("⏳ Evaluating resumes..."):
                files = [("resumes", (r.name, r, "application/octet-stream")) for r in resume_files]
                files.append(("jd", (jd_file.name, jd_file, "application/octet-stream")))

                try:
                    response = requests.post(f"{BACKEND_URL}/evaluate_batch", files=files, timeout=120)
                    if response.status_code == 200:
                        result = response.json()
                        st.success("✅ Evaluation complete!")
                        
                        st.markdown("### Job Description Skills")
                        st.write(", ".join(result.get("jd_skills", [])))

                        for res in result.get("results", []):
                            st.markdown(f"### 📝 {res.get('resume_filename', 'Unknown')}")
                            st.write("**Score:**", res.get("score", "N/A"))
                            st.write("**Verdict:**", res.get("fit_verdict", "N/A"))
                            st.write("**Matched Skills:**", ", ".join(res.get("matched_skills", [])))
                            st.write("**Missing Skills:**", ", ".join(res.get("missing_skills", [])))
                            st.write("**Suggestions:**")
                            for s in res.get("suggestions", []):
                                st.write("-", s)
                    else:
                        st.error(f"❌ Backend error {response.status_code}: {response.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"❌ Backend request failed: {e}")

# -------------------------------
# Tab 2: Dashboard
# -------------------------------
with tab2:
    st.subheader("Placement Team Dashboard: All Evaluations")
    try:
        resp = requests.get(f"{BACKEND_URL}/evaluations")
        data = resp.json()

        # Ensure data is a list of dicts
        if isinstance(data, dict):
            data = [data]  # wrap single dict in a list
        elif not isiimport streamlit as st
import requests
import pandas as pd
import os

# -------------------------------
# Configuration
# -------------------------------
# Use an environment variable for the backend URL, with a default for local testing
BACKEND_URL = os.getenv("BACKEND_URL", "http://34.221.106.207:8000")

# Page configuration
st.set_page_config(
    page_title="Automated Resume Relevance Dashboard",
    page_icon="📄",
    layout="wide"
)

# Main title
st.markdown("<h1 style='text-align:center;color:#6A0DAD;'>📄 Automated Resume Relevance Check & Dashboard</h1>", unsafe_allow_html=True)

# -------------------------------
# Tabs for navigation
# -------------------------------
tab1, tab2 = st.tabs(["Evaluate Resumes", "Evaluation Dashboard"])

# -------------------------------
# Tab 1: Evaluate Resumes
# -------------------------------
with tab1:
    st.subheader("Upload Job Description and Resumes")
    col1, col2 = st.columns(2)
    with col1:
        jd_file = st.file_uploader("Upload Job Description (PDF/DOCX)", type=["pdf", "docx"], key="jd_uploader")
    with col2:
        resume_files = st.file_uploader("Upload Resumes (PDF/DOCX)", type=["pdf", "docx"], accept_multiple_files=True, key="resume_uploader")

    if st.button("🚀 Evaluate Resumes"):
        if not jd_file or not resume_files:
            st.warning("⚠️ Please upload a Job Description and at least one resume.")
        else:
            with st.spinner("⏳ Evaluating resumes... This may take a moment."):
                # Prepare files for the multipart/form-data request
                files = [("resumes", (r.name, r.getvalue(), r.type)) for r in resume_files]
                files.append(("jd", (jd_file.name, jd_file.getvalue(), jd_file.type)))

                try:
                    # Make the API call to the backend
                    response = requests.post(f"{BACKEND_URL}/evaluate_batch", files=files, timeout=180) # Increased timeout for long evaluations
                    response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

                    result = response.json()
                    st.success("✅ Evaluation complete!")
                    
                    # Display Job Description Skills
                    st.markdown("### Job Description Skills")
                    st.info(", ".join(result.get("jd_skills", ["No skills extracted."])))

                    # Display results for each resume
                    for res in result.get("results", []):
                        with st.expander(f"📝 {res.get('resume_filename', 'Unknown Resume')} - Score: {res.get('score', 'N/A')}"):
                            st.markdown(f"**Verdict:** `{res.get('fit_verdict', 'N/A')}`")
                            st.markdown("**Matched Skills:**")
                            st.success(", ".join(res.get("matched_skills", ["None"])))
                            st.markdown("**Missing Skills:**")
                            st.warning(", ".join(res.get("missing_skills", ["None"])))
                            st.markdown("**Suggestions:**")
                            for suggestion in res.get("suggestions", []):
                                st.write(f"- {suggestion}")
                
                except requests.exceptions.HTTPError as e:
                    st.error(f"❌ Backend error {e.response.status_code}: {e.response.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"❌ Request failed: Could not connect to the backend. Please ensure it's running. Details: {e}")

# -------------------------------
# Tab 2: Dashboard
# -------------------------------
with tab2:
    st.subheader("Placement Team Dashboard: All Evaluations")
    try:
        resp = requests.get(f"{BACKEND_URL}/evaluations", timeout=60)
        resp.raise_for_status() # Check for HTTP errors
        
        raw_data = resp.json()

        # --- FIX: Normalize data to always be a list of dictionaries ---
        if isinstance(raw_data, dict):
            # If the API returns a single object, wrap it in a list
            processed_data = [raw_data]
        elif isinstance(raw_data, list):
            # If the API returns a list, use it directly
            processed_data = raw_data
        else:
            # If the API returns something else (e.g., null), treat it as empty
            processed_data = []

        if processed_data:
            # Now, creating the DataFrame is safe
            df = pd.DataFrame(processed_data)

            # --- Improved Filtering ---
            # Ensure 'verdict' column exists before trying to filter
            if 'verdict' in df.columns:
                # Get unique, non-null verdict options for the filter
                options = df['verdict'].dropna().unique()
                if len(options) > 0:
                    filter_verdict = st.multiselect("Filter by Verdict", options=options)
                    if filter_verdict:
                        # Apply filter if any options are selected
                        df = df[df['verdict'].isin(filter_verdict)]
            
            st.dataframe(df)
        else:
            st.info("No evaluation data found. Evaluate some resumes in the first tab to see results here.")

    except requests.exceptions.RequestException as e:
        st.error(f"❌ Could not fetch evaluations from the backend: {e}")
    except ValueError:
        # This catches JSON decoding errors if the backend response isn't valid JSON
        st.error("❌ Failed to decode data from the backend. The response was not in a valid format.")
nstance(data, list):
            data = []  # fallback if something unexpected is returned

        # Make sure each item is a dict
        data = [item if isinstance(item, dict) else {} for item in data]

        if data:
            df = pd.DataFrame(data)
            if 'verdict' in df.columns:
                filter_verdict = st.multiselect("Filter by Verdict", options=df['verdict'].unique())
                if filter_verdict:
                    df = df[df['verdict'].isin(filter_verdict)]
            st.dataframe(df)
        else:
            st.info("No evaluations found yet.")

    except requests.exceptions.RequestException as e:
        st.error(f"❌ Could not fetch evaluations from backend: {e}")
    except ValueError as ve:
        st.error(f"❌ Data format error: {ve}")
