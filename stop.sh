#!/bin/bash
# Stops the servers started by start.sh

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

for name in backend frontend; do
    PID_FILE="$SCRIPT_DIR/.${name}_pid"
    if [ -f "$PID_FILE" ]; then
        kill "$(cat "$PID_FILE")" 2>/dev/null
        rm "$PID_FILE"
        echo "Stopped $name"
    fi
done

# in case anything is still holding the ports
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:3001 | xargs kill -9 2>/dev/null
