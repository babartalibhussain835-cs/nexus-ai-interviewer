import streamlit as st
import os
from PyPDF2 import PdfReader
from textblob import TextBlob
import google.generativeai as genai
from datetime import datetime

# =========================
# CONFIG
# =========================

st.set_page_config(page_title="Nexus-AI Interviewer", layout="wide")

api_key = os.getenv("GEMINI_API_KEY")

model = None
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

# =========================
# CSS (Glassmorphism UI)
# =========================

st.markdown("""
<style>
body {
    background: #0e1117;
}

.glass {
    background: rgba(255,255,255,0.06);
    padding: 20px;
    border-radius: 15px;
    border: 1px solid rgba(0,255,255,0.3);
    box-shadow: 0 0 20px rgba(0,255,255,0.2);
    backdrop-filter: blur(10px);
    margin-bottom: 15px;
}

.status {
    color: #00ffff;
    font-weight: bold;
    font-size: 18px;
}

</style>
""", unsafe_allow_html=True)

# =========================
# SESSION STATE
# =========================

if "q_index" not in st.session_state:
    st.session_state.q_index = 0

if "questions" not in st.session_state:
    st.session_state.questions = []

if "answers" not in st.session_state:
    st.session_state.answers = []

if "scores" not in st.session_state:
    st.session_state.scores = []

if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""

# =========================
# SIDEBAR
# =========================

st.sidebar.title("Candidate Info")

resume = st.sidebar.file_uploader("Upload Resume PDF")
jd = st.sidebar.text_area("Job Description")

# =========================
# RESUME PARSER
# =========================

def extract_text(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

if resume:
    st.session_state.resume_text = extract_text(resume)

# =========================
# CHEATING DETECTION
# =========================

def detect_ai(text):
    if len(text.split()) < 10:
        return True
    if "therefore" in text.lower():
        return True
    if "as an ai" in text.lower():
        return True
    return False

# =========================
# SCORING
# =========================

def score_answer(text):
    sentiment = TextBlob(text).sentiment.polarity
    length_score = min(len(text.split()) / 20, 5)
    return round((sentiment + 1) * 2 + length_score, 2)

# =========================
# QUESTION GENERATION
# =========================

def generate_question():
    if not model:
        return "ERROR: GEMINI_API_KEY not set"

    last_answer = st.session_state.answers[-1] if st.session_state.answers else ""

    stages = [
        "Resume based introduction question",
        "Experience deep dive question",
        "Technical scenario question",
        "System design question",
        "Behavioral question",
        "Critical failure handling question"
    ]

    prompt = f"""
You are Nexus-AI Senior Recruiter.

Resume:
{st.session_state.resume_text}

Job Description:
{jd}

Previous Answer:
{last_answer}

Ask ONLY ONE question.
Stage: {stages[st.session_state.q_index]}
"""

    return model.generate_content(prompt).text

# =========================
# UI
# =========================

st.title("🧠 Nexus-AI Intelligent Interviewer")

st.camera_input("Live Camera Feed (Optional)")

st.markdown('<div class="status">AI STATUS: Listening...</div>', unsafe_allow_html=True)

# =========================
# INTERVIEW FLOW
# =========================

if st.session_state.q_index < 6:

    if st.button("Generate Question"):
        q = generate_question()
        st.session_state.questions.append(q)

    if st.session_state.questions:
        st.markdown(f'<div class="glass">{st.session_state.questions[-1]}</div>', unsafe_allow_html=True)

    answer = st.text_area("Your Answer")

    if st.button("Submit Answer") and answer:

        st.session_state.answers.append(answer)

        score = score_answer(answer)
        st.session_state.scores.append(score)

        if detect_ai(answer):
            st.warning("⚠ AI-like answer detected!")

        st.session_state.q_index += 1

# =========================
# FINAL REPORT
# =========================

if st.session_state.q_index >= 6:

    avg_score = sum(st.session_state.scores) / len(st.session_state.scores)

    if avg_score > 7:
        verdict = "Strong Hire"
    elif avg_score > 5:
        verdict = "Hire"
    else:
        verdict = "No Hire"

    st.subheader("📊 Hiring Report")

    st.write("Average Score:", avg_score)
    st.write("Verdict:", verdict)

    report = f"""
NEXUS AI INTERVIEW REPORT

Date: {datetime.now()}

Questions:
{st.session_state.questions}

Answers:
{st.session_state.answers}

Scores:
{st.session_state.scores}

Final Verdict: {verdict}
"""

    st.download_button("Download Report", report, "report.txt")
