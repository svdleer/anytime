#!/usr/bin/env python3
"""
Dry-run test to simulate booking cycle.
This will NOT perform real bookings when Config.DRY_RUN is True.
"""
import logging
import sys

from config import Config
from scheduler import BookingScheduler

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_booking_cycle():
    logger.info("Starting dry-run booking cycle test")
    scheduler = BookingScheduler()
    stats = scheduler.process_bookings()
    logger.info(f"Dry-run booking stats: {stats}")
    return stats


if __name__ == '__main__':
    if not Config.DRY_RUN:
        logger.warning('Config.DRY_RUN is False. For safety this test expects DRY_RUN=True')
    try:
        test_booking_cycle()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        sys.exit(1)
