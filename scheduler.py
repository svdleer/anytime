"""
Scheduling logic for automatic lesson booking.
"""
import logging
from typing import List, Dict, Set, Optional
from datetime import datetime, timedelta, timezone
import time
from dataclasses import dataclass

from config import Config
from api_client import APIClient
from email_notifier import EmailNotifier

logger = logging.getLogger(__name__)


@dataclass
class Lesson:
    """Represents a lesson."""
    id: str
    name: str
    lesson_type: str
    start_time: datetime
    duration_minutes: int
    instructor: str = ""
    location: str = ""
    available_spots: int = 0
    
    @property
    def booking_opens_at(self) -> datetime:
        """Calculate when booking opens for this lesson."""
        return self.start_time - timedelta(hours=Config.BOOKING_WINDOW_HOURS)
    
    @property
    def target_booking_time(self) -> datetime:
        """Calculate the earliest time to attempt booking (5 min before window)."""
        return self.booking_opens_at + timedelta(minutes=Config.BOOKING_BUFFER_MINUTES)
    
    @property
    def booking_window_end(self) -> datetime:
        """Calculate when to stop trying (47 hours before lesson)."""
        return self.start_time - timedelta(hours=Config.BOOKING_WINDOW_END_HOURS)
    
    def is_bookable_now(self) -> bool:
        """Check if this lesson is in the booking window (anytime from 48h before until lesson starts)."""
        now = datetime.now()  # Use naive datetime to match lesson times
        return now >= self.booking_opens_at and now < self.start_time
    
    def is_in_active_booking_window(self) -> bool:
        """Check if we're in the aggressive booking window (first hour: 48h to 47h before lesson)."""
        now = datetime.now()  # Use naive datetime to match lesson times
        # Aggressive window: from 5 min before 48h until 47h before lesson (1 hour window)
        # This is when we check every 5 minutes to grab spots quickly
        return now >= self.target_booking_time and now <= self.booking_window_end
    
    def should_attempt_booking(self) -> bool:
        """Check if we should attempt booking this lesson now."""
        return self.is_in_active_booking_window()


