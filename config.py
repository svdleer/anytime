"""
Configuration file for the sport lesson reservation system.
"""
import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the reservation system."""
    
    # API Configuration
    BASE_URL = os.getenv('ANYTIME_API_URL', 'https://bossnl.mendixcloud.com')
    
    # Authentication
    USERNAME = os.getenv('ANYTIME_USERNAME', 'wendyvanderleer@gmail.com')
    PASSWORD = os.getenv('ANYTIME_PASSWORD', 'Vanderleer82')
    
    # Token storage
    TOKEN_FILE = 'token.enc'
    
    # Location ID for Sportivity
    LOCATION_ID = os.getenv('LOCATION_ID', '13686')
    
    # Lesson types to book automatically
    # These are matched by Description field in the API response
    LESSON_TYPES: List[str] = [
        'BBB (billen, buik, benen)',  # Tuesday 19:00
        'BBB (Billen, Buik, Benen)',  # Alternative capitalization
        'Pilates',                     # Tuesday 20:00 & Wednesday 10:30
        'Kick Fun',                    # Wednesday 09:30
        'H.I.I.T.',                    # Friday 09:30
        'Yoga',                        # Friday 10:30
    ]
    
    # Specific lesson schedule (for filtering by day and time)
    LESSON_SCHEDULE = {
        1: [  # Tuesday (0=Monday, 1=Tuesday, etc.)
            {'type': 'BBB (billen, buik, benen)', 'time': '19:00'},
            {'type': 'BBB (Billen, Buik, Benen)', 'time': '19:00'},
            {'type': 'Pilates', 'time': '20:00'},
        ],
        2: [  # Wednesday
            {'type': 'Kick Fun', 'time': '09:30'},
            {'type': 'Pilates', 'time': '10:30'},
        ],
        4: [  # Friday
            {'type': 'H.I.I.T.', 'time': '09:30'},
            {'type': 'Yoga', 'time': '10:30'},
        ]
    }
    
    # Booking timing (in hours before lesson start)
    BOOKING_WINDOW_HOURS = 48
    BOOKING_BUFFER_MINUTES = -5  # Start trying 5 minutes BEFORE window opens
    BOOKING_WINDOW_END_HOURS = 47  # Stop trying after 47 hours (1 hour window)
    RETRY_INTERVAL_MINUTES = 5  # Check every 5 minutes during booking window
    
    # Retry for full lessons
    MAX_RETRIES_FOR_FULL_LESSON = 4  # Try 4 times per day if lesson is full
    RETRY_HOURS = [9, 12, 15, 18]  # Try at 9am, 12pm, 3pm, 6pm
    
    # Schedule checking
    CHECK_INTERVAL_MINUTES = 15  # How often to check for new lessons
    SCHEDULE_LOOKAHEAD_DAYS = 9  # How many days ahead to check (7 days + 48h buffer)
    
    # User Agent Configuration
    IOS_VERSION = '18.0'  # Darwin 24.6.0 = iOS 18.0
    IPHONE_MODEL = 'iPhone 15 Pro'
    APP_VERSION = '2004302'
    BUNDLE_ID = 'com.boss.sportivity'
    
    
    # Dry run (do not send booking POSTs). Set to False to enable real booking.
    DRY_RUN = os.getenv('DRY_RUN', 'true').lower() in ('1', 'true', 'yes')
    
    # Retry configuration
    MAX_RETRY_ATTEMPTS = 3
    RETRY_DELAY_SECONDS = 5
    
    # Email notifications
    ENABLE_EMAIL = os.getenv('ENABLE_EMAIL', 'true').lower() in ('1', 'true', 'yes')
    EMAIL_FROM = os.getenv('EMAIL_FROM', '')
    EMAIL_TO = os.getenv('EMAIL_TO', '')
    EMAIL_SMTP_SERVER = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
    EMAIL_SMTP_PORT = int(os.getenv('EMAIL_SMTP_PORT', '587'))
    EMAIL_SMTP_USER = os.getenv('EMAIL_SMTP_USER', '')
    EMAIL_SMTP_PASSWORD = os.getenv('EMAIL_SMTP_PASSWORD', '')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = 'anytime_booking.log'
    # Target lessons mapping (weekday: Monday=0 .. Sunday=6)
    # Update these entries to match the lessons you want to auto-book.
    TARGET_LESSONS = [
        # Tuesday
        { 'name': 'BBB', 'weekday': 1, 'start_time': '19:00' },
        { 'name': 'Pilates', 'weekday': 1, 'start_time': '20:00' },
        # Wednesday
        { 'name': 'Kick Fun', 'weekday': 2, 'start_time': '09:30' },
        { 'name': 'Pilates', 'weekday': 2, 'start_time': '10:30' },
        # Friday
        { 'name': 'H.I.I.T.', 'weekday': 4, 'start_time': '09:30' },
        { 'name': 'Yoga', 'weekday': 4, 'start_time': '10:30' },
    ]

    # Time matching tolerance (minutes) when comparing lesson start times
    TIME_TOLERANCE_MINUTES = 2

    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present."""
        if not cls.USERNAME or not cls.PASSWORD:
            raise ValueError("USERNAME and PASSWORD must be set")
        if not cls.BASE_URL:
            raise ValueError("BASE_URL must be set")
        return True
