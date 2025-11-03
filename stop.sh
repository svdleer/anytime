#!/bin/bash
# Stop the background Sportivity booking service

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║      Sportivity Auto-Booking - Stop Background Service    ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

if [ ! -f sportivity.pid ]; then
    echo "❌ No PID file found. Service may not be running."
    echo ""
    echo "To check manually:"
    echo "   ps aux | grep 'python3 main.py'"
    exit 1
fi

PID=$(cat sportivity.pid)

if ps -p $PID > /dev/null 2>&1; then
    echo "Stopping service (PID: $PID)..."
    kill $PID
    sleep 2
    
    # Check if still running
    if ps -p $PID > /dev/null 2>&1; then
        echo "Process still running, forcing kill..."
        kill -9 $PID
    fi
    
    rm -f sportivity.pid
    echo "✅ Service stopped successfully!"
else
    echo "⚠️  Process not running (PID: $PID)"
    rm -f sportivity.pid
fi

echo ""
