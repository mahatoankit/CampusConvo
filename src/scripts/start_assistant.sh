#!/bin/bash

# Quick Start Script for CampusConvo Voice Assistant
# No API keys needed!

# Change to project root (script is in src/scripts/)
cd "$(dirname "$0")/../.." || exit 1

echo "============================================================"
echo "  CampusConvo Voice Assistant - Quick Start"
echo "============================================================"
echo ""

# Check if virtual environment exists
if [ ! -d "env" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Run: python3 -m venv env && source env/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source env/bin/activate

echo "✅ Virtual environment activated"
echo ""

# Check if server is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "⚠️  Server not detected on localhost:8000"
    echo ""
    echo "Starting server in background..."
    python src/scripts/run_server.py > /tmp/campusconvo_server.log 2>&1 &
    SERVER_PID=$!
    echo "   Server PID: $SERVER_PID"
    echo "   Logs: /tmp/campusconvo_server.log"
    echo ""
    echo "Waiting for server to start..."
    sleep 5
fi

echo "✅ Server is running"
echo ""

echo "============================================================"
echo "  Starting Voice Assistant (Simple Mode - No API Key)"
echo "============================================================"
echo ""
echo "Wake Word: 'Hello Zyra' or 'Hey Zyra'"
echo "Exit Command: 'Bye Zyra' or Ctrl+C"
echo ""
echo "Press Enter to start..."
read

python src/client.py
