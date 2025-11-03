#!/usr/bin/env python3
"""
Test fetching lesson details by ID to check BookingStatus.
"""
import logging
import sys
import json
from api_client import APIClient

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_lesson_details():
    """Test fetching lesson details."""
    try:
        logger.info("=" * 60)
        logger.info("Testing Sportivity Lesson Details API")
        logger.info("=" * 60)
        
        client = APIClient()
        
        # Test with a known lesson ID (from your curl: 16226963)
        lesson_id = "16226963"  # XCORE lesson
        
        logger.info(f"\nFetching details for lesson ID: {lesson_id}")
        details = client.get_lesson_by_id(lesson_id)
        
        if details:
            logger.info("\n✓ Lesson details received:")
            logger.info(json.dumps(details, indent=2, default=str))
            
            # Check booking status
            booking_status = details.get('BookingStatus')
            if booking_status:
                logger.info(f"\n✓ Lesson is BOOKED - Status: {booking_status}")
            else:
                logger.info("\n✓ Lesson is NOT booked - available for booking")
            
            # Show other useful fields
            logger.info(f"\nLesson: {details.get('Description')}")
            logger.info(f"Trainer: {details.get('Trainer')}")
            logger.info(f"Time: {details.get('LessonStartTime')}")
            logger.info(f"Spots: {details.get('SpotsInt')}/{details.get('MaximumParticipants')}")
        else:
            logger.error("✗ Failed to fetch lesson details")
            return False
        
        logger.info("\n" + "=" * 60)
        logger.info("Test completed successfully!")
        logger.info("=" * 60)
        return True
        
    except Exception as e:
        logger.error(f"\n✗ Test failed: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = test_lesson_details()
    sys.exit(0 if success else 1)
