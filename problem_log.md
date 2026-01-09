# 问题日志 / Problem Log

## 2026-01-07: Streamlit `NameError: name 'st' is not defined`

### 问题描述
用户报告在运行 `streamlit run src/web_ui.py` 时出现以下错误：
```
File "src/web_ui.py", line 3, in <module>
    st.markdown("### 🎯 选择你的需求")
NameError: name 'st' is not defined
```

### 原因分析 (Root Cause)
1.  **误用工具**: 我使用了 `Write` 工具来修改文件的一部分，但 `Write` 工具的行为是**覆盖整个文件**。
2.  **代码丢失**: 这一操作导致 `src/web_ui.py` 中的所有 `import` 语句（如 `import streamlit as st`）和初始化代码被删除，只保留了最后写入的那段 UI 逻辑代码。
3.  **执行失败**: 当 Streamlit 尝试运行该文件时，由于缺少 `st` 对象的定义（因为它是在被删除的 import 语句中定义的），导致程序崩溃。

### 解决方案 (Solution)
1.  **恢复文件**: 重新构建 `src/web_ui.py`，确保包含完整的头部引用 (`imports`)、配置初始化 (`set_page_config`)、辅助函数 (`helper functions`) 以及完整的 UI 逻辑。
2.  **正确修改**: 在未来修改文件时，如果只是修改部分内容，**必须**使用 `SearchReplace` 工具，或者先读取完整文件内容，在内存中修改后再使用 `Write` 写入完整内容。

### 预防措施
*   **工具使用原则**: 修改现有文件时，优先使用 `SearchReplace`。
*   **全量写入原则**: 如果必须使用 `Write`，必须确保写入的是**完整**的可运行文件内容，而不仅仅是片段。

## 2026-01-08: Strategic Pivot (C-Side to B-Side)

### 问题描述 (Critique)
User pointed out fatal flaws in the C-side manual service model:
1.  **Platform Risk**: Comment sniping leads to immediate bans.
2.  **Privacy Trust**: Users distrust manual handling of data more than SaaS.
3.  **Unit Economics**: Manual processing yields negative ROI compared to low-skill labor.

### 解决方案 (Pivot)
1.  **Pivot to B-Side**: Target Headhunters/Recruiters instead of Candidates.
2.  **New Persona**: Added `headhunter` persona to generate "Candidate Presentation Notes" for Hiring Managers.
3.  **Batch Processing**: Updated UI to support batch resume upload and analysis against a single JD.
4.  **Local Deployment**: Created `run_for_recruiters.bat` to emphasize privacy (tool runs locally).
