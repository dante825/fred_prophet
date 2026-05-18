#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$SCRIPT_DIR/.streamlit.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "fred_prophet is not running (no PID file found)"
    exit 0
fi

PID=$(cat "$PID_FILE")

if kill -0 "$PID" 2>/dev/null; then
    kill "$PID"
    rm "$PID_FILE"
    echo "fred_prophet stopped (PID $PID)"
else
    echo "fred_prophet was not running (stale PID $PID)"
    rm "$PID_FILE"
fi
