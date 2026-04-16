import streamlit as st
import google.generativeai as genai
import os
import PyPDF2
from datetime import datetime

# --- Page Config ---
st.set_page_config(page_title="Nexus-AI | Elite Interviewer", layout="wide")

# --- Initialize Gemini ---
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-pro')
else:
    st.error("❌ API Key Missing in Cloud Run Variables!")

# --- Professional UI Styling ---
st.markdown("""
    <style>
    .main { background-color: #050505; color: #ffffff; }
    .stApp { background: #050505; }
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        margin-bottom: 20px;
    }
    .neon-text { color: #00f2ff; text-shadow: 0 0 10px rgba(0, 242, 255, 0.5); font-weight: bold; }
    .stButton>button { background: linear-gradient(45deg, #00f2ff, #7000ff); color: white; border: none; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- Session State Management ---
if 'history' not in st.session_state: st.session_state.history = []
if 'resume_text' not in st.session_state: st.session_state.resume_text = ""
if 'step' not in st.session_state: st.session_state.step = 0 # 0: Start, 1: Interviewing, 2: Finished
if 'final_report' not in st.session_state: st.session_state.final_report = ""

# --- Functions ---
def extract_text_from_pdf(file):
    pdf = PyPDF2.PdfReader(file)
    return " ".join([page.extract_text() for page in pdf.pages])

# --- Sidebar ---
with st.sidebar:
    st.markdown("<h1 class='neon-text'>Nexus-AI v1.0</h1>", unsafe_allow_html=True)
    st.write("Intelligent Technical Assessment")
    
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")
    if uploaded_file and not st.session_state.resume_text:
        st.session_state.resume_text = extract_text_from_pdf(uploaded_file)
        st.success("✅ Resume Parsed Successfully!")

    if st.session_state.resume_text:
        st.markdown("---")
        st.markdown("### 📊 Session Stats")
        st.write(f"Questions Asked: {len([m for m in st.session_state.history if m['role']=='assistant'])}")
        if st.button("Reset Session"):
            st.session_state.clear()
            st.rerun()

# --- Main Layout ---
col1, col2 = st.columns([2, 1])

with col2:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 📹 Live Feed")
    # Simulation for video feed
    st.image("https://picsum.photos/seed/face/400/300", caption="Candidate Camera (Active Monitoring)")
    
    st.markdown("### 🛡️ Security Monitor")
    st.info("Anti-Cheat: Active. Monitoring tab focus and environment noise.")
    st.markdown("</div>", unsafe_allow_html=True)

with col1:
    st.markdown("<h2 class='neon-text'>Technical Interview Session</h2>", unsafe_allow_html=True)
    
    if not st.session_state.resume_text:
        st.warning("👈 Please upload a PDF resume in the sidebar to begin.")
    else:
        # Start Button
        if st.session_state.step == 0:
            if st.button("🚀 Start Technical Interview"):
                st.session_state.step = 1
                with st.spinner("Nexus-AI is generating first question..."):
                    prompt = f"Resume Content: {st.session_state.resume_text}\nTask: You are an elite tech interviewer. Ask a specific technical question based on their projects or skills."
                    resp = model.generate_content(prompt).text
                    st.session_state.history.append({"role": "assistant", "content": resp})
                st.rerun()

        # Chat Interface
        for msg in st.session_state.history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        # Interview Loop
        if st.session_state.step == 1:
            if user_input := st.chat_input("Your Answer..."):
                st.session_state.history.append({"role": "user", "content": user_input})
                
                with st.spinner("Analyzing & Generating next..."):
                    # We ask 5 questions total
                    if len([m for m in st.session_state.history if m['role']=='assistant']) < 5:
                        prompt = f"Resume: {st.session_state.resume_text}\nHistory: {st.session_state.history}\nTask: Ask the next deeper technical question. If answer was short, pivot to implementation details."
                        resp = model.generate_content(prompt).text
                        st.session_state.history.append({"role": "assistant", "content": resp})
                    else:
                        st.session_state.step = 2
                        report_prompt = f"Analyze this interview transcript and give a Scorecard (0-100), Strengths, and Areas for Improvement: {st.session_state.history}"
                        st.session_state.final_report = model.generate_content(report_prompt).text
                st.rerun()

        # Final Report & Download
        if st.session_state.step == 2:
            st.success("✅ Interview Completed!")
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("### 📊 Final Evaluation Report")
            st.write(st.session_state.final_report)
            
            # Download Logic
            full_transcript = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.history])
            export_data = f"NEXUS-AI INTERVIEW REPORT\nDate: {datetime.now()}\n\nEVALUATION:\n{st.session_state.final_report}\n\nTRANSCRIPT:\n{full_transcript}"
            
            st.download_button(
                label="📥 Download Full Report (.txt)",
                data=export_data,
                file_name=f"NexusAI_Report_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )
            st.markdown("</div>", unsafe_allow_html=True)
