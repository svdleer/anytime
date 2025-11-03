# Anytime Sport Lesson Booking Automation

Automated booking system for sport lessons that reserves classes exactly 48 hours before they start.

## Features

- 🔐 **Secure Authentication**: AES-256 encrypted token storage with automatic re-authentication
- 📱 **iOS User-Agent Spoofing**: Mimics recent iPhone devices with auto-updating iOS versions
- ⏰ **Smart Scheduling**: Monitors and books lessons precisely at the 48-hour mark
- 🔄 **Continuous Operation**: Runs 24/7 checking for new bookable lessons
- 📊 **Multi-Lesson Support**: Handles 4 different lesson types simultaneously
- 🛡️ **Robust Error Handling**: Automatic retries and token refresh on failures
- 📝 **Detailed Logging**: Track all booking attempts and system status

## Architecture

```
anytime/
├── main.py              # Entry point
├── config.py            # Configuration management
├── auth.py              # Authentication & token management
├── user_agent.py        # iOS User-Agent generation
├── api_client.py        # API communication layer
├── scheduler.py         # Booking logic & scheduling
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
└── .gitignore          # Git ignore rules
```

## Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd anytime
```

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
ANYTIME_API_URL=https://api.yourservice.com
ANYTIME_USERNAME=your_username
ANYTIME_PASSWORD=your_password
LOG_LEVEL=INFO
```

### 5. Update configuration

Edit `config.py` to customize:

- **LESSON_TYPES**: The 4 lesson types you want to book
- **BOOKING_WINDOW_HOURS**: Hours before lesson start (default: 48)
- **CHECK_INTERVAL_MINUTES**: How often to check for new lessons (default: 15)
- **BOOKING_BUFFER_MINUTES**: Delay after booking window opens (default: 5)

## Configuration

### Your Scheduled Lessons

The system is configured to automatically book these lessons every week:

**Tuesday:**
- BBB (billen, buik, benen) - 19:00-20:00
- Pilates - 20:00-21:00

**Wednesday:**
- Kick Fun - 09:30-10:30
- Pilates - 10:30-11:30

**Friday:**
- H.I.I.T. - 09:30-10:30
- Yoga - 10:30-11:30

### Modify Lesson Schedule

To change which lessons to book, edit `config.py`:

```python
TARGET_LESSONS = [
    # Tuesday (weekday 1)
    { 'name': 'BBB', 'weekday': 1, 'start_time': '19:00' },
    { 'name': 'Pilates', 'weekday': 1, 'start_time': '20:00' },
    # Add more lessons...
]
```

**Weekday numbers:** Monday=0, Tuesday=1, Wednesday=2, Thursday=3, Friday=4, Saturday=5, Sunday=6

## Usage

### Testing (Dry-Run Mode - Safe)

By default, the system runs in **DRY-RUN mode** which will NOT make real bookings. This is safe to test:

```bash
# Test login
python test_login.py

# Test schedule fetching
python test_schedule.py

# Test lesson details
python test_lesson_details.py

# Test booking cycle (dry-run, no real bookings)
python test_booking.py
```

### Enable Real Bookings

⚠️ **IMPORTANT**: Only enable this when you're ready for real bookings!

Edit `.env` and set:
```env
DRY_RUN=false
```

Or set environment variable:
```bash
export DRY_RUN=false
```

### Run the booking automation

```bash
python main.py
```

The script will:
1. Authenticate with your credentials
2. Check for available lessons every 15 minutes (configurable)
3. Automatically book lessons when they become available (48h before start)
4. Skip lessons that are already booked
5. Continue running indefinitely

### Stop the automation

Press `Ctrl+C` to gracefully stop the script.

### View Logs

```bash
# Watch logs in real-time
tail -f anytime_booking.log

# View recent bookings
grep "Booked:" anytime_booking.log
```

## How It Works

### 1. Authentication Flow

```
┌─────────────┐
│   Startup   │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ Load Token from     │
│ Encrypted Storage   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Validate Token      │
└──────┬──────────────┘
       │
       ├─── Valid ───────► Use Token
       │
       └─── Invalid ────► Login Again
```

### 2. Booking Logic

```
Current Time: Sunday 10:00
Lesson Time:  Tuesday 10:00 (48 hours from now)

Booking Window Opens: Sunday 10:00
Target Booking Time:  Sunday 10:05 (+ 5 min buffer)

The system will book at: Sunday 10:05
```

### 3. Continuous Monitoring

