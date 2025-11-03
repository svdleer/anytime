#!/usr/bin/env python3
"""
Test script to fetch and display the schedule.
"""
import logging
import sys
import json
from datetime import datetime, timedelta
from api_client import APIClient

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_schedule():
    """Test fetching the schedule."""
    try:
        logger.info("=" * 60)
        logger.info("Testing Sportivity Schedule API")
        logger.info("=" * 60)
        
        client = APIClient()
        
        # Test today's schedule
        logger.info("\n1. Fetching today's schedule...")
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        
        lessons = client.get_schedule(start_date=today, end_date=tomorrow)
        
        logger.info(f"\n✓ Received {len(lessons)} lessons")
        
        if lessons:
            logger.info("\nFirst lesson sample:")
            logger.info(json.dumps(lessons[0], indent=2, default=str))
            
            if len(lessons) > 1:
                logger.info("\nAll lesson IDs/items:")
                for i, lesson in enumerate(lessons[:10], 1):  # Show first 10
                    logger.info(f"{i}. {lesson}")
        
        # Test 7-day lookahead
        logger.info("\n" + "=" * 60)
        logger.info("2. Fetching 7-day schedule...")
        end_date = today + timedelta(days=7)
        lessons_week = client.get_schedule(start_date=today, end_date=end_date)
        logger.info(f"✓ Received {len(lessons_week)} lessons for the next 7 days")
        
        logger.info("\n" + "=" * 60)
        logger.info("Test completed successfully!")
        logger.info("=" * 60)
        return True
        
    except Exception as e:
        logger.error(f"\n✗ Test failed: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = test_schedule()
    sys.exit(0 if success else 1)
