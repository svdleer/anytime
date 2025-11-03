"""
API client for interacting with the sport lesson booking system.
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import Config
from auth import AuthClient

logger = logging.getLogger(__name__)


class APIClient:
    """Client for interacting with the booking API."""
    
    def __init__(self):
        self.base_url = Config.BASE_URL
        self.auth_client = AuthClient()
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create a session with retry logic."""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=Config.MAX_RETRY_ATTEMPTS,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS", "TRACE"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Make an authenticated request to the API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            Response object
        """
        url = f"{self.base_url}{endpoint}"
        headers = self.auth_client.get_auth_headers()
        
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
        kwargs['headers'] = headers
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                # Token might be expired, try to re-authenticate
                logger.warning("Got 401, attempting to re-authenticate")
                self.auth_client.token_manager.clear_token()
                headers = self.auth_client.get_auth_headers()
                kwargs['headers'] = headers
                response = self.session.request(method, url, **kwargs)
                response.raise_for_status()
                return response
            else:
                raise
    
    def get_schedule(self, start_date: datetime = None, end_date: datetime = None) -> List[Dict]:
        """
        Get the schedule of available lessons from Sportivity API.
        
        Args:
            start_date: Start date for schedule (defaults to today)
            end_date: End date for schedule (defaults to 7 days from start)
            
        Returns:
            List of lesson dictionaries
        """
        if start_date is None:
            start_date = datetime.now()
        if end_date is None:
            end_date = start_date + timedelta(days=Config.SCHEDULE_LOOKAHEAD_DAYS)
        
        # Sportivity endpoint for getting lesson IDs
        endpoint = "/SportivityAppV3/Lesson/GetIds"
        
        # Format dates in ISO format with timezone
        params = {
            'LocationId': Config.LOCATION_ID,
            'StartDate': start_date.strftime('%Y-%m-%dT00:00:00.000Z'),
            'EndDate': end_date.strftime('%Y-%m-%dT23:59:59.999Z')
        }
        
        try:
            logger.info(f"Fetching schedule from {start_date.date()} to {end_date.date()}")
            response = self._make_request('GET', endpoint, params=params)
            data = response.json()
            
            logger.debug(f"Schedule response structure: Response={data.get('Response')}, count={len(data.get('LessonDefinitions', []))}")
            
            # Sportivity returns lessons in 'LessonDefinitions' array
            lessons = data.get('LessonDefinitions', [])
            
            logger.info(f"Found {len(lessons)} lessons in schedule")
            return lessons
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch schedule: {e}")
            return []
    
    def get_lesson_by_id(self, lesson_id: str) -> Optional[Dict]:
        """Retrieve full lesson details by lesson ID."""
        endpoint = f"/SportivityAppV3/Lesson/LessonById?LessonId={lesson_id}"
        try:
            response = self._make_request('GET', endpoint)
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get lesson {lesson_id}: {e}")
            return None


    def book_lesson(self, lesson_id: str, lesson_date_iso: str) -> bool:
        """
        Book a specific lesson.
        
        Args:
            lesson_id: ID of the lesson to book
            lesson_date_iso: ISO-formatted lesson start datetime in UTC (e.g. 2025-11-03T19:00:00.000Z)
            
        Returns:
            True if booking successful, False otherwise
        """
        # Use Sportivity JoinLesson endpoint
        endpoint = "/SportivityAppV3/Lesson/JoinLesson"

        payload = {
            "LessonId": str(lesson_id),
            "BuyLesson": False,
            "lessonDate": lesson_date_iso,
            "waitingList": False
        }

        # Respect dry-run mode to avoid accidental bookings
        if Config.DRY_RUN:
            logger.info(f"DRY RUN: would POST to {endpoint} with payload: {payload}")
            return True

        try:
            logger.info(f"Attempting to book lesson: {lesson_id} at {lesson_date_iso}")
            response = self._make_request('POST', endpoint, json=payload)

            if response.status_code in (200, 201):
                logger.info(f"Successfully booked lesson: {lesson_id}")
                return True
            else:
                logger.warning(f"Booking failed with status {response.status_code}: {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to book lesson {lesson_id}: {e}")
            return False
    
    def get_my_bookings(self) -> List[Dict]:
        """
        Get list of current bookings.
        
        Returns:
            List of booking dictionaries
        """
        # TODO: Replace with actual endpoint from curl request
        endpoint = "/api/bookings"
        
        try:
            logger.info("Fetching current bookings")
            response = self._make_request('GET', endpoint)
            data = response.json()
            
            # TODO: Adjust based on actual API response structure
            bookings = data.get('bookings', [])
            logger.info(f"Found {len(bookings)} current bookings")
            return bookings
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch bookings: {e}")
            return []
