#!/bin/bash
# Quick server startup test

echo "🧪 Testing server startup with unified config..."
echo ""

timeout 10 make run-server 2>&1 | head -50 &
PID=$!

sleep 8
kill $PID 2>/dev/null

echo ""
echo "✅ If you saw 'Application startup complete' above, configuration works!"
echo "ℹ️  Now start server normally with: make run-server"
