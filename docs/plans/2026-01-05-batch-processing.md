# Plan: Batch Processing Features (批量处理功能)

## Goal
Iterate AI Resume Sniper to v1.2. Add batch processing capabilities:
1.  **Batch Resumes vs Single JD**: Upload multiple resumes (PDF/DOC/DOCX) to match against one JD.
2.  **Batch JDs vs Single Resume**: Upload multiple JDs (PDF/DOC/DOCX/TXT/MD) to match against one Resume.

## Architecture
-   **New Module**: `src/document_parser.py`
    -   Class `DocumentParser`
    -   Method `parse_file(file_path) -> str`
    -   Supports: `.pdf` (via `pdfplumber`), `.docx` (via `python-docx`), `.txt`, `.md`.
-   **Core Logic Update**: `src/resume_sniper.py`
    -   Enhance `analyze_match` to handle batch requests or create a wrapper `batch_analyze`.
-   **UI Update**: `src/web_ui.py`
    -   Add tabs for "Single Mode" (existing), "Batch Resumes", "Batch JDs".
    -   Use `st.file_uploader(accept_multiple_files=True)`.
    -   Display results in a table/dataframe.

## Tasks (Bite-Sized)

### 1. Document Parser Module
-   [ ] **Test**: Create `tests/test_document_parser.py`. Test parsing a dummy PDF, DOCX, and TXT.
-   [ ] **Impl**: Create `src/document_parser.py`. Implement `parse_pdf`, `parse_docx`, `parse_text`.
-   [ ] **Refactor**: Ensure clean error handling (return empty string or raise custom error on failure).

### 2. Core Logic - Batch Interface
-   [ ] **Test**: Create `tests/test_batch_logic.py`. Mock LLM calls. Test iterating over a list of inputs.
-   [ ] **Impl**: Update `src/resume_sniper.py` to accept text input directly (decoupling from file read logic if currently coupled) or ensure it handles pre-parsed text.
-   [ ] **Refactor**: Optimize for concurrent API calls if possible (optional for MVP, keep sequential for stability first).

### 3. Web UI - Batch Resumes Tab
-   [ ] **Impl**: Add "Batch Resumes" tab in `src/web_ui.py`.
-   [ ] **Impl**: Add file uploader for Resumes.
-   [ ] **Impl**: Add text area for JD.
-   [ ] **Impl**: Loop through uploaded files, parse using `DocumentParser`, call `ResumeSniper`.
-   [ ] **Impl**: Display results in `st.dataframe` or list of expanders.

### 4. Web UI - Batch JDs Tab
-   [ ] **Impl**: Add "Batch JDs" tab in `src/web_ui.py`.
-   [ ] **Impl**: Add file uploader for JDs.
-   [ ] **Impl**: Add text area for Resume.
-   [ ] **Impl**: Loop through JDs, parse, call `ResumeSniper`.
-   [ ] **Impl**: Display results.

### 5. Documentation & Cleanup
-   [ ] **Doc**: Update `README.md` with new features and usage.
-   [ ] **Test**: Run full integration test.

## Tech Stack Additions
-   `pdfplumber`
-   `python-docx`
