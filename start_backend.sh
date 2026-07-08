#!/bin/bash

# Start the Python FastAPI backend server
# Make sure you have activated the virtual environment first

echo ""
echo "========================================"
echo "Starting Nifty 50 PPO Backend API Server"
echo "========================================"
echo ""

# Check if venv is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "ERROR: Virtual environment is not activated!"
    echo "Please run: source .venv/bin/activate"
    exit 1
fi

# Install required packages if needed
echo "Installing/verifying dependencies..."
pip install fastapi uvicorn python-multipart -q

# Start the server
echo ""
echo "Starting FastAPI server on http://localhost:8000"
echo ""
python -m uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
