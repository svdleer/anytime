#!/bin/bash
# Check status of the Sportivity booking service

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║     Sportivity Auto-Booking - Service Status             ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

if [ -f sportivity.pid ]; then
    PID=$(cat sportivity.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "✅ Service is RUNNING"
        echo ""
        echo "   PID: $PID"
        echo "   Started: $(ps -p $PID -o lstart=)"
        echo "   CPU/Mem: $(ps -p $PID -o %cpu,%mem | tail -1)"
        echo ""
        
        # Check DRY_RUN
        if grep -q "DRY_RUN=false" .env 2>/dev/null; then
            echo "   Mode: 🔴 LIVE BOOKINGS"
        else
            echo "   Mode: 🟢 DRY-RUN (test mode)"
        fi
        echo ""
        
        # Show last log entries
        echo "📝 Last 5 log entries:"
        echo "─────────────────────────────────────────────────────────"
        tail -5 anytime_booking.log 2>/dev/null || echo "   No log file found"
        echo ""
        
        echo "Commands:"
        echo "   Stop:    ./stop.sh"
        echo "   Restart: ./stop.sh && ./run-background.sh"
        echo "   Logs:    tail -f anytime_booking.log"
    else
        echo "❌ Service is NOT running (stale PID file)"
        echo ""
        echo "   Removing stale PID: $PID"
        rm -f sportivity.pid
        echo ""
        echo "To start: ./run-background.sh"
    fi
else
    echo "❌ Service is NOT running"
    echo ""
    echo "To start: ./run-background.sh"
    echo ""
    
    # Check if process is running without PID file
    if pgrep -f "python3 main.py" > /dev/null; then
        echo "⚠️  Warning: Found orphaned process:"
        ps aux | grep "python3 main.py" | grep -v grep
        echo ""
        echo "To kill: pkill -f 'python3 main.py'"
    fi
fi

echo ""
