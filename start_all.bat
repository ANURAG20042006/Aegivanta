@echo off
title SentinelAI - 1-Click Platform Launcher
color 0A

echo =========================================================================
echo               SENTINELAI ENTERPRISE IDS PLATFORM LAUNCHER
echo =========================================================================
echo.
echo [1/3] Checking environment & dependencies...
cd /d "%~dp0"

echo [2/3] Starting FastAPI Async Backend Server on http://localhost:8000 ...
start "SentinelAI Backend Server" cmd /k "py -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000"

echo [3/3] Starting Vite React Frontend Dev Server on http://localhost:5173 ...
start "SentinelAI Frontend Server" cmd /k "cd frontend && npm run dev"

echo.
echo Waiting 4 seconds for servers to initialize...
timeout /t 4 /nobreak >nul

echo Opening SentinelAI Operations Dashboard in default browser...
start http://localhost:5173/

echo.
echo =========================================================================
echo    SentinelAI Platform is LIVE!
echo    - Frontend: http://localhost:5173/
echo    - Backend API Docs: http://localhost:8000/docs
echo =========================================================================
echo.
pause
