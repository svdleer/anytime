#!/usr/bin/env python3
"""
Test the email notification system.
"""
import logging
from datetime import datetime, timedelta
from email_notifier import EmailNotifier

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_email_notification():
    """Test sending a booking confirmation email."""
    logger.info("=" * 60)
    logger.info("Testing Email Notification System")
    logger.info("=" * 60)
    
    # Test lesson data
    lesson_name = "Pilates"
    lesson_time = datetime.now() + timedelta(days=2, hours=20)  # Tuesday 8pm
    instructor = "Hasret Dagdelen"
    
    logger.info(f"\nSending test email for:")
    logger.info(f"  Lesson: {lesson_name}")
    logger.info(f"  Time: {lesson_time.strftime('%A, %B %d at %H:%M')}")
    logger.info(f"  Instructor: {instructor}")
    logger.info("")
    
    notifier = EmailNotifier()
    
    # Send test email
    success = notifier.send_booking_success(
        lesson_name=lesson_name,
        lesson_time=lesson_time,
        instructor=instructor
    )
    
    if success:
        logger.info("✓ Test email sent successfully!")
        logger.info("  Check your inbox for the confirmation email")
    else:
        logger.warning("✗ Email not sent")
        logger.info("  Possible reasons:")
        logger.info("  - ENABLE_EMAIL=false in .env")
        logger.info("  - Email credentials not configured in .env")
        logger.info("  - SMTP settings incorrect")
        logger.info("")
        logger.info("  To configure email:")
        logger.info("  1. Edit .env file")
        logger.info("  2. Set EMAIL_FROM, EMAIL_TO, EMAIL_SMTP_USER, EMAIL_SMTP_PASSWORD")
        logger.info("  3. For Gmail: use an App Password (not your regular password)")
        logger.info("     https://support.google.com/accounts/answer/185833")
    
    logger.info("")
    logger.info("=" * 60)
    return success


if __name__ == "__main__":
    test_email_notification()
