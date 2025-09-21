import streamlit as st
import requests

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(
    page_title="Automated Resume Relevance Check",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------
# Custom CSS
# -------------------------------
st.markdown("""
<style>
/* Sidebar */
.css-1d391kg {background-color: #6A0DAD !important;}
.css-1d391kg .css-qrbaxs {color: white !important;}
.css-1d391kg .css-16idsys {color: #dcd6f7 !important;}

/* Title */
.dashboard-title {
    font-size: 38px; font-weight: 900;
    color: #6A0DAD; text-align: center;
    margin-bottom: 20px;word-wrap: break-word;
}

/* Card */
.card {
    background: white;
    border-radius: 20px;
    padding: 20px;
    margin-bottom: 25px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
}

/* Buttons */
.stButton>button {
    background: linear-gradient(90deg, #6A0DAD, #9A4DFF);
    color: white; font-size:16px; font-weight:bold;
    padding:12px 28px; border-radius:12px; border:none;
    cursor:pointer; transition: all 0.3s ease-in-out;
}
.stButton>button:hover {
    background: linear-gradient(90deg, #4B0082, #7A2DE8);
    transform: scale(1.07);
}

/* Score Box */
.score-box {
    background: linear-gradient(135deg, #6A0DAD, #9A4DFF);
    color:white; font-size:26px; font-weight:700;
    text-align:center; border-radius:16px;
    padding:18px; margin-bottom:20px;
}

/* Verdict Colors */
.verdict-high { color: #2ECC71; font-weight:bold; font-size:22px; }
.verdict-medium { color: #E67E22; font-weight:bold; font-size:22px; }
.verdict-low { color: #E74C3C; font-weight:bold; font-size:22px; }

/* Scrollable results box */
.results-container {
    max-height: 500px;
    overflow-y: auto;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 12px;
    background-color: #fafafa;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# Sidebar
# -------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/document.png", width=100)
    st.title("Resume Relevance Dashboard")
    st.markdown("📊 AI-powered JD vs Resume analysis.")
    st.markdown("👩‍💻 Built with Streamlit")
    st.markdown("🚀 Theme 2: Modern UI Design")

# -------------------------------
# Title
# -------------------------------
st.markdown('<div class="dashboard-title">📄 Automated Resume Relevance Check</div>', unsafe_allow_html=True)

# -------------------------------
# Backend URL
# -------------------------------
BACKEND_URL = "http://44.251.109.205:8000"  # <-- Replace <AWS_PUBLIC_IP> with your EC2 public IP

# -------------------------------
# File Upload Section
# -------------------------------
col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="card"><h3>📑 Upload Job Description (JD)</h3></div>', unsafe_allow_html=True)
    jd_file = st.file_uploader("Upload JD (PDF/DOCX)", type=["pdf", "docx"])
with col2:
    st.markdown('<div class="card"><h3>📂 Upload Candidate Resumes</h3></div>', unsafe_allow_html=True)
    resume_files = st.file_uploader("Upload Resumes (PDF/DOCX)", type=["pdf","docx"], accept_multiple_files=True)

# -------------------------------
# Action Button
# -------------------------------
if st.button("🚀 Check Relevance"):
    if not jd_file or not resume_files:
        st.warning("⚠ Please upload a JD and at least one resume.")
    else:
        with st.spinner("⏳ Evaluating resumes..."):
            files = [("resumes", (r.name, r, "application/octet-stream")) for r in resume_files]
            files.append(("jd", (jd_file.name, jd_file, "application/octet-stream")))

            try:
                response = requests.post("http://44.251.109.205:8000/evaluate_batch", files=files, timeout=120)  # increased timeout

                if response.status_code == 200:
                    try:
                        result = response.json()
                    except Exception:
                        st.error("❌ Backend returned non-JSON response.")
                        st.stop()
                else:
                    st.error(f"❌ Backend returned error {response.status_code}: {response.text}")
                    st.stop()

                # Display JD Skills
                st.markdown('<div class="card"><h3>📌 Job Description Skills</h3></div>', unsafe_allow_html=True)
                st.markdown(f"JD File: {jd_file.name}")
                st.write(", ".join(result.get("jd_skills", [])))

                # Display Resume Results
                st.markdown('<div class="results-container">', unsafe_allow_html=True)

                for res in result.get("results", []):
                    st.markdown(f'<div class="card"><h3>📝 Resume: {res["resume_filename"]}</h3></div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="score-box">Relevance Score: {res["score"]}/100</div>', unsafe_allow_html=True)

                    verdict = res.get("fit_verdict", "Medium")
                    verdict_class = "verdict-medium"
                    if verdict.lower() == "high":
                        verdict_class = "verdict-high"
                    elif verdict.lower() == "low":
                        verdict_class = "verdict-low"
                    st.markdown(f'<div class="{verdict_class}">🏆 Fit Verdict: {verdict}</div>', unsafe_allow_html=True)

                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown('<div class="card"><h4>✅ Matched Skills</h4></div>', unsafe_allow_html=True)
                        matched = res.get("matched_skills", [])
                        st.markdown(f'<p style="font-size:20px; font-weight:bold; color:#2E8B57;">{", ".join(matched) if matched else "No matched skills found."}</p>', unsafe_allow_html=True)

                    with col2:
                        st.markdown('<div class="card"><h4>⚠ Missing Skills</h4></div>', unsafe_allow_html=True)
                        missing = res.get("missing_skills", [])
                        st.markdown(f'<p style="font-size:20px; font-weight:bold; color:#E67E22;">{", ".join(missing) if missing else "No missing skills!"}</p>', unsafe_allow_html=True)

                    st.markdown('<div class="card"><h4>💡 Suggestions</h4></div>', unsafe_allow_html=True)
                    suggestions = res.get("suggestions", [])
                    if suggestions:
                        for i, s in enumerate(suggestions, start=1):
                            st.markdown(f'<p style="font-size:18px; font-weight:bold; color:#6A0DAD;">{i}. {s}</p>', unsafe_allow_html=True)
                    else:
                        st.markdown('<p style="font-size:18px; font-weight:bold; color:#7F8C8D;">No suggestions available.</p>', unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)

            except requests.exceptions.Timeout:
                st.error("❌ Backend request timed out. Try again.")
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Error connecting to backend: {e}")
API_URL = "http://44.251.109.205:8000"
