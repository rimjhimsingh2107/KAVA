#!/bin/bash
# Shows whether the backend and frontend are running

check() {
    if lsof -Pi :$2 -sTCP:LISTEN -t >/dev/null; then
        echo "$1 is running on port $2 (PID $(lsof -ti:$2))"
    else
        echo "$1 is not running"
    fi
}

check "Backend" 8000
check "Frontend" 3001
