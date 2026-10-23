#!/bin/bash
# Starts the backend (port 8000) and frontend (port 3001). Run ./stop.sh to stop them.

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd "$SCRIPT_DIR/backend"
source venv/bin/activate
python -m uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

sleep 3

cd "$SCRIPT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!

echo "$BACKEND_PID" > "$SCRIPT_DIR/.backend_pid"
echo "$FRONTEND_PID" > "$SCRIPT_DIR/.frontend_pid"

echo ""
echo "Frontend: http://localhost:3001"
echo "Backend:  http://localhost:8000"
echo ""

wait
