#!/usr/bin/env python3
"""
Main entry point for the sport lesson booking automation system.
"""
import logging
import sys
from pathlib import Path

from config import Config
from scheduler import BookingScheduler


def setup_logging():
    """Configure logging for the application."""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(log_format))
    
    # File handler
    file_handler = logging.FileHandler(Config.LOG_FILE)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(log_format))
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, Config.LOG_LEVEL))
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    return root_logger


def main():
    """Main function."""
    logger = setup_logging()
    logger.info("=" * 60)
    logger.info("Sport Lesson Booking Automation Starting")
    logger.info("=" * 60)
    
    try:
        # Validate configuration
        Config.validate()
        logger.info("Configuration validated")
        
        # Create scheduler and run
        scheduler = BookingScheduler()
        
        logger.info(f"Monitoring lesson types: {', '.join(Config.LESSON_TYPES)}")
        logger.info(f"Booking window: {Config.BOOKING_WINDOW_HOURS} hours before lesson")
        logger.info(f"Check interval: {Config.CHECK_INTERVAL_MINUTES} minutes")
        
        # Run continuously
        scheduler.run_continuous()
        
    except KeyboardInterrupt:
        logger.info("\nShutdown requested by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
