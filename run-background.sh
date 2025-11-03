#!/bin/bash
# Run Sportivity booking system in background using nohup

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║   Sportivity Auto-Booking - Background Start (nohup)     ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Check if already running
if [ -f sportivity.pid ]; then
    PID=$(cat sportivity.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "⚠️  Service is already running (PID: $PID)"
        echo ""
        echo "To stop it: ./stop.sh"
        echo "To restart: ./stop.sh && ./run-background.sh"
        exit 1
    else
        echo "Removing stale PID file..."
        rm -f sportivity.pid
    fi
fi

# Check DRY_RUN status
if grep -q "DRY_RUN=false" .env 2>/dev/null; then
    echo "⚠️  DRY_RUN is DISABLED - Real bookings will be made!"
else
    echo "ℹ️  DRY_RUN is ENABLED - Test mode (no real bookings)"
fi
echo ""

# Start in background
echo "🚀 Starting in background..."
nohup python3 main.py >> anytime_booking.log 2>&1 &
PID=$!
echo $PID > sportivity.pid

echo "✅ Started successfully!"
echo ""
echo "   PID: $PID"
echo "   Log: $SCRIPT_DIR/anytime_booking.log"
echo ""
echo "📊 Monitor logs:"
echo "   tail -f anytime_booking.log"
echo ""
echo "🛑 Stop service:"
echo "   ./stop.sh"
echo ""
