# Helper functions
from ast import Dict
from email import parser
from pytz import timezone
import requests
from tomlkit import datetime
from core.auth import token_validator
from core.auth.decorators import with_auth_retry
from core.utils.error_handling_standerizer import format_error_response, handle_api_response
from core.settings import API_BASE_URL

@with_auth_retry(max_retries=3)
def api_request(method: str, path: str, **kwargs):
    """Centralized API request helper that uses standardized response handling.

    - method: 'get'|'post'|'put'|'delete' etc.
    - path: API path relative to API_BASE_URL (e.g. 'plants/', 'plants/12/')
    - kwargs: passed directly to requests.request (json=..., files=..., params=...)
    Returns: parsed data on success, or a dict with 'error' (and optional details/status_code).
    """
    try:
        url = f"{API_BASE_URL.rstrip('/')}/{path.lstrip('/')}"
        headers = kwargs.pop("headers", {})
        response = requests.request(method, url, headers=headers, **kwargs)
        result = handle_api_response(response)   # uses your centralized handler
        if "error" in result:
            return result
        return result.get("data")
    except Exception as e:
        return format_error_response(e)

@with_auth_retry(max_retries=3)
def format_datetime(dt):
    """Format datetime for UI display (safe for str or datetime)"""
    if not dt:
        return None
    if isinstance(dt, str):
        try:
            dt = parser.isoparse(dt)
        except Exception:
            return dt  # fallback: return raw string
    return dt.astimezone(timezone.get_current_timezone()).strftime('%Y-%m-%d %H:%M:%S')

def parse_datetime(dt_str):
    """Parse datetime from UI input (robust)"""
    if not dt_str:
        return None
    try:
        dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        try:
            dt = parser.parse(dt_str)
        except Exception:
            return None
    return timezone.make_aware(dt)

def refresh_jwt_token(old_token: str) -> Dict:
    """Refresh JWT token using the API and return new token or error dict"""
    try:
        headers = {"Authorization": f"Bearer {old_token}"}
        response = requests.post(
            f"{API_BASE_URL.rstrip('/')}/auth/refresh/",
            headers=headers
        )
        result = handle_api_response(response)
        if "error" in result:
            return result
        return result.get("data")
    except Exception as e:
        return format_error_response(e)

# ============================================================================
# UI STATE MANAGEMENT HELPERS
# ============================================================================

def init_auth_state():
    """Initialize authentication state"""
    return {"token": None, "user": None}

def is_authenticated(auth_state):
    """Check if user is authenticated"""
    return auth_state.get("token") is not None

def get_auth_headers(auth_state):
    """Get authorization headers from token"""
    token = auth_state.get("token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}