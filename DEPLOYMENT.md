# 🚀 Deployment Guide - Running Hetty 24/7

## Overview

Multiple options to keep Sportivity Auto-Booking (Hetty) running continuously.

---

## ⚡ Quick Start (Simple Background)

**Best for:** Quick testing, temporary deployment

```bash
# Start in background
./run-background.sh

# Check status
./status.sh

# View logs
tail -f anytime_booking.log

# Stop
./stop.sh
```

### Pros & Cons
✅ Simple, no root required  
✅ Works on any Linux/macOS  
❌ Stops when you logout (unless in tmux/screen)  
❌ No auto-restart on crash  

---

## 🔧 Option 1: Linux systemd Service (Recommended for VPS)

**Best for:** Production Linux VPS deployment

### Setup

```bash
# On your VPS (as sportivity user)
cd ~/anytime
./setup-service-linux.sh
```

### Usage

```bash
# Start service
sudo systemctl start sportivity-booking

# Enable auto-start on boot
sudo systemctl enable sportivity-booking

# Check status
sudo systemctl status sportivity-booking

# View logs
journalctl -u sportivity-booking -f
# OR
tail -f ~/anytime/anytime_booking.log

# Stop service
sudo systemctl stop sportivity-booking

# Restart service
sudo systemctl restart sportivity-booking
```

### Pros
✅ Automatic restart on crash  
✅ Starts on system boot  
✅ Proper service management  
✅ Systemd logging integration  

---

## 🖥️ Option 2: tmux/screen (Simple Persistent Session)

**Best for:** Development, testing, manual control

### Using tmux

```bash
# Install tmux (if needed)
sudo apt install tmux  # Debian/Ubuntu
# or
sudo yum install tmux  # CentOS/RHEL

# Start tmux session
tmux new -s hetty

# Inside tmux, start the booking system
cd ~/anytime
python3 main.py

# Detach from session: Press Ctrl+B then D

# Re-attach later
tmux attach -t hetty

# List sessions
tmux ls
```

### Using screen

```bash
# Start screen session
screen -S hetty

# Start booking system
cd ~/anytime
python3 main.py

# Detach: Press Ctrl+A then D

# Re-attach
screen -r hetty
```

---

## 📦 Option 3: Docker Container

**Best for:** Containerized environments, Kubernetes

```bash
# Create Dockerfile (already provided)
docker build -t sportivity-hetty .

# Run container
docker run -d \
  --name hetty \
  --restart unless-stopped \
  -v $(pwd)/.env:/app/.env \
  -v $(pwd)/anytime_booking.log:/app/anytime_booking.log \
  sportivity-hetty

# View logs
docker logs -f hetty

# Stop
docker stop hetty

# Start
docker start hetty
```

---

## 🍎 Option 4: macOS launchd (For Mac)

**Best for:** Running on your Mac laptop

### Setup

1. Edit the plist file with your paths:
```bash
# The plist file is at: ~/Library/LaunchAgents/com.sportivity.booking.plist
# Update paths in the plist to match your installation
```

2. Load the service:
```bash
launchctl load ~/Library/LaunchAgents/com.sportivity.booking.plist
```

3. Start the service:
```bash
launchctl start com.sportivity.booking
```

### Usage

```bash
# Check if running
launchctl list | grep sportivity

# View logs
tail -f ~/anytime/anytime_booking.log

# Stop
launchctl stop com.sportivity.booking

# Unload (disable)
launchctl unload ~/Library/LaunchAgents/com.sportivity.booking.plist
```

---

## 🔥 Option 5: PM2 Process Manager

**Best for:** Node.js-like process management

```bash
# Install PM2
npm install -g pm2

# Start with PM2
pm2 start main.py --name hetty --interpreter python3

# Save PM2 process list
pm2 save

# Enable startup on boot
pm2 startup

# Monitor
pm2 monit

# Logs
pm2 logs hetty

# Stop
pm2 stop hetty

# Restart
pm2 restart hetty
```

---

## 📋 Comparison Table

| Method | Auto-restart | Boot startup | Complexity | Best for |
|--------|--------------|--------------|------------|----------|
| **run-background.sh** | ❌ | ❌ | ⭐ | Testing |
| **systemd** | ✅ | ✅ | ⭐⭐ | Production VPS |
| **tmux/screen** | ❌ | ❌ | ⭐ | Manual control |
| **Docker** | ✅ | ✅ | ⭐⭐⭐ | Containers |
| **launchd** | ✅ | ✅ | ⭐⭐ | macOS |
| **PM2** | ✅ | ✅ | ⭐⭐ | Node.js users |

---

## 🎯 Recommended Deployment Strategy

### For Your VPS (sportivity.useless.nl)

**Recommended:** systemd service

```bash
ssh sportivity@sportivity.useless.nl
cd ~/anytime
./setup-service-linux.sh
sudo systemctl start sportivity-booking
sudo systemctl enable sportivity-booking
```

**Why:** 
- Automatic restart on failure
- Starts on system boot
- Proper logging
- Professional service management

---

## 🔍 Monitoring & Troubleshooting

### Check if Running

```bash
# Using status script
./status.sh

# OR manually
ps aux | grep "python3 main.py"

# Check systemd (if using service)
sudo systemctl status sportivity-booking
```

### View Logs

```bash
# File logs (all methods)
tail -f anytime_booking.log

# systemd logs
journalctl -u sportivity-booking -f

# Last 100 lines
tail -100 anytime_booking.log

# Search for errors
grep ERROR anytime_booking.log

# Search for bookings
grep "Booked:" anytime_booking.log
```

### Restart if Hung

```bash
# Quick method
./stop.sh && ./run-background.sh

# systemd
sudo systemctl restart sportivity-booking

# Force kill if needed
pkill -f "python3 main.py"
```

---

## 📧 Email Notifications

Hetty will email you at `silvester@vdleer.nl` when:
- ✅ Lesson successfully booked
- ⏳ Lesson is full (retry notification after 2+ attempts)

Make sure email is working:
```bash
python3 test_email.py
```

---

## 🛡️ Security Notes

- ✅ `.env` file contains credentials (not in git)
- ✅ Token encrypted with AES-256
- ✅ Service runs as non-root user
- ✅ Logs are local only

---

## 📝 Quick Reference

```bash
# Start background (simple)
./run-background.sh

# Check status
./status.sh

# View logs
tail -f anytime_booking.log

# Stop
./stop.sh

# Systemd (production)
sudo systemctl start sportivity-booking
sudo systemctl status sportivity-booking
journalctl -u sportivity-booking -f
```

---

## 🆘 Help

**Service won't start?**
- Check Python3 installed: `python3 --version`
- Check dependencies: `pip3 install -r requirements.txt`
- Check .env exists and has credentials
- Check logs: `tail -50 anytime_booking.log`

**No bookings happening?**
- Verify DRY_RUN=false in .env
- Check booking window: lessons book 48h before start
- Check logs for "Found X lessons ready for booking"
- Run test: `python3 test_booking.py`

**Email not working?**
- Test: `python3 test_email.py`
- Check SMTP credentials in .env
- Verify EMAIL_SMTP_PASSWORD is correct

---

**Happy booking! 🎉 Hetty is at your service!**