Every 15 minutes (configurable), the script:
1. Fetches schedule for next 7 days
2. Filters for target lesson types
3. Calculates which lessons are ready to book
4. Attempts booking for eligible lessons
5. Tracks booked/attempted lessons to avoid duplicates

## Security Features

- **Token Encryption**: Bearer tokens stored encrypted with AES-256
- **Secure Key Storage**: Encryption keys with restricted file permissions (600)
- **Environment Variables**: Credentials loaded from `.env` (not committed to git)
- **Token Auto-Refresh**: Automatic re-authentication on token expiry

## Logging

All activity is logged to:
- **Console**: INFO level and above
- **File** (`anytime_booking.log`): DEBUG level and above

Log format:
```
2025-11-02 10:05:23 - scheduler - INFO - ✓ Booked: Yoga Class at 2025-11-04 10:00:00
2025-11-02 10:05:25 - scheduler - INFO - ✓ Booked: Spin Class at 2025-11-04 18:00:00
```

## Customization

### Change lesson types

Edit `config.py`:

```python
LESSON_TYPES: List[str] = [
    'yoga',
    'spinning',
    'pilates',
    'boxing'
]
```

### Adjust booking timing

Edit `config.py`:

```python
BOOKING_WINDOW_HOURS = 48  # When bookings open
BOOKING_BUFFER_MINUTES = 5  # Wait time after window opens
```

### Change check frequency

Edit `config.py`:

```python
CHECK_INTERVAL_MINUTES = 10  # Check every 10 minutes
```

## Troubleshooting

### Token keeps expiring

**Solution**: Delete `token.enc` and `token_key` files, then restart. The system will re-authenticate automatically.

### Bookings fail

Check logs for specific error messages. Common issues:
- **Lesson already full**: The lesson may have filled up before booking window. Consider reducing `BOOKING_BUFFER_MINUTES`.
- **Outside booking window**: Bookings only work 48h before lesson. This is normal behavior.
- **Already booked**: System detected `BookingStatus: 'Gereserveerd'` and skipped.
- **Cancelled lesson**: System detected `BookingStatus: 'Afgemeld_door_klant'` and will re-book.
- **Network issues**: Check internet connection and Sportivity API status.

### No lessons being booked

**Solutions**:
1. Check `DRY_RUN=false` in `.env` (must be lowercase 'false')
2. Verify lesson names match exactly (check API response for exact spelling)
3. Check timing: Lessons only bookable 48h before start time
4. Check logs: `grep "Target lesson found" anytime_booking.log`
5. Verify weekday numbers are correct (Monday=0, Tuesday=1, etc.)

### Lesson already booked but showing as "not booked"

The system fetches lesson details via `LessonById` API and checks the `BookingStatus` field:
- `'Gereserveerd'` = Successfully booked (will skip)
- `'Afgemeld_door_klant'` = Cancelled by you (will re-book)
- `null` or missing = Not booked (will book)

### User-Agent detection

If you're being detected as a bot:
1. The system already mimics the real Sportivity iOS app
2. Check `user_agent.py` for current iOS version (18.0 / Darwin 24.6.0)
3. Increase delays: Edit `scheduler.py` and increase `time.sleep(2)` to `time.sleep(5)`
4. Reduce check frequency: Edit `config.py` `CHECK_INTERVAL_MINUTES` from 15 to 30

## Running as a Service

### macOS (launchd)

Create `~/Library/LaunchAgents/com.anytime.booking.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.anytime.booking</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/venv/bin/python</string>
        <string>/path/to/anytime/main.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/path/to/anytime</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

Load the service:
```bash
launchctl load ~/Library/LaunchAgents/com.anytime.booking.plist
```

### Linux (systemd)

Create `/etc/systemd/system/anytime-booking.service`:

```ini
[Unit]
Description=Anytime Sport Lesson Booking
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/path/to/anytime
ExecStart=/path/to/venv/bin/python /path/to/anytime/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable anytime-booking
sudo systemctl start anytime-booking
```

## Next Steps

**To complete the setup, please provide:**

1. **Curl requests** for:
   - Login/authentication
   - Getting schedule
   - Booking a lesson
   - (Optional) Token validation

2. **API response examples** showing:
   - Lesson data structure
   - Booking response format
   - Authentication response format

3. **Lesson type identifiers** - the exact values used by the API

4. **Any other API details**:
   - Rate limits
   - Required headers
   - Query parameters

Once you provide these, I'll update the code with the exact API integration!

## License

MIT

## Disclaimer

This tool is for personal use only. Make sure automated booking is allowed by your service's terms of service.