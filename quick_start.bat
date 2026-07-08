
@echo off
REM Quick Start Script - Starts Both Backend and Frontend

echo.
echo ============================================================
echo   Nifty 50 RL Trading Model + Dashboard - Quick Start
echo ============================================================
echo.

REM Change to project directory
cd /d "%~dp0"

REM Check if venv exists
if not exist ".venv" (
    echo ERROR: Virtual environment not found!
    echo Please create it first:
    echo   python -m venv .venv
    echo   .venv\Scripts\Activate.ps1
    pause
    exit /b 1
)

REM Activate venv
call .venv\Scripts\Activate.ps1

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in virtual environment
    pause
    exit /b 1
)

REM Install backend dependencies
echo.
echo Installing backend dependencies...
pip install -q fastapi uvicorn python-multipart

echo.
echo ============================================================
echo Starting servers...
echo ============================================================
echo.
echo IMPORTANT: Keep this window open!
echo.
echo Backend API will start on:   http://localhost:8000
echo API Docs will be available at: http://localhost:8000/docs
echo.
echo Frontend will start separately on: http://localhost:5173
echo.
echo Press any key to continue...
pause

REM Start backend in background using START command
echo Starting Backend API Server...
start "Nifty50 Backend API" cmd /k python -m uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload

REM Wait a moment for backend to start
timeout /t 3 /nobreak

REM Navigate to frontend
cd trade-signal-dashboard-main

REM Check if node_modules exists
if not exist "node_modules" (
    echo.
    echo Installing frontend dependencies (this may take a minute)...
    call npm install -q
)

REM Start frontend
echo.
echo Starting Frontend Development Server...
echo.
call npm run dev

pause
