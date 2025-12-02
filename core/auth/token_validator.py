from datetime import datetime, timedelta
import os
from typing import Optional, Tuple
import requests
from django.core.cache import cache
from dotenv import load_dotenv

load_dotenv()

class TokenValidator:
    def __init__(self):
        self._token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None
        self._refresh_token()

    def _refresh_token(self) -> None:
        """Load token from environment and set expiry"""
        self._token = os.getenv('API_TOKEN')
        if not self._token:
            print("API_TOKEN not set in environment")
            raise ValueError("API_TOKEN not set in environment")
            self._token = None
            self._token_expiry = None
            return
        
        # Set expiry to 24 hours from now
        self._token_expiry = datetime.now() + timedelta(hours=24)
        
    @property
    def is_valid(self) -> bool:
        """Check if token is valid and not expired"""
        if not self._token or not self._token_expiry:
            print("Token or expiry not set")
            return False
        return datetime.now() < self._token_expiry

    def get_headers(self) -> dict:
        """Get authorization headers with valid token"""
        if not self.is_valid:
            print("Token is invalid or expired, refreshing...")
            self._refresh_token()
        if not self._token:
            print("No API token available")
            return {"error": "No API token available"}
        return {"Authorization": f"Token {self._token}"}

# Create singleton instance
token_validator = TokenValidator()