#!/bin/bash
# Setup script for Linux systemd service

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║     Sportivity Auto-Booking - Service Setup (Linux)      ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo "❌ Don't run this script as root. Run as the sportivity user."
    exit 1
fi

echo "📋 Setting up systemd service..."
echo ""

# Get the current directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Update service file with correct paths
TEMP_SERVICE=$(mktemp)
sed "s|/home/sportivity/anytime|$SCRIPT_DIR|g" sportivity-booking.service > "$TEMP_SERVICE"
sed -i "s|User=sportivity|User=$USER|g" "$TEMP_SERVICE"

# Install the service
echo "Installing service to /etc/systemd/system/..."
sudo cp "$TEMP_SERVICE" /etc/systemd/system/sportivity-booking.service
rm "$TEMP_SERVICE"

# Reload systemd
echo "Reloading systemd..."
sudo systemctl daemon-reload

# Enable the service
echo "Enabling service to start on boot..."
sudo systemctl enable sportivity-booking.service

echo ""
echo "✅ Service installed successfully!"
echo ""
echo "📝 Available commands:"
echo ""
echo "  Start service:    sudo systemctl start sportivity-booking"
echo "  Stop service:     sudo systemctl stop sportivity-booking"
echo "  Restart service:  sudo systemctl restart sportivity-booking"
echo "  Check status:     sudo systemctl status sportivity-booking"
echo "  View logs:        journalctl -u sportivity-booking -f"
echo "  View file logs:   tail -f $SCRIPT_DIR/anytime_booking.log"
echo ""
echo "🚀 To start the service now:"
echo "   sudo systemctl start sportivity-booking"
echo ""
