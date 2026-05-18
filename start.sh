#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$SCRIPT_DIR/.streamlit.pid"

if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
    echo "fred_prophet is already running (PID $(cat "$PID_FILE"))"
    echo "Open: http://localhost:8501"
    exit 0
fi

cd "$SCRIPT_DIR"
nohup .venv/bin/streamlit run ui/app.py > .streamlit/app.log 2>&1 &
echo $! > "$PID_FILE"

echo "fred_prophet started (PID $!)"
echo "Open: http://localhost:8501"
echo "Logs: $SCRIPT_DIR/.streamlit/app.log"
