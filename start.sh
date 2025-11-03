#!/bin/bash
# Quick start script for Sportivity Auto-Booking

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║     Sportivity Auto-Booking System - Quick Start         ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: Please run this script from the anytime directory"
    exit 1
fi

echo "📋 Running System Tests..."
echo ""

echo "1️⃣  Testing Login..."
python3 test_login.py
if [ $? -ne 0 ]; then
    echo "❌ Login test failed. Please check your credentials in .env"
    exit 1
fi
echo ""

echo "2️⃣  Testing Schedule API..."
python3 test_schedule.py | tail -5
if [ $? -ne 0 ]; then
    echo "❌ Schedule test failed"
    exit 1
fi
echo ""

echo "3️⃣  Testing Booking Logic (Dry-Run)..."
python3 test_booking.py | tail -3
if [ $? -ne 0 ]; then
    echo "❌ Booking test failed"
    exit 1
fi
echo ""

echo "✅ All tests passed!"
echo ""

# Check DRY_RUN status
if grep -q "DRY_RUN=false" .env; then
    echo "⚠️  WARNING: DRY_RUN is disabled - Real bookings will be made!"
    echo ""
    read -p "   Continue with real bookings? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "❌ Aborted"
        exit 1
    fi
else
    echo "ℹ️  DRY_RUN is enabled - No real bookings will be made"
    echo "   To enable real bookings, edit .env and set: DRY_RUN=false"
    echo ""
fi

echo "🚀 Starting Sportivity Auto-Booking System..."
echo ""
echo "   Monitoring for:"
echo "   • Tuesday: BBB (19:00), Pilates (20:00)"
echo "   • Wednesday: Kick Fun (09:30), Pilates (10:30)"
echo "   • Friday: H.I.I.T. (09:30), Yoga (10:30)"
echo ""
echo "   Press Ctrl+C to stop"
echo ""
echo "   Logs: tail -f anytime_booking.log"
echo ""

python3 main.py
