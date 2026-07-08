@echo off
REM Start the frontend React/Vite development server

echo.
echo ========================================
echo Starting Nifty 50 Dashboard Frontend
echo ========================================
echo.

cd /d "%~dp0\trade-signal-dashboard-main"

REM Check if node_modules exists
if not exist "node_modules" (
    echo Installing dependencies...
    call npm install
)

echo.
echo Starting Vite development server...
echo The dashboard will open at http://localhost:5173
echo.
call npm run dev

pause
