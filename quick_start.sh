#!/bin/bash

# Quick Start Script - Starts Both Backend and Frontend

echo ""
echo "============================================================"
echo "  Nifty 50 RL Trading Model + Dashboard - Quick Start"
echo "============================================================"
echo ""

# Change to project directory
cd "$(dirname "$0")"

# Check if venv exists
if [ ! -d ".venv" ]; then
    echo "ERROR: Virtual environment not found!"
    echo "Please create it first:"
    echo "  python -m venv .venv"
    echo "  source .venv/bin/activate"
    exit 1
fi

# Activate venv
source .venv/bin/activate

# Check Python
if ! command -v python &> /dev/null; then
    echo "ERROR: Python not found in virtual environment"
    exit 1
fi

# Install backend dependencies
echo ""
echo "Installing backend dependencies..."
pip install -q fastapi uvicorn python-multipart

echo ""
echo "============================================================"
echo "Starting servers..."
echo "============================================================"
echo ""
echo "IMPORTANT: Keep this window open!"
echo ""
echo "Backend API will start on:   http://localhost:8000"
echo "API Docs will be available at: http://localhost:8000/docs"
echo ""
echo "Frontend will start separately on: http://localhost:5173"
echo ""
echo "Press Enter to continue..."
read

# Start backend in background
echo "Starting Backend API Server..."
python -m uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Navigate to frontend
cd trade-signal-dashboard-main

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo ""
    echo "Installing frontend dependencies (this may take a minute)..."
    npm install
fi

# Start frontend
echo ""
echo "Starting Frontend Development Server..."
echo ""
npm run dev

# On exit, kill backend
trap "kill $BACKEND_PID" EXIT
