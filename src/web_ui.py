import streamlit as st
import os
import pandas as pd
from resume_sniper import ResumeSniper
from document_parser import DocumentParser

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

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["1️⃣ Single Mode", "2️⃣ Batch Resumes", "3️⃣ Batch JDs"])

# --- Tab 1: Single Mode (Existing) ---
with tab1:
    st.header("Single Resume Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Candidate Resume")
        # Support file upload for single mode too
        resume_file = st.file_uploader("Upload Resume", type=['txt', 'md', 'pdf', 'docx'], key="single_resume_uploader")
        resume_text_area = st.text_area("Or Paste Content", height=300, placeholder="Paste the full text of the resume here...", key="single_resume_text")
        
        resume_text = ""
        if resume_file:
            parser = DocumentParser()
            # Save temp file to parse
            with open(resume_file.name, "wb") as f:
                f.write(resume_file.getbuffer())
            resume_text = parser.parse_file(resume_file.name)
            os.remove(resume_file.name) # Cleanup
        elif resume_text_area:
            resume_text = resume_text_area
    
    with col2:
        st.subheader("Target Job Description (JD)")
        jd_file = st.file_uploader("Upload JD", type=['txt', 'md', 'pdf', 'docx'], key="single_jd_uploader")
        jd_text_area = st.text_area("Or Paste Content", height=300, placeholder="Paste the Job Description here...", key="single_jd_text")

        jd_text = ""
        if jd_file:
            parser = DocumentParser()
            with open(jd_file.name, "wb") as f:
                f.write(jd_file.getbuffer())
            jd_text = parser.parse_file(jd_file.name)
            os.remove(jd_file.name)
        elif jd_text_area:
            jd_text = jd_text_area

    # --- Action ---
    analyze_btn = st.button("🚀 Analyze Single", type="primary", use_container_width=True)
    
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
            st.markdown("##" + sections[2]) # Red Flags
            if len(sections) > 4:
                st.markdown("##" + sections[4]) # Quick Fixes
                
        if st.session_state['tier'] >= 3:
            st.markdown("##" + sections[3]) # STAR Rewrites
            st.balloons()

# --- Tab 2: Batch Resumes (1 JD vs N Resumes) ---
with tab2:
    st.header("Batch Resumes Matching (1 JD vs N Resumes)")
    
    st.subheader("1. Target Job Description (JD)")
    batch_jd_text = st.text_area("Paste JD Content", height=200, key="batch_resumes_jd")
    
    st.subheader("2. Upload Resumes")
    uploaded_resumes = st.file_uploader("Upload Multiple Resumes", type=['txt', 'md', 'pdf', 'docx'], accept_multiple_files=True, key="batch_resumes_uploader")
    
    if st.button("🚀 Analyze Batch Resumes", type="primary"):
        if not batch_jd_text or not uploaded_resumes:
            st.error("Please provide JD and upload at least one resume.")
        else:
            parser = DocumentParser()
            sniper = ResumeSniper()
            results = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, uploaded_file in enumerate(uploaded_resumes):
                status_text.text(f"Processing {uploaded_file.name}...")
                
                # Save temp file
                with open(uploaded_file.name, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                try:
                    resume_content = parser.parse_file(uploaded_file.name)
                    report = sniper.analyze(resume_content, batch_jd_text)
                    
                    # Extract Score (Simple heuristic parsing)
                    score = "N/A"
                    try:
                        # Looking for "Match Score: 65/100" or similar
                        import re
                        match = re.search(r"Score.*?(\d+)", report, re.IGNORECASE)
                        if match:
                            score = int(match.group(1))
                    except:
                        pass
                    
                    results.append({
                        "File Name": uploaded_file.name,
                        "Score": score,
                        "Report": report
                    })
                except Exception as e:
                    st.error(f"Error processing {uploaded_file.name}: {e}")
                finally:
                    if os.path.exists(uploaded_file.name):
                        os.remove(uploaded_file.name)
                
                progress_bar.progress((i + 1) / len(uploaded_resumes))
            
            status_text.text("Batch Analysis Complete!")
            
            # Display Results
            df = pd.DataFrame(results)
            st.dataframe(df[["File Name", "Score"]])
            
            # Export
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Results CSV",
                data=csv,
                file_name="batch_resume_results.csv",
                mime="text/csv",
            )
            
            # Detailed Reports
            with st.expander("View Detailed Reports"):
                for res in results:
                    st.markdown(f"### {res['File Name']} (Score: {res['Score']})")
                    st.markdown(res['Report'])
                    st.divider()

# --- Tab 3: Batch JDs (1 Resume vs N JDs) ---
with tab3:
    st.header("Batch JDs Matching (1 Resume vs N JDs)")
    
    st.subheader("1. Candidate Resume")
    batch_resume_text = st.text_area("Paste Resume Content", height=200, key="batch_jds_resume")
    
    st.subheader("2. Upload Job Descriptions")
    uploaded_jds = st.file_uploader("Upload Multiple JDs", type=['txt', 'md', 'pdf', 'docx'], accept_multiple_files=True, key="batch_jds_uploader")
    
    if st.button("🚀 Analyze Batch JDs", type="primary"):
        if not batch_resume_text or not uploaded_jds:
            st.error("Please provide Resume and upload at least one JD.")
        else:
            parser = DocumentParser()
            sniper = ResumeSniper()
            results = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, uploaded_file in enumerate(uploaded_jds):
                status_text.text(f"Processing {uploaded_file.name}...")
                
                with open(uploaded_file.name, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                try:
                    jd_content = parser.parse_file(uploaded_file.name)
                    report = sniper.analyze(batch_resume_text, jd_content)
                    
                    score = "N/A"
                    try:
                        import re
                        match = re.search(r"Score.*?(\d+)", report, re.IGNORECASE)
                        if match:
                            score = int(match.group(1))
                    except:
                        pass
                    
                    results.append({
                        "JD File": uploaded_file.name,
                        "Score": score,
                        "Report": report
                    })
                except Exception as e:
                    st.error(f"Error processing {uploaded_file.name}: {e}")
                finally:
                    if os.path.exists(uploaded_file.name):
                        os.remove(uploaded_file.name)
                
                progress_bar.progress((i + 1) / len(uploaded_jds))
            
            status_text.text("Batch Analysis Complete!")
            
            df = pd.DataFrame(results)
            st.dataframe(df[["JD File", "Score"]])
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Results CSV",
                data=csv,
                file_name="batch_jd_results.csv",
                mime="text/csv",
            )
            
            with st.expander("View Detailed Reports"):
                for res in results:
                    st.markdown(f"### {res['JD File']} (Score: {res['Score']})")
                    st.markdown(res['Report'])
                    st.divider()

# --- Footer ---
st.markdown("---")
st.markdown("© 2025 Digital Life Kha'Zix System | Built with Skill 01 & Skill 02")
