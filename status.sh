#!/bin/bash

# KAVA Status Checker
# Check if backend and frontend are running

echo "🔍 Checking KAVA System Status..."
echo ""

# Check backend (port 8000)
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "✅ Backend is RUNNING on port 8000"
    BACKEND_PID=$(lsof -ti:8000)
    echo "   PID: $BACKEND_PID"
else
    echo "❌ Backend is NOT running on port 8000"
fi

echo ""

# Check frontend (port 3001)
if lsof -Pi :3001 -sTCP:LISTEN -t >/dev/null ; then
    echo "✅ Frontend is RUNNING on port 3001"
    FRONTEND_PID=$(lsof -ti:3001)
    echo "   PID: $FRONTEND_PID"
else
    echo "❌ Frontend is NOT running on port 3001"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if both are running
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null && lsof -Pi :3001 -sTCP:LISTEN -t >/dev/null ; then
    echo "✨ KAVA is fully operational!"
    echo "🌐 Access at: http://localhost:3001"
else
    echo "⚠️  KAVA is not fully running"
    echo "💡 Run: ./start.sh to start the system"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
