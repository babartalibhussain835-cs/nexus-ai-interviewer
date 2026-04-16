import streamlit as st
import google.generativeai as genai
import os
from datetime import datetime
from PyPDF2 import PdfReader
from textblob import TextBlob

# =========================
# CONFIG
# =========================

st.set_page_config(
    page_title="Nexus AI Interviewer",
    layout="wide"
)

API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash")
else:
    model = None


# =========================
# UI STYLE
# =========================

st.markdown("""
<style>

body {
background:#0e1117;
}

.glass {
background: rgba(255,255,255,0.05);
border-radius:20px;
padding:20px;
border:1px solid rgba(0,255,255,0.2);
backdrop-filter: blur(12px);
margin-bottom:15px;
}

.status {
color:#00ffff;
font-weight:bold;
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
# HEADER
# =========================

st.title("🧠 Nexus AI Intelligent Interviewer")

st.markdown('<p class="status">AI STATUS: Listening...</p>',
            unsafe_allow_html=True)


# =========================
# SIDEBAR
# =========================

st.sidebar.header("Candidate Setup")

resume = st.sidebar.file_uploader("Upload Resume PDF")

job_description = st.sidebar.text_area(
    "Paste Job Description"
)


# =========================
# RESUME PARSER
# =========================

def extract_resume_text(file):

    reader = PdfReader(file)

    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    return text


if resume:
    st.session_state.resume_text = extract_resume_text(resume)


# =========================
# CAMERA PANEL
# =========================

st.camera_input("📷 Camera Presence Detection (Optional)")


# =========================
# CHEATING DETECTION
# =========================

def detect_cheating(answer):

    suspicious_words = [
        "as an ai",
        "language model",
        "therefore",
        "however"
    ]

    if len(answer.split()) < 6:
        return True

    for word in suspicious_words:
        if word in answer.lower():
            return True

    return False


# =========================
# SCORING ENGINE
# =========================

def score_answer(answer):

    sentiment = TextBlob(answer).sentiment.polarity

    length_score = min(len(answer.split()) / 10, 5)

    confidence_score = (sentiment + 1) * 2

    total = round(length_score + confidence_score, 2)

    return total


# =========================
# QUESTION ENGINE
# =========================

def generate_question():

    if not model:
        return "❌ GEMINI_API_KEY missing"

    stage_map = [

        "Resume introduction question",

        "Experience deep dive question",

        "Technical scenario question",

        "Problem solving question",

        "Behavioral teamwork question",

        "Failure handling leadership question"
    ]

    last_answer = ""

    if st.session_state.answers:
        last_answer = st.session_state.answers[-1]

    prompt = f"""

You are Nexus AI Senior Recruiter.

Candidate Resume:

{st.session_state.resume_text}

Job Description:

{job_description}

Previous Answer:

{last_answer}

Ask ONLY ONE interview question.

Stage:

{stage_map[st.session_state.q_index]}

"""

    response = model.generate_content(prompt)

    return response.text


# =========================
# INTERVIEW FLOW
# =========================

if st.session_state.q_index < 6:

    if st.button("Generate Question"):

        question = generate_question()

        st.session_state.questions.append(question)

    if st.session_state.questions:

        st.markdown(

            f'<div class="glass">{st.session_state.questions[-1]}</div>',

            unsafe_allow_html=True
        )

    answer = st.text_area("Your Answer")

    if st.button("Submit Answer"):

        if answer:

            st.session_state.answers.append(answer)

            score = score_answer(answer)

            st.session_state.scores.append(score)

            if detect_cheating(answer):

                st.warning("⚠ Possible AI-generated answer detected")

            st.session_state.q_index += 1


# =========================
# FINAL REPORT
# =========================

if st.session_state.q_index >= 6:

    avg_score = sum(
        st.session_state.scores
    ) / len(st.session_state.scores)

    if avg_score >= 7:

        verdict = "🔥 STRONG HIRE"

    elif avg_score >= 5:

        verdict = "✅ HIRE"

    else:

        verdict = "❌ NO HIRE"

    st.header("📊 Final Hiring Report")

    st.write("Average Score:", avg_score)

    st.write("Verdict:", verdict)

    report = f"""

NEXUS AI REPORT

Date:

{datetime.now()}

Questions:

{st.session_state.questions}

Answers:

{st.session_state.answers}

Scores:

{st.session_state.scores}

Verdict:

{verdict}

"""

    st.download_button(

        "Download Interview Report",

        report,

        "nexus_ai_report.txt"
    )
