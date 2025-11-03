#!/usr/bin/env python3
"""
Test script to verify lesson filtering logic.
"""
import logging
import sys
from datetime import datetime, timedelta
from scheduler import BookingScheduler

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_lesson_filtering():
    """Test the lesson filtering logic."""
    try:
        logger.info("=" * 60)
        logger.info("Testing Lesson Filtering Logic")
        logger.info("=" * 60)
        
        scheduler = BookingScheduler()
        
        # Fetch 7-day schedule
        logger.info("\nFetching 7-day schedule...")
        today = datetime.now()
        end_date = today + timedelta(days=7)
        
        schedule_data = scheduler.api_client.get_schedule(start_date=today, end_date=end_date)
        logger.info(f"Found {len(schedule_data)} total lessons")
        
        # Filter to target lessons
        logger.info("\nFiltering for target lessons...")
        target_lessons = scheduler.filter_target_lessons(schedule_data)
        
        logger.info(f"\n✓ Found {len(target_lessons)} target lessons to book")
        
        if target_lessons:
            logger.info("\n" + "=" * 60)
            logger.info("Target Lessons:")
            logger.info("=" * 60)
            
            for lesson in target_lessons:
                day_name = lesson.start_time.strftime('%A')
                time_str = lesson.start_time.strftime('%H:%M')
                bookable_at = lesson.booking_opens_at.strftime('%Y-%m-%d %H:%M')
                
                logger.info(f"\n  • {lesson.name}")
                logger.info(f"    Day: {day_name}")
                logger.info(f"    Time: {time_str} - {lesson.duration_minutes} min")
                logger.info(f"    Instructor: {lesson.instructor}")
                logger.info(f"    Available spots: {lesson.available_spots}")
                logger.info(f"    Booking opens: {bookable_at}")
                logger.info(f"    Should book now: {lesson.should_attempt_booking()}")
        else:
            logger.info("\n  No target lessons found in the schedule")
        
        logger.info("\n" + "=" * 60)
        logger.info("Test completed successfully!")
        logger.info("=" * 60)
        return True
        
    except Exception as e:
        logger.error(f"\n✗ Test failed: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = test_lesson_filtering()
    sys.exit(0 if success else 1)
