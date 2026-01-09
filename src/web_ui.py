"""
Web UI / Web界面
Streamlit-based web interface for HRD's Blackbox (formerly AI Resume Sniper).
"""

import sys
import streamlit as st
import os
import pandas as pd
import re
import json
from pathlib import Path
from dotenv import load_dotenv
import plotly.graph_objects as go

# Load .env file with override to ensure local settings take precedence
load_dotenv(override=True)

# Add parent directory to path for imports
_current_dir = Path(__file__).parent.resolve()
_parent_dir = _current_dir.parent
if str(_parent_dir) not in sys.path:
    sys.path.insert(0, str(_parent_dir))

# Import from new plugin architecture
from src.core.engine import ResumeSniperEngine
from src.core.config import get_config
from src.plugins.document_parsers import get_parser_for_file
from src.core.exceptions import PluginNotFoundError, UnsupportedFormatError

# --- Page Config ---
st.set_page_config(
    page_title="天生我才 | HRD 的黑匣子",
    page_icon="💼",
    layout="wide"
)

# --- Translations ---
TRANSLATIONS = {
    'en': {
        # Pain Points / 用户痛点
        'pain1_title': '😰 Resume Ghosted',
        'pain1_desc': 'Sent 100+ applications, zero callbacks. What\'s wrong with my resume?',
        'pain2_title': '😕 Lost in the Market',
        'pain2_desc': 'Don\'t know my real market value. Am I undercharging myself?',
        'pain3_title': '😓 Achievements to Duties',
        'pain3_desc': 'My resume reads like a job description, not an achievement log.',
        # Solution / 爽点
        'solution1_title': '🎯 See Why You\'re Rejected',
        'solution1_desc': 'Know exactly why HR rejects you in 6 seconds. Fix it fast.',
        'solution2_title': '💎 Know Your Worth',
        'solution2_desc': 'Discover hidden assets and market positioning.',
        'solution3_title': '✨ STAR Rewrite',
        'solution3_desc': 'Turn平淡描述 into 量化成果 that HR loves.',
        # Tabs
        'tab_diagnostic': '🔍 Who Am I?',
        'tab_career': '💼 Resume Audit',
        'tab_side_hustle': '🚀 Side Hustle',
        'tab_headhunter': '💰 Recruiter Mode',
        # Actions
        'btn_diagnostic': '🔍 Diagnose My Value',
        'btn_analyze': '🎯 Audit My Resume',
        'btn_hustle': '💰 Smart JD (Coming Soon)',
        'btn_headhunter': '💼 Generate Candidate Packet',
        # Form labels
        'resume_label': 'Your Resume',
        'upload_resume': 'Upload (PDF/DOCX/Txt)',
        'paste_resume': 'Or paste here...',
        'jd_label': 'Target Job Description',
        'upload_jd': 'Upload JD',
        'paste_jd': 'Or paste JD here...',
        # Status
        'no_resume': 'Please upload your resume.',
        'no_jd': 'Please provide a job description.',
        'processing_diag': '🧠 HRD is analyzing your hidden value...',
        'processing_audit': '🎯 Auditing your resume against the JD...',
        'diag_complete': '✅ Diagnosis Complete',
        'audit_complete': '✅ Audit Complete',
        'footer': '15-year HRD experience in your pocket',
        # Settings
        'settings': 'Settings',
        'provider': 'LLM Provider',
        'api_key': 'API Key',
        'api_key_help': 'Leave empty to use .env',
        'model': 'Model Name',
        'persona': 'Analysis Persona',
        'use_cache': 'Enable Cache',
        'engine_error': 'Engine not initialized. Please check sidebar settings.',
    },
    'zh': {
        # Pain Points / 用户痛点
        'pain1_title': '😰 简历石沉大海',
        'pain1_desc': '投了100份，一个回复都没有？到底哪里出了问题？',
        'pain2_title': '😕 不知道自己值多少钱',
        'pain2_desc': '市场定位模糊，薪资谈判心里没底。',
        'pain3_title': '😓 写成岗位职责而不是成绩',
        'pain3_desc': '简历写的是"做了什么"，没有"做成什么"。',
        # Solution / 爽点
        'solution1_title': '🎯 6秒被拒的原因，一目了然',
        'solution1_desc': '精准定位简历硬伤，告诉你怎么改。',
        'solution2_title': '💎 挖掘你的隐性价值',
        'solution2_desc': '发现你没意识到的市场价值。',
        'solution3_title': '✨ 自动 STAR 重写',
        'solution3_desc': '把平淡描述改成HR爱看的量化成果。',
        # Tabs
        'tab_diagnostic': '🔍 我是谁？(深度诊断)',
        'tab_career': '💼 简历匹配 (职场突围)',
        'tab_side_hustle': '🚀 副业变现 (智能 JD)',
        'tab_headhunter': '💰 猎头模式 (推荐报告)',
        # Actions
        'btn_diagnostic': '🔍 深度挖掘我的价值',
        'btn_analyze': '🎯 帮我过 HR 这一关',
        'btn_hustle': '🚀 生成副业 JD',
        'btn_headhunter': '📝 生成候选人推荐报告',
        # Form labels
        'resume_label': '上传你的简历',
        'upload_resume': '选择文件 (PDF/DOCX/Txt)',
        'paste_resume': '或直接粘贴简历内容...',
        'jd_label': '目标职位描述 (JD)',
        'upload_jd': '上传 JD 文件',
        'paste_jd': '或直接粘贴 JD 内容...',
        # Status
        'no_resume': '请先上传或粘贴简历',
        'no_jd': '请先上传或粘贴职位描述',
        'processing_diag': '🧠 HRD 正在深度分析你的价值...',
        'processing_audit': '🎯 正在对比简历和JD，找出差距...',
        'diag_complete': '✅ 深度诊断完成',
        'audit_complete': '✅ 简历分析完成',
        'footer': '把15年HRD经验装进口袋',
        # Settings
        'settings': '设置',
        'provider': 'AI 模型提供商',
        'api_key': 'API Key (可选)',
        'api_key_help': '留空则使用 .env 配置',
        'model': '模型名称',
        'persona': '分析角色',
        'use_cache': '启用缓存',
        'engine_error': '引擎未初始化，请检查左侧设置。',
    }
}

