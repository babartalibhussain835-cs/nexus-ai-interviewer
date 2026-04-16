import streamlit as st
import google.generativeai as genai
import os
import PyPDF2
from datetime import datetime

# --- Page Config ---
st.set_page_config(page_title="Nexus-AI | Elite Interviewer", layout="wide")

# --- Initialize Gemini (Upgraded to 2.0 Flash for 2026 Stability) ---
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    # 2.0 Flash is the most reliable model currently
    model = genai.GenerativeModel('gemini-2.0-flash')
else:
    st.error("❌ API Key Missing! Please add it to Cloud Run Environment Variables.")

# --- Professional UI ---
st.markdown("""
    <style>
    .main { background-color: #050505; color: white; }
    .stApp { background: #050505; }
    .glass-card {
        background: rgba(255, 255, 255, 0.07);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
    }
    .neon { color: #00f2ff; font-weight: bold; text-shadow: 0 0 10px #00f2ff; }
    .stButton>button { background: linear-gradient(90deg, #00f2ff, #7000ff); color: white; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- Session State ---
if 'history' not in st.session_state: st.session_state.history = []
if 'resume_text' not in st.session_state: st.session_state.resume_text = ""
if 'step' not in st.session_state: st.session_state.step = 0 
if 'final_report' not in st.session_state: st.session_state.final_report = ""

# --- Sidebar ---
with st.sidebar:
    st.markdown("<h1 class='neon'>Nexus-AI v2.0</h1>", unsafe_allow_html=True)
    st.write("Next-Gen Technical Assessment")
    
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")
    if uploaded_file and not st.session_state.resume_text:
        pdf = PyPDF2.PdfReader(uploaded_file)
        st.session_state.resume_text = " ".join([p.extract_text() for p in pdf.pages])
        st.success("✅ Resume Parsed!")
    
    st.markdown("---")
    if st.button("🔄 Reset Interview"):
        st.session_state.clear()
        st.rerun()

# --- Layout ---
col1, col2 = st.columns([2, 1])

with col2:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 📹 Live Security Feed")
    # Real Camera Integration
    st.camera_input("Security Monitor", key="secure_cam", label_visibility="collapsed")
    st.warning("🛡️ Anti-Cheat: Monitoring Active")
    st.markdown("</div>", unsafe_allow_html=True)

with col1:
    st.markdown("<h2 class='neon'>Technical Session</h2>", unsafe_allow_html=True)
    
    if not st.session_state.resume_text:
        st.info("👈 Please upload your resume in the sidebar to start.")
    else:
        # Step 0: Initial Question
        if st.session_state.step == 0:
            if st.button("🚀 Start Interview"):
                st.session_state.step = 1
                with st.spinner("AI is analyzing resume..."):
                    prompt = f"Resume: {st.session_state.resume_text}\nTask: You are an interviewer. Ask the first technical question."
                    resp = model.generate_content(prompt).text
                    st.session_state.history.append({"role": "assistant", "content": resp})
                st.rerun()

        # Chat display
        for msg in st.session_state.history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        # Step 1: 5 Questions Loop
        if st.session_state.step == 1:
            if user_ans := st.chat_input("Your Answer..."):
                st.session_state.history.append({"role": "user", "content": user_ans})
                
                with st.spinner("Processing..."):
                    ai_qs = [m for m in st.session_state.history if m['role']=='assistant']
                    if len(ai_qs) < 5:
                        prompt = f"History: {st.session_state.history}\nTask: Ask the next technical question."
                        resp = model.generate_content(prompt).text
                        st.session_state.history.append({"role": "assistant", "content": resp})
                    else:
                        st.session_state.step = 2
                        report_prompt = f"Transcript: {st.session_state.history}\nTask: Provide Scorecard and Feedback."
                        st.session_state.final_report = model.generate_content(report_prompt).text
                st.rerun()

        # Step 2: Final Report & Download
        if st.session_state.step == 2:
            st.success("✅ Interview Completed!")
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("### 📊 Performance Scorecard")
            st.write(st.session_state.final_report)
            
            report_out = f"NEXUS-AI FINAL REPORT\n{st.session_state.final_report}"
            st.download_button("📥 Download Report", report_out, file_name="NexusAI_Scorecard.txt")
            st.markdown("</div>", unsafe_allow_html=True)
