# 🚀 NEW FEATURES - Enhanced Booking & Notifications

## 📅 Date: November 3, 2025

---

## ✨ What's New

### 1. ⚡ Aggressive Booking Window (48h → 47h)

**Previously**: System tried to book once at exactly 48 hours before lesson  
**Now**: System aggressively tries every **5 minutes** from **5 minutes BEFORE** the 48-hour window opens until **47 hours** before the lesson.

#### Booking Timeline Example

For **Tuesday Pilates at 20:00**:

```
Sunday 19:55 ────► Start checking (5 min before window)
Sunday 20:00 ────► Official booking window opens
Sunday 20:05 ────► Attempt #1
Sunday 20:10 ────► Attempt #2
Sunday 20:15 ────► Attempt #3
...every 5 minutes...
Monday 20:00 ────► Stop trying (47h before lesson = 1h window)
```

**Benefits:**
- ✅ Higher chance of getting spots
- ✅ Catches cancellations immediately
- ✅ Beats other manual bookers

---

### 2. 🔄 Smart Retry for Full Lessons

**What happens if a lesson is full?**

The system will **automatically retry** throughout the day:

#### Retry Schedule
- **9:00 AM** - Morning check
- **12:00 PM** - Lunch check
- **3:00 PM** - Afternoon check  
- **6:00 PM** - Evening check

**Maximum**: 4 retry attempts per day for each full lesson

#### How It Works

1. **Initial Attempt**: System tries to book during active window (48h-47h)
2. **Lesson Full**: System detects `Full: true` or `available_spots: 0`
3. **Track for Retry**: Lesson added to retry queue
4. **Daily Checks**: System checks 4x per day at scheduled hours
5. **Success**: Books immediately when spot opens up
6. **Give Up**: After 4 attempts in one day, stops trying

**Example Log Output:**
```
10:05 - Lesson Pilates is full. Will retry later.
10:05 - Full lesson retry tracking: Pilates - Attempt 1
12:00 - Retry hour 12:00 - will attempt Pilates again
12:05 - ✓ Booked: Pilates at 2025-11-05 20:00:00 (got it on retry!)
```

---

### 3. 📧 Email Notifications

Get instant email confirmation when lessons are booked!

#### Email Features

**Booking Success Email:**
- ✅ Sent immediately after successful booking
- ✅ Beautiful HTML format with lesson details
- ✅ Includes: Lesson name, date, time, instructor, location
- ✅ Mobile-friendly design

**Email Preview:**
```
Subject: ✅ Sportivity Booking Confirmed: Pilates

┌─────────────────────────────────┐
│   ✅ Booking Confirmed!         │
└─────────────────────────────────┘

Lesson:     Pilates
Date:       Tuesday, November 5, 2025
Time:       20:00
Instructor: Hasret Dagdelen
Location:   First Class Sports

This booking was made automatically by your 
Sportivity Auto-Booking System.
```

#### Email Configuration

**Gmail Setup (Recommended):**

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Copy the 16-character password
3. **Update `.env`**:
   ```env
   ENABLE_EMAIL=true
   EMAIL_FROM=your_email@gmail.com
   EMAIL_TO=your_email@gmail.com
   EMAIL_SMTP_SERVER=smtp.gmail.com
   EMAIL_SMTP_PORT=587
   EMAIL_SMTP_USER=your_email@gmail.com
   EMAIL_SMTP_PASSWORD=your_16_char_app_password
   ```

**Other Email Providers:**

| Provider | SMTP Server | Port |
|----------|-------------|------|
| Outlook | smtp-mail.outlook.com | 587 |
| Yahoo | smtp.mail.yahoo.com | 587 |
| iCloud | smtp.mail.me.com | 587 |

---

## ⚙️ Configuration

### New Settings in `config.py`

```python
# Aggressive booking window
BOOKING_BUFFER_MINUTES = -5      # Start 5 min BEFORE 48h window
BOOKING_WINDOW_END_HOURS = 47    # Stop at 47h (1 hour window)
RETRY_INTERVAL_MINUTES = 5       # Check every 5 min during window

# Full lesson retries
MAX_RETRIES_FOR_FULL_LESSON = 4  # 4 attempts per day
RETRY_HOURS = [9, 12, 15, 18]    # Specific retry hours

# Email notifications
ENABLE_EMAIL = true              # Enable/disable emails
EMAIL_FROM = your_email          # Sender email
EMAIL_TO = your_email            # Recipient email
EMAIL_SMTP_SERVER = smtp server  # SMTP server address
EMAIL_SMTP_PORT = 587            # SMTP port
EMAIL_SMTP_USER = your_email     # SMTP username
EMAIL_SMTP_PASSWORD = app_pass   # SMTP password (app-specific)
```

