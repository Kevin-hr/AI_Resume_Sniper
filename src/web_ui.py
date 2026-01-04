import streamlit as st
import os
from resume_sniper import ResumeSniper

# --- Page Config ---
st.set_page_config(
    page_title="AI Resume Sniper",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Styling ---
st.markdown("""
<style>
    .report-container {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #ff4b4b;
    }
    .score-card {
        text-align: center;
        padding: 20px;
        background: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 3em;
        font-weight: bold;
        color: #ff4b4b;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.title("🎯 AI Resume Sniper")
st.markdown("**Your 24/7 Virtual HRBP Consultant.** *Pass the ATS. Get the Interview.*")

# --- Sidebar: Configuration ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Key Management
    api_key_input = st.text_input("DeepSeek API Key", type="password", help="Enter your API Key if not set in environment variables.")
    
    if api_key_input:
        # Override the hardcoded key in resume_sniper.py for this session
        # Note: In a real app, use st.session_state or environment variables securely
        pass 
    
    st.info("💡 **Pro Tip**: Paste the Job Description exactly as it appears on the hiring site.")
    st.divider()
    st.markdown("### 🛠️ Mode")
    mode = st.radio("Select Mode", ["Strict (HRBP)", "Coach (Friendly)"], index=0)

# --- Main Interface ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("1️⃣ Candidate Resume")
    resume_text = st.text_area("Paste Resume Content Here", height=300, placeholder="Paste the full text of the resume here...")

with col2:
    st.subheader("2️⃣ Target Job Description (JD)")
    jd_text = st.text_area("Paste JD Content Here", height=300, placeholder="Paste the Job Description here...")

# --- Action ---
analyze_btn = st.button("🚀 Analyze Resume", type="primary", use_container_width=True)

if analyze_btn:
    if not resume_text or not jd_text:
        st.error("⚠️ Please provide BOTH Resume and JD content.")
    else:
        with st.spinner("🤖 Sniper is scanning your resume... (Simulating 6-second HR scan)"):
            try:
                # Initialize Sniper
                sniper = ResumeSniper()
                
                # Run Analysis
                full_report = sniper.analyze(resume_text, jd_text)
                
                # --- Tier 1: Free Hook ---
                st.success("Analysis Complete!")
                st.subheader("📄 Sniper Report (Preview)")
                
                # Split report to simulate locking
                # Note: In production, backend should only return partial data to frontend
                sections = full_report.split("##")
                
                # Display Score (Always Free)
                score_section = "##" + sections[1] if len(sections) > 1 else "Score not found"
                st.markdown(score_section)
                
                st.warning("🔒 **Full Report Locked**")
                
                col_p1, col_p2 = st.columns(2)
                
                with col_p1:
                    st.info("**Tier 2: Core Report (¥9.9)**\n\n✅ All Red Flags\n\n✅ Quick Fixes")
                    if st.button("🔓 Unlock Core Report (¥9.9)"):
                        st.session_state['tier'] = 2
                        st.rerun()

                with col_p2:
                    st.error("**Tier 3: Premium Asset (¥19.9)**\n\n✅ Everything in Tier 2\n\n💎 **STAR Rewrites**")
                    if st.button("💎 Unlock Premium (¥19.9)"):
                        st.session_state['tier'] = 3
                        st.rerun()
                
                # Store report in session state
                st.session_state['full_report'] = full_report
                
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")

# --- Display Unlocked Content (Based on Payment) ---
if 'tier' in st.session_state and 'full_report' in st.session_state:
    report = st.session_state['full_report']
    sections = report.split("##")
    
    st.markdown("---")
    st.header("🔓 Unlocked Content")
    
    if st.session_state['tier'] >= 2:
        # Show Red Flags & Quick Fixes (Usually section 2 & 4 in our prompt structure)
        # Note: This index parsing is fragile and relies on Prompt structure. 
        # For production, return JSON.
        st.markdown("##" + sections[2]) # Red Flags
        if len(sections) > 4:
            st.markdown("##" + sections[4]) # Quick Fixes
            
    if st.session_state['tier'] >= 3:
        # Show STAR Rewrites (Section 3)
        st.markdown("##" + sections[3]) # STAR Rewrites
        st.balloons()

# --- Footer ---
st.markdown("---")
st.markdown("© 2025 Digital Life Kha'Zix System | Built with Skill 01 & Skill 02")
