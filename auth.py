"""
Authentication and token management.
"""
import json
import os
import logging
from typing import Optional, Dict
from datetime import datetime
import requests
from cryptography.fernet import Fernet
from pathlib import Path

from config import Config
from user_agent import iOSUserAgent

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


class TokenManager:
    """Manages bearer token storage and validation."""
    
    def __init__(self, token_file: str = None):
        self.token_file = token_file or Config.TOKEN_FILE
        self._key = self._get_or_create_key()
        self._cipher = Fernet(self._key)
        self._token: Optional[str] = None
        self._load_token()
    
    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key for token storage."""
        key_file = Path('.token_key')
        if key_file.exists():
            return key_file.read_bytes()
        else:
            key = Fernet.generate_key()
            key_file.write_bytes(key)
            # Set restrictive permissions
            os.chmod(key_file, 0o600)
            return key
    
    def _load_token(self) -> None:
        """Load token from encrypted file."""
        token_path = Path(self.token_file)
        if token_path.exists():
            try:
                encrypted_data = token_path.read_bytes()
                decrypted_data = self._cipher.decrypt(encrypted_data)
                self._token = decrypted_data.decode('utf-8')
                logger.info("Token loaded from storage")
            except Exception as e:
                logger.warning(f"Failed to load token: {e}")
                self._token = None
    
    def save_token(self, token: str) -> None:
        """Save token to encrypted file."""
        try:
            encrypted_data = self._cipher.encrypt(token.encode('utf-8'))
            token_path = Path(self.token_file)
            token_path.write_bytes(encrypted_data)
            os.chmod(token_path, 0o600)
            self._token = token
            logger.info("Token saved to storage")
        except Exception as e:
            logger.error(f"Failed to save token: {e}")
            raise
    
    def get_token(self) -> Optional[str]:
        """Get the current token."""
        return self._token
    
    def clear_token(self) -> None:
        """Clear the token from memory and storage."""
        self._token = None
        token_path = Path(self.token_file)
        if token_path.exists():
            token_path.unlink()
        logger.info("Token cleared")


class AuthClient:
    """Handles authentication with the API."""
    
    def __init__(self):
        self.base_url = Config.BASE_URL
        self.token_manager = TokenManager()
        self.session = requests.Session()
        self.session.headers.update(iOSUserAgent.get_headers())
    
    def login(self, username: str = None, password: str = None) -> str:
        """
        Authenticate with the Sportivity API and return bearer token.
        
        Args:
            username: Email for authentication
            password: Password for authentication
            
        Returns:
            Bearer token string
            
        Raises:
            AuthenticationError: If authentication fails
        """
        username = username or Config.USERNAME
        password = password or Config.PASSWORD
        
        if not username or not password:
            raise AuthenticationError("Username and password are required")
        
        login_url = f"{self.base_url}/SportivityAppV3/Login"
        
        # Sportivity expects "User" and "Password" fields (capital letters)
        payload = {
            "User": username,
            "Password": password
        }
        
        try:
            logger.info(f"Attempting login for user: {username}")
            response = self.session.post(login_url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            logger.debug(f"Login response: {data}")
            
            # Extract token from response - adjust field name based on actual response
            token = data.get('Token') or data.get('token') or data.get('SessionToken') or data.get('session_token')
            
            if not token:
                raise AuthenticationError(f"No token found in response: {data}")
            
            self.token_manager.save_token(token)
            logger.info("Login successful")
            return token
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Login failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise AuthenticationError(f"Login failed: {e}")
    
    def validate_token(self) -> bool:
        """
        Check if the current token is still valid by attempting to fetch schedule.
        
        Returns:
            True if token is valid, False otherwise
        """
        token = self.token_manager.get_token()
        if not token:
            return False
        
        # Try to fetch schedule as a validation check
        try:
            from datetime import datetime
            
            headers = self.session.headers.copy()
            headers['Authorization'] = f'Bearer {token}'
            
            # Use lesson endpoint to validate with minimal date range
            today = datetime.now().strftime('%Y-%m-%dT00:00:00.000Z')
            validation_url = (
                f"{self.base_url}/SportivityAppV3/Lesson/GetIds"
                f"?LocationId={Config.LOCATION_ID}&StartDate={today}&EndDate={today}"
            )
            response = self.session.get(validation_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                logger.info("Token is valid")
                return True
            elif response.status_code == 401 or response.status_code == 403:
                logger.warning("Token is invalid or expired")
                return False
            else:
                logger.warning(f"Token validation returned status {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Token validation failed: {e}")
            return False
    
    def ensure_authenticated(self) -> str:
        """
        Ensure we have a valid token, re-authenticating if necessary.
        
        Returns:
            Valid bearer token
        """
        token = self.token_manager.get_token()
        
        if token and self.validate_token():
            return token
        
        logger.info("Token invalid or missing, re-authenticating...")
        return self.login()
    
    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get headers with valid authentication token.
        Sportivity uses standard 'Authorization: Bearer' header.
        
        Returns:
            Dictionary of headers including Authorization
        """
        token = self.ensure_authenticated()
        headers = iOSUserAgent.get_headers()
        headers['Authorization'] = f'Bearer {token}'
        return headers
