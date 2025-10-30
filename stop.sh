#!/bin/bash

# KAVA Project Shutdown Script
# This script stops both backend and frontend servers

echo "🛑 Stopping KAVA Insurance Claims Validation System..."
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Read PIDs from file
if [ -f "$SCRIPT_DIR/.backend_pid" ]; then
    BACKEND_PID=$(cat "$SCRIPT_DIR/.backend_pid")
    echo "📦 Stopping Backend (PID: $BACKEND_PID)..."
    kill $BACKEND_PID 2>/dev/null
    rm "$SCRIPT_DIR/.backend_pid"
    echo "✅ Backend stopped"
else
    echo "⚠️  No backend PID file found"
fi

if [ -f "$SCRIPT_DIR/.frontend_pid" ]; then
    FRONTEND_PID=$(cat "$SCRIPT_DIR/.frontend_pid")
    echo "🎨 Stopping Frontend (PID: $FRONTEND_PID)..."
    kill $FRONTEND_PID 2>/dev/null
    rm "$SCRIPT_DIR/.frontend_pid"
    echo "✅ Frontend stopped"
else
    echo "⚠️  No frontend PID file found"
fi

# Also kill any processes on the ports just to be safe
echo ""
echo "🧹 Cleaning up ports..."
lsof -ti:8000 | xargs kill -9 2>/dev/null && echo "✅ Port 8000 cleaned" || echo "✓ Port 8000 already free"
lsof -ti:3001 | xargs kill -9 2>/dev/null && echo "✅ Port 3001 cleaned" || echo "✓ Port 3001 already free"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ KAVA has been stopped successfully!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