def t(key):
    lang = st.session_state.get('lang', 'zh')
    return TRANSLATIONS[lang].get(key, key)

# --- Helper Functions ---
def get_content_list(uploaded_files, text_area_content, label):
    """Returns a list of dictionaries: [{'name': '...', 'content': '...'}]"""
    content_list = []

    # Process Uploaded Files
    if uploaded_files:
        for uploaded_file in uploaded_files:
            # Save temp file
            with open(uploaded_file.name, "wb") as f:
                f.write(uploaded_file.getbuffer())

            try:
                parser = get_parser_for_file(uploaded_file.name)
                doc = parser.parse(uploaded_file.name)
                content_list.append({
                    "name": uploaded_file.name,
                    "content": doc.content,
                    "type": doc.file_type
                })
            except UnsupportedFormatError:
                st.error(f"❌ Unsupported format: {uploaded_file.name}")
            except Exception as e:
                st.error(f"❌ Error parsing {uploaded_file.name}: {e}")
            finally:
                if os.path.exists(uploaded_file.name):
                    os.remove(uploaded_file.name)

    # Process Text Area
    if text_area_content and text_area_content.strip():
        name = f"Manual {label} Input"
        content_list.append({
            "name": name,
            "content": text_area_content,
            "type": "text"
        })

    return content_list

def extract_score(report_text):
    try:
        match = re.search(r"Score.*?(\d+)", report_text, re.IGNORECASE)
        if match:
            return int(match.group(1))
    except:
        pass
    return None

def get_score_color(score):
    if score is None: return "gray"
    if score >= 80: return "green"
    if score >= 60: return "orange"
    return "red"

def parse_and_preview_file(uploaded_file):
    """Parse uploaded file and return content with preview."""
    if uploaded_file is None:
        return None, None

    # Save temp file
    temp_path = uploaded_file.name
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    try:
        parser = get_parser_for_file(temp_path)
        doc = parser.parse(temp_path)
        content = doc.content
        preview = content[:500] + "..." if len(content) > 500 else content
        return content, preview
    except UnsupportedFormatError:
        return None, f"❌ 不支持的格式: {uploaded_file.name}"
    except Exception as e:
        return None, f"❌ 解析错误: {e}"
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def extract_radar_data(report_text):
    """Extract radar chart data from report JSON block."""
    try:
        # Look for JSON block with radar data
        pattern = r'```json\s*(\{[^`]*"radar"[^`]*\})\s*```'
        match = re.search(pattern, report_text, re.DOTALL)
        if match:
            data = json.loads(match.group(1))
            return data.get("radar", {})

        # Fallback: try to find inline JSON
        pattern2 = r'\{"radar":\s*\{[^}]+\}\}'
        match2 = re.search(pattern2, report_text)
        if match2:
            data = json.loads(match2.group(0))
            return data.get("radar", {})
    except:
        pass
    return None

