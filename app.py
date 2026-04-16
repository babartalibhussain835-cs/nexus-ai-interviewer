import streamlit as st
import google.generativeai as genai
import os
import PyPDF2
import io
import json
from datetime import datetime

# --- Configuration ---
st.set_page_config(page_title="Nexus-AI: Intelligent Interviewer", layout="wide")

# Initialize Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-pro')

# --- Custom CSS for Dark Glassmorphism ---
st.markdown("""
    <style>
    .stApp {
        background: #050505;
        color: #ffffff;
    }
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        margin-bottom: 20px;
    }
    .neon-text {
        color: #00f2ff;
        text-shadow: 0 0 10px rgba(0, 242, 255, 0.5);
    }
    .stButton>button {
        background: linear-gradient(45deg, #00f2ff, #7000ff);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 25px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        box-shadow: 0 0 20px rgba(0, 242, 255, 0.4);
        transform: translateY(-2px);
    }
    </style>
    """, unsafe_allow_html=True)

# --- Session State Management ---
if 'history' not in st.session_state:
    st.session_state.history = []
if 'current_q' not in st.session_state:
    st.session_state.current_q = 0
if 'resume_text' not in st.session_state:
    st.session_state.resume_text = ""
if 'interview_complete' not in st.session_state:
    st.session_state.interview_complete = False

# --- Helper Functions ---
def parse_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def get_ai_response(prompt, system_instruction=""):
    full_prompt = f"{system_instruction}\n\n{prompt}"
    response = model.generate_content(full_prompt)
    return response.text

# --- Sidebar: Resume Upload & Stats ---
with st.sidebar:
    st.markdown("<h1 class='neon-text'>Nexus-AI</h1>", unsafe_allow_html=True)
    st.write("Intelligent Interviewer v1.0")
    
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")
    if uploaded_file and not st.session_state.resume_text:
        with st.spinner("Parsing Resume..."):
            st.session_state.resume_text = parse_pdf(uploaded_file)
            st.success("Resume Loaded Successfully!")

    if st.session_state.resume_text:
        st.markdown("---")
        st.markdown("### Interview Progress")
        progress = st.session_state.current_q / 6
        st.progress(progress)
        st.write(f"Question {st.session_state.current_q} of 6")

# --- Main UI ---
col1, col2 = st.columns([2, 1])

with col2:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 📹 Live Feed")
    # Video Placeholder
    st.image("https://picsum.photos/seed/interview/400/300", caption="Candidate Camera Feed (Active)")
    
    st.markdown("### 🛡️ Security Monitor")
    st.info("Anti-Cheat Active: Monitoring tab focus and eye tracking.")
    st.markdown("</div>", unsafe_allow_html=True)

with col1:
    st.markdown("<h2 class='neon-text'>Technical Interview Session</h2>", unsafe_allow_html=True)
    
    if not st.session_state.resume_text:
        st.warning("Please upload a resume in the sidebar to begin.")
    elif st.session_state.current_q == 0:
        if st.button("Start Interview"):
            st.session_state.current_q = 1
            with st.spinner("Nexus-AI is thinking..."):
                prompt = f"Based on this resume: {st.session_state.resume_text}, generate the first technical interview question. Be specific and professional."
                q1 = get_ai_response(prompt, "You are an elite technical interviewer at a top tech firm.")
                st.session_state.history.append({"role": "AI", "content": q1})
                st.rerun()
    
    # Chat Interface
    chat_container = st.container()
    for msg in st.session_state.history:
        with chat_container.chat_message(msg["role"]):
            st.write(msg["content"])

    if st.session_state.current_q > 0 and not st.session_state.interview_complete:
        if user_input := st.chat_input("Your Answer..."):
            st.session_state.history.append({"role": "user", "content": user_input})
            
            # AI Thinking Logic
            with st.status("Nexus-AI is analyzing your response...", expanded=True) as status:
                st.write("Performing Sentiment Analysis...")
                # Sentiment/Confidence Analysis
                analysis_prompt = f"Analyze the confidence and technical depth of this answer: '{user_input}'. Return JSON with 'confidence' (0-100) and 'sentiment' (one word)."
                analysis = get_ai_response(analysis_prompt)
                
                st.write("Applying Anti-Cheat Pivot Logic...")
                # Adaptive Question Logic
                if st.session_state.current_q < 6:
                    st.session_state.current_q += 1
                    next_q_prompt = f"""
                    Resume: {st.session_state.resume_text}
                    History: {st.session_state.history}
                    Task: Generate question #{st.session_state.current_q}. 
                    If the previous answer was vague, use 'Anti-Cheat' pivot logic to ask for a specific implementation detail or edge case.
                    """
                    next_q = get_ai_response(next_q_prompt, "You are an elite technical interviewer.")
                    st.session_state.history.append({"role": "AI", "content": next_q})
                else:
                    st.session_state.interview_complete = True
                    st.write("Generating Final Report...")
                    report_prompt = f"Generate a final interview report (Scorecard 0-100, Strengths, Weaknesses) based on this transcript: {st.session_state.history}"
                    st.session_state.final_report = get_ai_response(report_prompt)
                
                status.update(label="Analysis Complete!", state="complete", expanded=False)
            st.rerun()

    # Final Report & Export
    if st.session_state.interview_complete:
        st.success("Interview Complete!")
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 📊 Final Scorecard")
        st.write(st.session_state.final_report)
        
        # Transcript Export
        transcript = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.history])
        full_report = f"NEXUS-AI INTERVIEW REPORT\nDate: {datetime.now()}\n\n{st.session_state.final_report}\n\nTRANSCRIPT:\n{transcript}"
        
        st.download_button(
            label="Download Full Report",
            data=full_report,
            file_name="NexusAI_Report.txt",
            mime="text/plain"
        )
        st.markdown("</div>", unsafe_allow_html=True)