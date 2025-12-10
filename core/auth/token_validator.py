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
        self._initialized = False

    def _refresh_token(self) -> None:
        """Load token from environment and set expiry"""
        self._token = os.getenv('API_TOKEN')
        if not self._token:
            # Log but don't raise - allow Django to start in CI/CD environments
            print("⚠️  API_TOKEN not set in environment - running in test mode")
            self._token = None
            self._token_expiry = None
            self._initialized = True
            return
        
        # Set expiry to 24 hours from now
        self._token_expiry = datetime.now() + timedelta(hours=24)
        self._initialized = True
        
    @property
    def is_valid(self) -> bool:
        """Check if token is valid and not expired"""
        # Lazy initialize on first check
        if not self._initialized:
            self._refresh_token()
            
        if not self._token or not self._token_expiry:
            return False
        return datetime.now() < self._token_expiry

    def get_headers(self) -> dict:
        """Get authorization headers with valid token"""
        # Lazy initialize on first check
        if not self._initialized:
            self._refresh_token()
            
        if not self.is_valid:
            self._refresh_token()
        if not self._token:
            return {"error": "No API token available"}
        return {"Authorization": f"Token {self._token}"}

# Create singleton instance (lazy - doesn't fail on import)
token_validator = TokenValidator()