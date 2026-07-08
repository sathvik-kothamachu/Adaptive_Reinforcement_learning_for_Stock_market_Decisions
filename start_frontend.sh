#!/bin/bash

# Start the frontend React/Vite development server

echo ""
echo "========================================"
echo "Starting Nifty 50 Dashboard Frontend"
echo "========================================"
echo ""

cd "$(dirname "$0")/trade-signal-dashboard-main"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

echo ""
echo "Starting Vite development server..."
echo "The dashboard will open at http://localhost:5173"
echo ""
npm run dev