def render_radar_chart(radar_data):
    """Render radar chart using Plotly."""
    if not radar_data:
        return None

    categories = list(radar_data.keys())
    values = list(radar_data.values())

    # Close the radar chart
    categories = categories + [categories[0]]
    values = values + [values[0]]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='能力雷达',
        line_color='#667eea',
        fillcolor='rgba(102, 126, 234, 0.3)'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=10)
            ),
            angularaxis=dict(
                tickfont=dict(size=12)
            )
        ),
        showlegend=False,
        title=dict(
            text="📊 能力雷达图",
            x=0.5,
            font=dict(size=16)
        ),
        height=400,
        margin=dict(l=60, r=60, t=60, b=60)
    )

    return fig

# --- Main UI ---

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/resume.png", width=64)
    st.markdown("## HRD's Blackbox")
    
    lang_select = st.selectbox("Language / 语言", ["zh", "en"], index=0)
    st.session_state['lang'] = lang_select
    
    st.divider()
    st.markdown(f"### {t('settings')}")
    
    # Init Engine Logic
    config = get_config()
    
    # 强制使用 DeepSeek
    provider = st.selectbox(t('provider'), ["deepseek"], index=0)
    api_key = st.text_input(t('api_key'), type="password", help=t('api_key_help'))
    if api_key:
        os.environ[f"{provider.upper()}_API_KEY"] = api_key
        
    # 获取默认模型
    default_model_name = "deepseek-chat"
        
    model = st.text_input(t('model'), value=default_model_name)
    persona_key = st.selectbox(t('persona'), ["hrbp", "coach", "product_manager", "headhunter"], index=0)
    use_cache = st.checkbox(t('use_cache'), value=True)
    
    if st.button("Reload Engine"):
        if 'engine' in st.session_state:
            del st.session_state['engine']

# Initialize Engine
if 'engine' not in st.session_state:
    try:
        st.session_state.engine = ResumeSniperEngine(llm_provider=provider)
    except Exception as e:
        st.sidebar.error(f"Engine Init Error: {e}")

# ========================================
# 🚀 HOMEPAGE - 用户视角
# ========================================

st.markdown("""
<div style='text-align: center; padding: 20px 0;'>
    <h1 style='font-size: 2.5em; margin-bottom: 10px;'>💼 天生我才</h1>
    <p style='font-size: 1.2em; color: #666;'>把15年HRD经验装进口袋</p>
</div>
""", unsafe_allow_html=True)

# --- 痛点区 ---
st.markdown("### 😰 你的困扰")
col_pain1, col_pain2, col_pain3 = st.columns(3)
with col_pain1:
    st.error(f"**{t('pain1_title')}**\n\n{t('pain1_desc')}")
with col_pain2:
    st.warning(f"**{t('pain2_title')}**\n\n{t('pain2_desc')}")
with col_pain3:
    st.info(f"**{t('pain3_title')}**\n\n{t('pain3_desc')}")

st.markdown("---")

# --- 爽点区 ---
st.markdown("### ✨ 我来帮你")
col_sol1, col_sol2, col_sol3 = st.columns(3)
with col_sol1:
    st.success(f"**{t('solution1_title')}**\n\n{t('solution1_desc')}")
with col_sol2:
    st.success(f"**{t('solution2_title')}**\n\n{t('solution2_desc')}")
with col_sol3:
    st.success(f"**{t('solution3_title')}**\n\n{t('solution3_desc')}")

st.markdown("---")

# --- 功能选择 ---
st.markdown("### 🎯 选择你的需求")
tab_career, tab_diag, tab_hustle, tab_headhunter = st.tabs([t('tab_career'), t('tab_diagnostic'), t('tab_side_hustle'), t('tab_headhunter')])

