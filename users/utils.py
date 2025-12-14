import json, os
from typing import Dict, List, Optional
import requests
from core.settings import API_BASE_URL, BASE_DIR
from core.utils.error_handling_standerizer import format_error_response, handle_api_response
from plants.utils import load_plant_templates
from users.crud import create_user, update_user
from core.auth import token_validator
from core.auth.decorators import with_auth_retry
from core.utils.utility_files import api_request

# --- Helper: update care info when category changes --- API wrapper
# Use api_request for standardized error handling and retries
# For User Management
def login_user(username: str, password: str) -> Dict:
    """Login user via API endpoint - takes username/password, returns token.
    NO auth required - public endpoint.
    """
    data = {"username": username, "password": password}
    result = api_request("post", "auth/login/", json=data)
    return result
    
@with_auth_retry(max_retries=3)
def get_user_account_details(**kwargs) -> Dict:
    """Get current user account details via /users/me/ endpoint"""
    headers = kwargs.get("headers") or token_validator.get_headers()
    result = api_request("get", "users/me/", headers=headers)
    return result

def register_user(
    username: str,
    email: str,
    password: str,
    **kwargs
) -> Dict:
    """Register a new user via API endpoint - NO authentication required.
    User is automatically logged in after registration.
    """
    data = {
        "username": username,
        "email": email,
        "password": password
    }
    result = api_request("post", "auth/register/", json=data)
    return result

@with_auth_retry(max_retries=3)
def update_user_account(
    email: Optional[str] = None,
    password: Optional[str] = None,
    username: Optional[str] = None,
    display_name: Optional[str] = None,
    **kwargs
) -> Dict:
    """Update current user account details via /users/me/ endpoint (PATCH)"""
    data = {}
    if email is not None:
        data["email"] = email
    if password is not None:
        data["password"] = password
    if username is not None:
        data["username"] = username
    if display_name is not None:
        data["display_name"] = display_name

    headers = kwargs.get("headers") or token_validator.get_headers()
    result = api_request("patch", "users/me/", json=data, headers=headers)
    return result

@with_auth_retry(max_retries=3)
def logout_user(**kwargs) -> Dict:
    """Logout user by state reset, no server-side action"""
    headers = kwargs.get("headers") or token_validator.get_headers()
    result = api_request("post", "auth/logout/", headers=headers)
    return result

@with_auth_retry(max_retries=3)
def delete_user_account(**kwargs) -> Dict:
    """Delete current user account via /users/me/ endpoint"""
    headers = kwargs.get("headers") or token_validator.get_headers()
    result = api_request("delete", "users/me/", headers=headers)
    return result

@with_auth_retry(max_retries=3)
def validate_user_token(token: str) -> Dict:
    """Validate JWT token and return user info or error dict"""
    headers = {"Authorization": f"Bearer {token}"}
    result = api_request("post", "auth/validate/token/", headers=headers)
    return result


# ============================================================================
# UI HANDLER WRAPPERS (for Gradio interface)
# ============================================================================

def ui_handle_login(username: str, password: str, auth_state: Dict) -> tuple:
    """UI handler for user login - updates auth_state with token and returns updated state + message"""
    result = login_user(username, password)
    
    if isinstance(result, dict) and "error" in result:
        return auth_state, f"❌ Error: {result['error']}"
    
    token = result.get("token") if isinstance(result, dict) else result
    user_data = result.get("user") if isinstance(result, dict) else None
    
    # Update auth_state with token and user info
    auth_state["token"] = token
    auth_state["user"] = user_data
    
    return auth_state, "✅ Login successful!"

def ui_handle_register(username: str, email: str, password: str, password_confirm: str, auth_state: Dict) -> tuple:
    """UI handler for user registration"""
    if password != password_confirm:
        return auth_state, "❌ Passwords do not match"
    
    if not username or not email or not password:
        return auth_state, "❌ All fields are required"
    
    result = register_user(username, email, password)
    
    if isinstance(result, dict) and "error" in result:
        return auth_state, f"❌ Error: {result['error']}"
    
    return auth_state, "✅ Registration successful! Please login."

def ui_load_account_details(auth_state: Dict) -> dict:
    """UI handler to load user account details"""
    from core.utils.utility_files import is_authenticated, get_auth_headers

    if not is_authenticated(auth_state):
        return {"error": "Not authenticated"}

    headers = get_auth_headers(auth_state)
    result = get_user_account_details(headers=headers)

    if isinstance(result, dict) and "error" in result:
        return {"error": result['error']}

    # result should be a dict with user data
    return result if isinstance(result, dict) else {}

def ui_handle_account_update(email: str, password: str, username: str, display_name: str, auth_state: Dict) -> str:
    """UI handler to update user account"""
    from core.utils.utility_files import is_authenticated, get_auth_headers

    if not is_authenticated(auth_state):
        return "❌ Not authenticated"

    headers = get_auth_headers(auth_state)
    result = update_user_account(
        email=email if email else None,
        password=password if password else None,
        username=username if username else None,
        display_name=display_name if display_name else None,
        headers=headers
    )
    
    if isinstance(result, dict) and "error" in result:
        return f"❌ Error: {result['error']}"
    
    return "Account updated successfully"

def ui_handle_logout(auth_state: Dict) -> tuple:
    """UI handler for user logout - clears auth_state and returns cleared state + message"""
    from core.utils.utility_files import is_authenticated, get_auth_headers, init_auth_state
    
    if not is_authenticated(auth_state):
        return auth_state, "⚠️ Not logged in"
    
    headers = get_auth_headers(auth_state)
    result = logout_user(headers=headers)
    
    if isinstance(result, dict) and "error" in result:
        return auth_state, f"❌ Error: {result['error']}"
    
    # Clear auth state
    cleared_state = init_auth_state()
    return cleared_state, "✅ Logged out successfully"

def ui_handle_delete_account(confirmed: bool, auth_state: Dict) -> tuple:
    """UI handler to delete user account - requires confirmation checkbox"""
    from core.utils.utility_files import is_authenticated, get_auth_headers, init_auth_state

    if not is_authenticated(auth_state):
        return auth_state, "❌ Not authenticated"

    if not confirmed:
        return auth_state, "⚠️ Please confirm deletion"

    headers = get_auth_headers(auth_state)
    result = delete_user_account(headers=headers)

    if isinstance(result, dict) and "error" in result:
        return auth_state, f"❌ Error: {result['error']}"

    # Clear auth state after deletion
    cleared_state = init_auth_state()
    return cleared_state, "✅ Account deleted successfully"