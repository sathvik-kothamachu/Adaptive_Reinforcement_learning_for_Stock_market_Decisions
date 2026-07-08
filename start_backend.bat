@echo off
REM Start the Python FastAPI backend server
REM Make sure you have activated the virtual environment first

echo.
echo ========================================
echo Starting Nifty 50 PPO Backend API Server
echo ========================================
echo.

REM Check if venv is activated
if not defined VIRTUAL_ENV (
    echo ERROR: Virtual environment is not activated!
    echo Please run: .venv\Scripts\Activate.ps1
    pause
    exit /b 1
)

REM Install required packages if needed
echo Installing/verifying dependencies...
pip install fastapi uvicorn python-multipart -q

REM Start the server
echo.
echo Starting FastAPI server on http://localhost:8000
echo.
python -m uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload

pause
