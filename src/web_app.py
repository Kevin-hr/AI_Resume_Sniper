import os
import sys
import logging
import asyncio
import streamlit as st
from pathlib import Path

# Add parent directory to path to allow imports from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.engine import ResumeSniperEngine
from src.plugins.document_parsers import get_parser

# Configure Page
st.set_page_config(
    page_title="AI Resume Sniper",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Mobile Optimization
st.markdown("""
<style>
    /* Make buttons full width on mobile */
    .stButton button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
    }
    
    /* Increase font size for inputs */
    .stTextArea textarea {
        font-size: 16px;
    }
    
    /* Hide footer */
    footer {visibility: hidden;}
    
    /* Better spacing */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Engine (Cached)
@st.cache_resource
def get_engine():
    try:
        return ResumeSniperEngine()
    except Exception as e:
        st.error(f"Failed to initialize engine: {e}")
        return None

engine = get_engine()

def main():
    st.title("🎯 AI 简历狙击手")
    st.caption("AI 驱动的简历评分与优化助手")

    # --- Input Section ---
    with st.container():
        st.subheader("1. 上传简历")
        resume_file = st.file_uploader(
            "支持 PDF, DOCX, TXT", 
            type=["pdf", "docx", "txt", "md"],
            label_visibility="collapsed"
        )

        st.subheader("2. 职位描述 (JD)")
        jd_text = st.text_area(
            "粘贴职位描述...", 
            height=150,
            placeholder="请在此处粘贴目标职位的详细描述...",
            label_visibility="collapsed"
        )

        st.subheader("3. 目标角色")
        persona = st.selectbox(
            "选择面试官视角",
            ["hrbp", "technical_interviewer", "hiring_manager"],
            format_func=lambda x: {
                "hrbp": "HRBP (人力资源)",
                "technical_interviewer": "Technical Interviewer (技术面试官)",
                "hiring_manager": "Hiring Manager (招聘经理)"
            }.get(x, x),
            label_visibility="collapsed"
        )

    # --- Action Section ---
    st.divider()
    
    if st.button("开始分析 🚀", type="primary"):
        if not resume_file:
            st.warning("⚠️ 请先上传简历文件")
            return
        
        if not jd_text.strip():
            st.warning("⚠️ 请输入职位描述")
            return
            
        if not engine:
            st.error("❌ 引擎未初始化，无法分析")
            return

        with st.spinner("正在分析简历，请稍候..."):
            try:
                # 1. Parse File
                file_ext = os.path.splitext(resume_file.name)[1].lower()
                
                # Map extension to parser name
                ext_map = {
                    '.pdf': 'pdf',
                    '.docx': 'docx',
                    '.doc': 'docx',
                    '.txt': 'text',
                    '.md': 'text'
                }
                
                parser_name = ext_map.get(file_ext)
                if not parser_name:
                    st.error(f"不支持的文件格式: {file_ext}")
                    return

                parser = get_parser(parser_name)
                content_bytes = resume_file.getvalue()
                resume_text = parser.parse_content(content_bytes, file_ext)

                if not resume_text.strip():
                    st.error("无法从简历中提取文本，请检查文件是否损坏或加密。")
                    return

                # 2. Analyze
                result = engine.analyze(
                    resume_text=resume_text,
                    jd_text=jd_text,
                    persona=persona
                )

                # --- Result Section ---
                st.success("分析完成！")
                
                # Score Card
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("匹配得分", f"{result.score}/100")
                with col2:
                    st.metric("消耗 Token", result.tokens_used)

                # Report (Collapsible for mobile)
                with st.expander("📄 查看完整分析报告", expanded=True):
                    st.markdown(result.report)

                # Metadata
                with st.expander("ℹ️ 分析元数据"):
                    st.json({
                        "Model": result.model,
                        "Latency": f"{result.latency_ms:.2f} ms",
                        "Cached": result.cached
                    })

            except Exception as e:
                st.error(f"分析过程中发生错误: {str(e)}")
                logging.exception("Analysis failed")

if __name__ == "__main__":
    main()