# --- Tab 1: Career (简历优化/精准狙击) ---
with tab_career:
    st.markdown("""
    **💼 简历优化：你的简历能通过HR的6秒筛选吗？**

    上传简历 + 目标岗位JD，精准定位差距，给出STAR重写建议。
    """)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**{t('resume_label')}**")
        uploaded_resumes_career = st.file_uploader(
            t('upload_resume'),
            type=['txt', 'md', 'pdf', 'docx'],
            accept_multiple_files=True,
            key="career_resume"
        )
        resume_text_career = st.text_area(
            t('paste_resume'),
            height=200,
            key="career_resume_text"
        )

        # Show parsed preview for resume
        if uploaded_resumes_career:
            for uf in uploaded_resumes_career:
                content, preview = parse_and_preview_file(uf)
                if content:
                    with st.expander(f"📄 已解析: {uf.name}", expanded=False):
                        st.text_area("提取的文本内容", preview, height=150, disabled=True, key=f"preview_resume_{uf.name}")
                else:
                    st.error(preview)

    with col2:
        st.markdown(f"**{t('jd_label')}**")
        uploaded_jds_career = st.file_uploader(
            t('upload_jd'),
            type=['txt', 'md', 'pdf', 'docx'],
            accept_multiple_files=True,
            key="career_jd"
        )
        jd_text_career = st.text_area(
            t('paste_jd'),
            height=200,
            key="career_jd_text"
        )

        # Show parsed preview for JD
        if uploaded_jds_career:
            for uf in uploaded_jds_career:
                content, preview = parse_and_preview_file(uf)
                if content:
                    with st.expander(f"📄 已解析: {uf.name}", expanded=False):
                        st.text_area("提取的文本内容", preview, height=150, disabled=True, key=f"preview_jd_{uf.name}")
                else:
                    st.error(preview)

    if st.button(t('btn_analyze'), type="primary", use_container_width=True):
        if 'engine' not in st.session_state:
            st.error(t('engine_error'))
        else:
            resume_list = get_content_list(uploaded_resumes_career, resume_text_career, "Resume")
            jd_list = get_content_list(uploaded_jds_career, jd_text_career, "JD")

            if not resume_list:
                st.error(t('no_resume'))
            elif not jd_list:
                st.error(t('no_jd'))
            else:
                engine = st.session_state.engine

                # Single Mode
                if len(resume_list) == 1 and len(jd_list) == 1:
                    st.info(t('processing_audit'))
                    try:
                        result = engine.analyze(
                            resume_text=resume_list[0]['content'],
                            jd_text=jd_list[0]['content'],
                            persona=persona_key,
                            use_cache=use_cache,
                            model=model
                        )
                        st.success(t('audit_complete'))

                        # Score and Radar Chart in columns
                        col_score, col_radar = st.columns([1, 2])

                        with col_score:
                            if result.score is not None:
                                color = get_score_color(result.score)
                                st.markdown(f'<h1 style="color:{color}">匹配度: {result.score}/100</h1>', unsafe_allow_html=True)

                        with col_radar:
                            radar_data = extract_radar_data(result.report)
                            if radar_data:
                                fig = render_radar_chart(radar_data)
                                if fig:
                                    st.plotly_chart(fig, use_container_width=True)

                        # Report
                        with st.expander("📄 查看完整报告", expanded=True):
                            st.markdown(result.report)

                    except Exception as e:
                        st.error(f"分析失败: {e}")

                # Batch Mode (Resume vs 1 JD)
                elif len(resume_list) > 1 and len(jd_list) == 1:
                    st.info(f"正在批量分析 {len(resume_list)} 份简历...")
                    target_jd = jd_list[0]['content']
                    results = []

                    progress_bar = st.progress(0)
                    for i, res in enumerate(resume_list):
                        try:
                            result = engine.analyze(
                                resume_text=res['content'],
                                jd_text=target_jd,
                                persona=persona_key,
                                use_cache=use_cache,
                                model=model
                            )
                            score = extract_score(result.report)
                            results.append({
                                "Name": res['name'],
                                "Score": score if score else 0,
                                "Report": result.report
                            })
                        except Exception as e:
                            results.append({"Name": res['name'], "Score": 0, "Report": str(e)})
                        progress_bar.progress((i + 1) / len(resume_list))

                    df = pd.DataFrame(results).sort_values(by="Score", ascending=False)
                    st.dataframe(df)
                    st.download_button("📥 下载CSV", df.to_csv().encode('utf-8'), "results.csv")

