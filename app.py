import streamlit as st
import google.generativeai as genai
import os
import PyPDF2

# --- Page Config ---
st.set_page_config(page_title="Nexus-AI Elite", layout="wide", initial_sidebar_state="expanded")

# --- Initialize Gemini ---
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
else:
    st.error("❌ API Key Missing!")

# --- Elite CSS (Advanced UI) ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp { background-color: #0b0e11; color: #e1e1e1; }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] { background-color: #15191d !important; border-right: 1px solid #2d333b; }
    
    /* Custom Cards */
    .glass-card {
        background: #1c2128;
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #30363d;
        margin-bottom: 15px;
    }
    
    /* Neon Accents */
    .neon-blue { color: #58a6ff; font-weight: bold; }
    .neon-purple { color: #bc8cff; font-weight: bold; }
    
    /* Progress Bar Custom */
    .stProgress > div > div > div > div { background-color: #238636; }
    
    /* Chat Bubbles */
    .stChatMessage { background-color: #1c2128; border: 1px solid #30363d; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- Session State ---
if 'history' not in st.session_state: st.session_state.history = []
if 'step' not in st.session_state: st.session_state.step = 0
if 'resume_loaded' not in st.session_state: st.session_state.resume_loaded = False

# --- Sidebar (Left Analysis) ---
with st.sidebar:
    st.markdown("<h1 style='color:#58a6ff;'>Nexus-AI</h1>", unsafe_allow_html=True)
    
    # Resume Section
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    if not st.session_state.resume_loaded:
        uploaded = st.file_uploader("RESUME UPLOAD", type="pdf")
        if uploaded:
            st.session_state.resume_loaded = True
            st.rerun()
    else:
        st.success("✅ Resume Loaded")
    st.markdown("</div>", unsafe_allow_html=True)

    # Progress & Analytics
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.write("PROGRESS")
    st.progress(len(st.session_state.history) * 10) # Dynamic progress
    st.markdown("---")
    st.write("📊 LIVE ANALYSIS")
    st.write("Confidence: **85%**")
    st.write("Sentiment: <span style='color:#bc8cff;'>COOPERATIVE</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.button("Download Report 📥"):
        st.toast("Generating Report...")

# --- Main Dashboard ---
col_main, col_sec = st.columns([3, 1])

with col_sec:
    # Security Monitor (Right Side)
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 📹 LIVE SESSION")
    st.camera_input("CAM_01", label_visibility="collapsed")
    st.markdown("---")
    st.markdown("### 🛡️ SECURITY MONITOR")
    st.write("EYE TRACKING: <span style='color:#238636;'>STABLE</span>", unsafe_allow_html=True)
    st.write("AUDIO CLARITY: <span style='color:#58a6ff;'>HIGH</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_main:
    # Chat Area
    st.markdown("### 🤖 Interview Session")
    
    if not st.session_state.resume_loaded:
        st.info("Awaiting Resume Upload...")
    else:
        for msg in st.session_state.history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        if prompt := st.chat_input("Type your response..."):
            st.session_state.history.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("Nexus-AI is thinking..."):
                    # Simulating AI Response (Replace with actual Gemini call)
                    response = model.generate_content(prompt).text
                    st.markdown(response)
                    st.session_state.history.append({"role": "assistant", "content": response})
