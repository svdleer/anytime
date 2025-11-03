# Sportivity Auto-Booking System - Complete Guide

## 🎯 What This Does

Automatically books your favorite Sportivity lessons exactly **48 hours** before they start, so you never miss a class!

## ✅ Current Status

### ✓ Working Components
- ✅ Login & Authentication (with encrypted token storage)
- ✅ Schedule fetching (7-day lookahead)
- ✅ Lesson filtering (your 6 weekly lessons)
- ✅ Booking status checking
- ✅ Dry-run mode (safe testing)
- ✅ iOS app headers (anti-detection)
- ✅ Automatic token refresh

### 📋 Your Weekly Schedule
The system will automatically book these lessons:

| Day | Lesson | Time |
|-----|--------|------|
| Tuesday | BBB (billen, buik, benen) | 19:00-20:00 |
| Tuesday | Pilates | 20:00-21:00 |
| Wednesday | Kick Fun | 09:30-10:30 |
| Wednesday | Pilates | 10:30-11:30 |
| Friday | H.I.I.T. | 09:30-10:30 |
| Friday | Yoga | 10:30-11:30 |

## 🚀 Quick Start

### 1. Test Everything (Safe - No Real Bookings)

```bash
cd /Users/silvester/PythonDev/Git/Anytime/anytime

# Test 1: Verify login works
python3 test_login.py

# Test 2: Verify schedule fetching
python3 test_schedule.py

# Test 3: Verify lesson details
python3 test_lesson_details.py

# Test 4: Dry-run booking (no real bookings)
python3 test_booking.py
```

All tests should pass with ✓ marks.

### 2. Enable Real Bookings

⚠️ **Only when you're ready!**

Edit `.env`:
```env
DRY_RUN=false
```

### 3. Run the System

```bash
python3 main.py
```

This will:
- Check for bookable lessons every 15 minutes
- Book lessons exactly 48 hours + 5 minutes before they start
- Skip already-booked lessons
- Log all activity to `anytime_booking.log`

### 4. Run as Background Service

To keep it running 24/7:

```bash
# Using nohup (simple method)
nohup python3 main.py > output.log 2>&1 &

# Or use macOS launchd (see README.md for full setup)
```

## 📊 How It Works

### Booking Timeline

```
Example: Tuesday Pilates at 20:00

Sunday 20:00 ─────► Booking window opens (48h before)
Sunday 20:05 ─────► System attempts booking (48h + 5min buffer)
Tuesday 20:00 ─────► Lesson starts
```

### Smart Features

1. **48-Hour Window**: Books exactly when reservations open
2. **Anti-Detection**: Uses real iOS app headers
3. **Skip Booked**: Won't try to book lessons you already have
4. **Auto-Retry**: Refreshes token if expired
5. **Dry-Run**: Test without making real bookings

## 🔍 Monitoring

### Check Logs

```bash
# Real-time log viewing
tail -f anytime_booking.log

# See what was booked
grep "✓ Booked:" anytime_booking.log

# See errors
grep "ERROR" anytime_booking.log
```

### Log Examples

```
✓ Booked: Pilates at 2025-11-05 20:00:00
✓ Lesson BBB is already booked (Status: Gereserveerd)
Found 3 lessons ready for booking
Booking cycle complete: 2 booked, 0 failed, 2 checked
```

## ⚙️ Configuration

### Change Lesson Schedule

Edit `config.py` → `TARGET_LESSONS`:

```python
TARGET_LESSONS = [
    { 'name': 'Yoga', 'weekday': 0, 'start_time': '10:00' },  # Monday
    { 'name': 'Spinning', 'weekday': 2, 'start_time': '18:00' },  # Wednesday
]
```

**Weekday numbers:**
- 0 = Monday
- 1 = Tuesday
- 2 = Wednesday
- 3 = Thursday
- 4 = Friday
- 5 = Saturday
- 6 = Sunday

### Change Check Frequency

Edit `config.py`:
```python
CHECK_INTERVAL_MINUTES = 15  # Check every 15 minutes
```

### Change Booking Timing

Edit `config.py`:
```python
BOOKING_WINDOW_HOURS = 48      # Book 48h before lesson
BOOKING_BUFFER_MINUTES = 5     # Wait 5min after window opens
```

## 🔒 Security

- ✅ Credentials stored in `.env` (not committed to git)
- ✅ Token encrypted with AES-256
- ✅ Encryption key with restricted permissions (600)
- ✅ Automatic token refresh on expiry

## 🐛 Troubleshooting

### Problem: "Token invalid or expired"
**Solution**: Delete `token.enc` and restart. It will re-login automatically.

### Problem: "No lessons ready for booking"
**Solution**: Normal! Lessons are only bookable 48h before. Check `BOOKING_WINDOW_HOURS`.

### Problem: Lessons not being booked
**Solutions**:
1. Check `DRY_RUN=false` in `.env`
2. Verify lesson names match exactly (case-sensitive)
3. Check logs: `grep "Target lesson found" anytime_booking.log`

### Problem: "Already booked" but I want to re-book
**Solution**: The lesson has `BookingStatus: 'Gereserveerd'`. Cancel it in the app first.

## 📁 Files Overview

```
anytime/
├── main.py                  # Main entry point (run this)
├── config.py                # Configuration (edit lesson schedule here)
├── auth.py                  # Authentication & token management
├── api_client.py            # API communication
├── scheduler.py             # Booking logic
├── user_agent.py            # iOS app headers
├── test_*.py                # Test scripts
├── .env                     # Your credentials (DRY_RUN setting)
├── requirements.txt         # Python dependencies
└── anytime_booking.log      # Activity log
```

## 🔄 Weekly Workflow

The system automatically handles weekly rebooking:

```
Week 1: Books Tuesday Nov 5 Pilates (on Sunday Nov 3 at 20:05)
Week 2: Books Tuesday Nov 12 Pilates (on Sunday Nov 10 at 20:05)
Week 3: Books Tuesday Nov 19 Pilates (on Sunday Nov 17 at 20:05)
... continues indefinitely
```

## 💡 Tips

1. **Start in dry-run mode** to verify everything works
2. **Check logs daily** for the first week
3. **Keep the script running** on a computer/server that's always on
4. **Monitor booking confirmations** in the Sportivity app
5. **Adjust buffer time** if lessons fill up quickly

## 🆘 Support

If something isn't working:

1. Check the logs: `tail -f anytime_booking.log`
2. Run tests: `python3 test_booking.py`
3. Verify credentials in `.env`
4. Check internet connection
5. Ensure Sportivity API is accessible

## 📈 Next Steps (Optional Improvements)

- Add email/Telegram notifications on successful bookings
- Add retry logic with exponential backoff
- Add database to track booking history
- Add web dashboard to monitor status
- Add support for multiple users
- Add waitlist joining if lesson is full

---

**Last Updated**: November 2, 2025  
**Status**: ✅ Fully Functional (Dry-Run Tested)  
**Ready for**: Production use (set `DRY_RUN=false`)