---

## 🎯 Updated Behavior

### Check Frequency

**During Active Booking Window (48h-47h):**
- Checks every **5 minutes** ⚡
- Aggressive attempts to grab spots
- Logs: "⚡ Active booking window detected"

**Outside Booking Window:**
- Checks every **15 minutes** (normal)
- Monitors for new lessons
- Tracks full lesson retries

### Retry Logic

**Lesson Available:**
- ✅ Books immediately
- ✅ Sends email
- ✅ Logs success

**Lesson Full:**
- ⏳ Adds to retry queue
- ⏳ Attempts 4x per day
- ⏳ Tracks attempt count
- ✅ Books when spot opens
- ✅ Sends email on success

---

## 🧪 Testing

### Test Email System

```bash
python3 test_email.py
```

Expected output:
```
✓ Test email sent successfully!
  Check your inbox for the confirmation email
```

### Test Booking with New Logic

```bash
# Dry-run mode (safe)
python3 test_booking.py
```

Check logs for:
```
⚡ Active booking window detected - checking every 5 minutes
Found 2 lessons ready for booking (active window + retries)
Full lesson retry tracking: BBB - Attempt 1
```

---

## 📊 Performance Impact

**Before (Old System):**
- 1 check every 15 minutes
- 1 attempt per lesson
- No retry for full lessons
- No notifications

**After (New System):**
- **During active window**: 1 check every 5 minutes (12 per hour)
- **Multiple attempts**: Every 5 min for 1 hour = up to 12 attempts
- **Retry full lessons**: 4 extra attempts per day
- **Email notifications**: Instant confirmation

**Resource Usage:**
- API calls increase by ~3x during active windows
- Minimal impact outside windows (same 15 min checks)
- Email: ~2-4 emails per successful booking

---

## 💡 Tips

### Maximize Success Rate

1. **Keep system running 24/7** (use nohup or launchd)
2. **Enable email** to get instant confirmation
3. **Check logs** after first week to verify behavior
4. **Adjust retry hours** if needed (edit `RETRY_HOURS` in config.py)

### Gmail App Password Setup

**Step-by-step:**
1. Go to Google Account settings
2. Security → 2-Step Verification (enable if not on)
3. Security → App passwords
4. Generate password for "Mail"
5. Copy 16-character password
6. Paste into `.env` as `EMAIL_SMTP_PASSWORD`

### Troubleshooting Emails

**Email not sending?**
```bash
# Test email configuration
python3 test_email.py

# Check config
grep EMAIL .env

# Check logs
grep "email" anytime_booking.log
```

**Common issues:**
- ❌ Missing app password (not regular password!)
- ❌ 2FA not enabled on Gmail
- ❌ Wrong SMTP settings
- ❌ `ENABLE_EMAIL=false` in .env

---

## 📈 Expected Results

### Week 1 Performance

With the new aggressive booking + retry system:

**Tuesday BBB (19:00):**
- Sunday 18:55: Start checking
- Sunday 19:00-20:00: Aggressive attempts every 5 min
- **Result**: Booked at Sunday 19:05 ✓
- Email sent: Sunday 19:05 📧

**Tuesday Pilates (20:00):**
- Sunday 19:55: Start checking  
- Sunday 20:00-21:00: Aggressive attempts every 5 min
- **Result**: Booked at Sunday 20:00 ✓
- Email sent: Sunday 20:00 📧

**If lesson is full:**
- Monday 09:00: Retry attempt #1
- Monday 12:00: Retry attempt #2
- Monday 15:00: Retry attempt #3
- Monday 18:00: Retry attempt #4 → ✓ Got it!
- Email sent: Monday 18:00 📧

---

## 🎉 Summary

**New capabilities:**
- ✅ **12x more booking attempts** during active window
- ✅ **4 daily retries** for full lessons
- ✅ **Instant email notifications** on success
- ✅ **Higher success rate** catching cancellations
- ✅ **Better monitoring** with detailed logs

**Your lessons will be booked faster and more reliably!** 🚀

---

**Questions?**  
Check logs: `tail -f anytime_booking.log`  
Test email: `python3 test_email.py`  
Read guide: `GUIDE.md`
