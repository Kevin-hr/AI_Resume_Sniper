@echo off
chcp 65001 > nul
echo ===================================================
echo   AI Resume Sniper - Recruiter Edition (B-Side)
echo ===================================================
echo.
echo [INFO] Starting Local Privacy-First Server...
echo [INFO] Your data stays on your machine (except for API calls).
echo.

:: Check for python
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed. Please install Python 3.10+.
    pause
    exit /b
)

:: Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment...
    call .venv\Scripts\activate.bat
)

:: Run Streamlit
echo [INFO] Launching Web Interface...
streamlit run src/web_ui.py

pause
