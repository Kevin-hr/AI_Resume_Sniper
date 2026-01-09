@echo off
chcp 65001 > nul
setlocal

echo [1/3] Cleaning up environment...
taskkill /F /IM cloudflared.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM uvicorn.exe >nul 2>&1

echo [2/3] Configuring Tunnel...
powershell -ExecutionPolicy Bypass -File ".\setup_tunnel.ps1"

echo [3/3] Launching services...
if exist ".venv\Scripts\activate.bat" (
    start "API" cmd /c "call .venv\Scripts\activate.bat && python -m uvicorn src.api_server:app --host 127.0.0.1 --port 8000"
) else (
    start "API" cmd /c "python -m uvicorn src.api_server:app --host 127.0.0.1 --port 8000"
)

start "Web" cmd /c "cd frontend-web && pnpm dev"
start "Tunnel" cmd /c "cloudflared tunnel --config tunnel_config.yml run resume-sniper"

start "" "https://bmwuv.com"

exit /b 0
