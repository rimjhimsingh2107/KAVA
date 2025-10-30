#!/bin/bash

# KAVA Project Startup Script
# This script starts both backend and frontend servers

echo "🚀 Starting KAVA Insurance Claims Validation System..."
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Start backend in background
echo "📦 Starting Backend (FastAPI on port 8000)..."
cd "$SCRIPT_DIR/backend"
source venv/bin/activate
python -m uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"
echo ""

# Wait for backend to be ready
echo "⏳ Waiting for backend to initialize..."
sleep 3

# Start frontend in background
echo "🎨 Starting Frontend (Next.js on port 3001)..."
cd "$SCRIPT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: $FRONTEND_PID)"
echo ""

# Save PIDs to file for easy shutdown
echo "$BACKEND_PID" > "$SCRIPT_DIR/.backend_pid"
echo "$FRONTEND_PID" > "$SCRIPT_DIR/.frontend_pid"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ KAVA is now running!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Frontend: http://localhost:3001"
echo "🔌 Backend:  http://localhost:8000"
echo ""
echo "📝 Logs:"
echo "   Backend PID: $BACKEND_PID"
echo "   Frontend PID: $FRONTEND_PID"
echo ""
echo "⚠️  To stop the servers, run: ./stop.sh"
echo "   Or press Ctrl+C in this terminal"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Keep script running and wait for Ctrl+C
wait