class BookingScheduler:
    """Manages automatic booking of lessons."""
    
    def __init__(self):
        self.api_client = APIClient()
        self.booked_lesson_ids: Set[str] = set()
        self.attempted_lesson_ids: Set[str] = set()
        self.full_lesson_retries: Dict[str, Dict] = {}  # Track retries for full lessons
        self.email_notifier = EmailNotifier()
    
    def parse_lesson(self, lesson_data: Dict) -> Lesson:
        """
        Parse lesson data from Sportivity API response.
        
        Args:
            lesson_data: Raw lesson data from API
            
        Returns:
            Lesson object
        """
        from dateutil import parser
        
        # Use local time (LessonStartTime) for lesson scheduling
        # This ensures times match user's expectations (09:30, 10:30, etc.)
        local_start = lesson_data.get('LessonStartTime')
        local_end = lesson_data.get('LessonEndTime')
        
        if local_start:
            start_time = parser.parse(local_start)
        else:
            # Fallback to UTC
            start_time = parser.isoparse(lesson_data.get('UTCStartTime'))
        
        if local_end:
            end_time = parser.parse(local_end)
        else:
            end_time = parser.isoparse(lesson_data.get('UTCEndTime'))
        
        duration = int((end_time - start_time).total_seconds() / 60)
        
        # Calculate available spots
        max_participants = lesson_data.get('MaximumParticipants', 0)
        spots_taken = lesson_data.get('SpotsInt', 0)
        available_spots = max_participants - spots_taken
        
        return Lesson(
            id=str(lesson_data.get('_id')),  # Lesson ID
            name=lesson_data.get('Description', ''),  # Lesson type/name
            lesson_type=lesson_data.get('Description', ''),  # Same as name
            start_time=start_time,
            duration_minutes=duration,
            instructor=lesson_data.get('Trainer', ''),
            location=lesson_data.get('LocationName', ''),
            available_spots=available_spots
        )
    
    def filter_target_lessons(self, lessons: List[Dict]) -> List[Lesson]:
        """
        Filter lessons to only include target lesson types on specific days/times.
        
        Args:
            lessons: List of raw lesson data
            
        Returns:
            List of Lesson objects matching target types and schedule
        """
        target_lessons = []
        
        for lesson_data in lessons:
            try:
                # Skip if already booked or cancelled by user
                booking_status = lesson_data.get('BookingStatus')
                if booking_status:
                    logger.debug(f"Skipping lesson with status '{booking_status}': {lesson_data.get('Description')} at {lesson_data.get('LessonStartTime')}")
                    continue
                
                lesson = self.parse_lesson(lesson_data)
                
                # Skip if already attempted or booked in this session
                if lesson.id in self.booked_lesson_ids or lesson.id in self.attempted_lesson_ids:
                    continue
                
                # Check if this is a lesson type we want to book
                if lesson.lesson_type not in Config.LESSON_TYPES:
                    continue
                
                # Check if the lesson matches our schedule (day and time)
                # Use local time from LessonStartTime for comparison (not UTC)
                local_start = lesson_data.get('LessonStartTime')
                if local_start:
                    from dateutil import parser
                    local_time = parser.parse(local_start)
                    day_of_week = local_time.weekday()
                    lesson_time = local_time.strftime('%H:%M')
                else:
                    day_of_week = lesson.start_time.weekday()
                    lesson_time = lesson.start_time.strftime('%H:%M')
                
                if day_of_week in Config.LESSON_SCHEDULE:
                    # Check if this lesson matches the schedule for this day
                    matches_schedule = any(
                        schedule['type'] == lesson.lesson_type and schedule['time'] == lesson_time
                        for schedule in Config.LESSON_SCHEDULE[day_of_week]
                    )
                    
                    if matches_schedule:
                        target_lessons.append(lesson)
                        logger.debug(f"Target lesson found: {lesson.name} on {lesson.start_time}")
                # Only book lessons that are explicitly in LESSON_SCHEDULE (day + time + type must match)
                        
            except Exception as e:
                logger.error(f"Error parsing lesson: {e}")
                continue
        
        return target_lessons
    
    def get_upcoming_bookable_lessons(self) -> List[Lesson]:
        """
        Get lessons that are ready to be booked (including retries for full lessons).
        
        Returns:
            List of Lesson objects ready for booking
        """
        schedule_data = self.api_client.get_schedule()
        all_lessons = self.filter_target_lessons(schedule_data)
        
        bookable_lessons = []
        for lesson in all_lessons:
            # Bookable if window is open (anytime from 48h before until lesson starts)
            if lesson.is_bookable_now():
                bookable_lessons.append(lesson)
        
        logger.info(f"Found {len(bookable_lessons)} lessons ready for booking")
        return bookable_lessons
    
    def book_lesson(self, lesson: Lesson) -> bool:
        """
        Attempt to book a lesson with retry logic for full lessons.
        
        Args:
            lesson: Lesson to book
            
        Returns:
            True if successful, False otherwise
        """
        self.attempted_lesson_ids.add(lesson.id)

        # Check if lesson is already booked by fetching full details
        lesson_details = self.api_client.get_lesson_by_id(lesson.id)
        if lesson_details:
            booking_status = lesson_details.get('BookingStatus')
            if booking_status:
                # BookingStatus can be: 'Gereserveerd' (reserved), 'Afgemeld_door_klant' (cancelled), etc.
                if booking_status == 'Gereserveerd':
                    logger.info(f"✓ Lesson {lesson.name} at {lesson.start_time} is already booked (Status: {booking_status})")
                    self.booked_lesson_ids.add(lesson.id)
                    # Send email notification
                    self.email_notifier.send_booking_success(
                        lesson.name, 
                        lesson.start_time,
                        lesson.instructor
                    )
                    return True  # Already booked successfully
                elif booking_status == 'Afgemeld_door_klant':
                    logger.info(f"Lesson {lesson.name} was cancelled, will attempt to re-book")
                    # Continue to booking logic
                else:
                    logger.info(f"Lesson {lesson.name} has status '{booking_status}', will attempt to book")
                    # Continue to booking logic
            
            # Check if lesson is full
            is_full = lesson_details.get('Full', False)
            if is_full and lesson.available_spots <= 0:
                logger.warning(f"Lesson {lesson.name} is full. Will retry later.")
                self._track_full_lesson_retry(lesson)
                return False
        
        # Format lesson start time as UTC ISO string expected by API: 2025-11-03T19:00:00.000Z
        try:
            start_utc = lesson.start_time
            if start_utc.tzinfo is None:
                # assume local -> convert to UTC
                start_utc = start_utc.replace(tzinfo=timezone.utc)
            start_utc = start_utc.astimezone(timezone.utc)
            lesson_date_iso = start_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        except Exception:
            # Fallback: use naive isoformat
            lesson_date_iso = lesson.start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')

        success = self.api_client.book_lesson(lesson.id, lesson_date_iso)
        
        if success:
            self.booked_lesson_ids.add(lesson.id)
            logger.info(f"✓ Booked: {lesson.name} at {lesson.start_time}")
            # Send email notification
            self.email_notifier.send_booking_success(
                lesson.name,
                lesson.start_time,
                lesson.instructor
            )
        else:
            logger.warning(f"✗ Failed to book: {lesson.name} at {lesson.start_time}")
            self._track_full_lesson_retry(lesson)
        
        return success
    
    def _track_full_lesson_retry(self, lesson: Lesson):
        """Track retry attempts for full lessons."""
        if lesson.id not in self.full_lesson_retries:
            self.full_lesson_retries[lesson.id] = {
                'lesson': lesson,
                'attempts': 0,
                'last_attempt': None,
                'retry_hours': []
            }
        
        now = datetime.now()  # Use naive datetime
        retry_info = self.full_lesson_retries[lesson.id]
        retry_info['attempts'] += 1
        retry_info['last_attempt'] = now
        
        current_hour = now.hour
        if current_hour not in retry_info['retry_hours']:
            retry_info['retry_hours'].append(current_hour)
        
        logger.info(f"Full lesson retry tracking: {lesson.name} - Attempt {retry_info['attempts']}")
    
    def should_retry_full_lesson(self, lesson: Lesson) -> bool:
        """Check if we should retry booking a full lesson."""
        if lesson.id not in self.full_lesson_retries:
            return True  # First attempt
        
        retry_info = self.full_lesson_retries[lesson.id]
        now = datetime.now()  # Use naive datetime
        current_hour = now.hour
        
        # Check if we've hit max retries for the day
        if retry_info['attempts'] >= Config.MAX_RETRIES_FOR_FULL_LESSON:
            logger.debug(f"Max retries reached for {lesson.name}")
            return False
        
        # Check if we should retry at this hour (9am, 12pm, 3pm, 6pm)
        if current_hour in Config.RETRY_HOURS and current_hour not in retry_info['retry_hours']:
            logger.info(f"Retry hour {current_hour}:00 - will attempt {lesson.name} again")
            return True
        
        # During active booking window (48h-47h), retry every 5 minutes
        if lesson.is_in_active_booking_window():
            if retry_info['last_attempt']:
                time_since_last = (now - retry_info['last_attempt']).total_seconds() / 60
                if time_since_last >= Config.RETRY_INTERVAL_MINUTES:
                    return True
            else:
                return True
        
        return False
    
    def process_bookings(self) -> Dict[str, int]:
        """
        Check for and book any available lessons.
        
        Returns:
            Dictionary with booking statistics
        """
        logger.info("Checking for bookable lessons...")
        
        lessons = self.get_upcoming_bookable_lessons()
        stats = {
            'checked': len(lessons),
            'booked': 0,
            'failed': 0
        }
        
        for lesson in lessons:
            success = self.book_lesson(lesson)
            if success:
                stats['booked'] += 1
            else:
                stats['failed'] += 1
            
            # Small delay between bookings to appear more human
            time.sleep(2)
        
        return stats
    
    def get_next_booking_window(self) -> Optional[datetime]:
        """
        Calculate when the next booking window opens.
        
        Returns:
            DateTime of next booking window, or None if no upcoming lessons
        """
        schedule_data = self.api_client.get_schedule()
        all_lessons = self.filter_target_lessons(schedule_data)
        
        # Find lessons that haven't been booked yet
        unboked_lessons = [
            lesson for lesson in all_lessons
            if lesson.id not in self.booked_lesson_ids
            and lesson.id not in self.attempted_lesson_ids
        ]
        
        if not unboked_lessons:
            return None
        
        # Find the earliest booking window
        next_lesson = min(unboked_lessons, key=lambda l: l.target_booking_time)
        return next_lesson.target_booking_time
    
    def run_continuous(self) -> None:
        """
        Run the booking scheduler continuously.
        Uses aggressive 5-minute checks during active booking windows (48h-47h before lessons).
        """
        logger.info("Starting continuous booking scheduler with aggressive retry logic...")
        logger.info(f"Active booking window: {Config.BOOKING_BUFFER_MINUTES} min before to {Config.BOOKING_WINDOW_END_HOURS}h before lesson")
        logger.info(f"Retry interval during window: {Config.RETRY_INTERVAL_MINUTES} minutes")
        logger.info(f"Daily retry attempts for full lessons: {Config.MAX_RETRIES_FOR_FULL_LESSON} times at hours {Config.RETRY_HOURS}")
        
        while True:
            try:
                stats = self.process_bookings()
                logger.info(
                    f"Booking cycle complete: "
                    f"{stats['booked']} booked, "
                    f"{stats['failed']} failed, "
                    f"{stats['checked']} checked"
                )
                
                # Show active retry tracking
                if self.full_lesson_retries:
                    logger.info(f"Tracking {len(self.full_lesson_retries)} lessons with retries")
                
                # Show next booking window
                next_window = self.get_next_booking_window()
                if next_window:
                    now = datetime.now()  # Use naive datetime
                    time_until = next_window - now
                    logger.info(f"Next booking window in: {time_until}")
                
                # Dynamic sleep interval: 5 minutes during active windows, 15 minutes otherwise
                schedule_data = self.api_client.get_schedule()
                all_lessons = self.filter_target_lessons(schedule_data)
                
                has_active_window = any(lesson.is_in_active_booking_window() for lesson in all_lessons)
                
                if has_active_window or self.full_lesson_retries:
                    sleep_minutes = Config.RETRY_INTERVAL_MINUTES
                    logger.info(f"⚡ Active booking window detected - checking every {sleep_minutes} minutes")
                else:
                    sleep_minutes = Config.CHECK_INTERVAL_MINUTES
                    logger.info(f"Sleeping for {sleep_minutes} minutes...")
                
                time.sleep(sleep_minutes * 60)
                
            except KeyboardInterrupt:
                logger.info("Scheduler stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in booking cycle: {e}", exc_info=True)
                logger.info("Continuing after error...")
                time.sleep(60)  # Wait a minute before retrying