# --- Tab 2: Diagnostic (深度诊断) ---
with tab_diag:
    st.markdown("""
    **🔍 深度诊断：我是谁？我值多少钱？**

    不看JD，只看你的简历，挖掘你可能没意识到的隐性价值。
    """)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown(f"**{t('resume_label')}**")
        uploaded_resumes_diag = st.file_uploader(
            t('upload_resume'),
            type=['txt', 'md', 'pdf', 'docx'],
            accept_multiple_files=True,
            key="diag_resume"
        )
        resume_text_diag = st.text_area(
            t('paste_resume'),
            height=200,
            key="diag_text"
        )

        # Show parsed preview for diagnostic resume
        if uploaded_resumes_diag:
            for uf in uploaded_resumes_diag:
                content, preview = parse_and_preview_file(uf)
                if content:
                    with st.expander(f"📄 已解析: {uf.name}", expanded=False):
                        st.text_area("提取的文本内容", preview, height=150, disabled=True, key=f"preview_diag_{uf.name}")
                else:
                    st.error(preview)

    if st.button(t('btn_diagnostic'), type="primary", use_container_width=True):
        if 'engine' not in st.session_state:
            st.error(t('engine_error'))
        else:
            resume_list = get_content_list(uploaded_resumes_diag, resume_text_diag, "Resume")

            if not resume_list:
                st.error(t('no_resume'))
            else:
                st.info(t('processing_diag'))

                for res in resume_list:
                    try:
                        with st.spinner(f"分析中..."):
                            result = st.session_state.engine.diagnose_resume(
                                resume_text=res['content'],
                                persona="hrbp",
                                use_cache=use_cache,
                                model=model
                            )

                        st.success(t('diag_complete'))
                        with st.expander("📄 查看深度诊断报告", expanded=True):
                            st.markdown(result.report)

                    except Exception as e:
                        st.error(f"分析失败: {e}")

# --- Tab 3: Side Hustle (副业变现) ---
with tab_hustle:
    st.markdown("""
    **🚀 副业变现：把你的技能变成产品**

    输入你能提供的产品/服务，生成一份老板无法拒绝的JD。
    """)
    st.info(t('btn_hustle'))

# --- Tab 4: Headhunter Mode (猎头模式) ---
with tab_headhunter:
    st.markdown("""
    **💰 猎头模式：批量生成候选人推荐报告**
    
    专为 B 端猎头/HR 设计。上传 JD 和多个候选人简历，一键生成发送给 Hiring Manager 的推荐语 (Presentation Note)。
    """)
    
    col_jd_hh, col_res_hh = st.columns([1, 1])
    
    with col_jd_hh:
        st.markdown("**1. 目标职位 (Target JD)**")
        uploaded_jd_hh = st.file_uploader(
            "上传 JD (支持多文件合并)",
            type=['txt', 'md', 'pdf', 'docx'],
            accept_multiple_files=True,
            key="hh_jd_files"
        )
        jd_text_hh = st.text_area(
            "或粘贴 JD 内容",
            height=200,
            key="hh_jd_text"
        )

    with col_res_hh:
        st.markdown("**2. 候选人简历 (Batch Upload)**")
        uploaded_resumes_hh = st.file_uploader(
            "批量上传简历 (PDF/Word)",
            type=['txt', 'md', 'pdf', 'docx'],
            accept_multiple_files=True,
            key="hh_resumes"
        )
        # No text paste for batch mode to encourage file workflow

    if st.button(t('btn_headhunter'), type="primary", use_container_width=True):
        if 'engine' not in st.session_state:
            st.error(t('engine_error'))
        else:
            # Prepare JD
            jd_list = get_content_list(uploaded_jd_hh, jd_text_hh, "JD")
            if not jd_list:
                st.error("请提供 JD！")
            else:
                final_jd = "\n\n".join([j['content'] for j in jd_list])
                
                # Prepare Resumes
                resume_list = get_content_list(uploaded_resumes_hh, "", "Resume")
                
                if not resume_list:
                    st.error("请至少上传一份简历！")
                else:
                    st.info(f"正在分析 {len(resume_list)} 位候选人... (使用 Persona: Headhunter)")
                    
                    # Force Headhunter Persona
                    engine = st.session_state.engine
                    
                    progress_bar = st.progress(0)
                    
                    for i, res in enumerate(resume_list):
                        with st.expander(f"👤 候选人: {res.get('filename', f'Candidate {i+1}')}", expanded=True):
                            try:
                                result = engine.analyze(
                                    resume_text=res['content'],
                                    jd_text=final_jd,
                                    persona="headhunter", # Force this
                                    use_cache=use_cache,
                                    model=model
                                )
                                
                                # Display Score
                                if result.score is not None:
                                    color = get_score_color(result.score)
                                    st.markdown(f"### 推荐指数: <span style='color:{color}'>{result.score}/100</span>", unsafe_allow_html=True)
                                
                                st.markdown(result.report)
                                
                            except Exception as e:
                                st.error(f"分析失败: {e}")
                        
                        progress_bar.progress((i + 1) / len(resume_list))
                    
                    st.success("✅ 批量分析完成！")


# Footer
st.markdown("---")
st.caption(f"⚡ {t('footer')}")
