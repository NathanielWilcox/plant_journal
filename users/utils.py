import json, os
import token
from typing import Dict, List, Optional
import requests
from core.settings import API_BASE_URL, BASE_DIR
from core.utils.error_handling_standerizer import format_error_response, handle_api_response
from plants.utils import load_plant_templates
from users.crud import create_user, update_user
from core.auth import token_validator
from core.auth.decorators import with_auth_retry
from core.utils.utility_files import api_request

# --- Helper: update care info when species changes --- API wrapper
# Use api_request for standardized error handling and retries
# For User Management
@with_auth_retry(max_retries=3)
def login_user(username: str, password: str) -> Dict:
    """Login user and return JWT token or error dict"""
    data = {"username": username, "password": password}
    try:
        response = requests.post(
           f"{API_BASE_URL.rstrip('/')}/auth/login/",
            data=data
        )
        result = handle_api_response(response)
        if "error" in result:
            return result
        return result.get("data")
    except Exception as e:
        return format_error_response(e)
    
@with_auth_retry(max_retries=3)
def get_user_account_details(user_id: int, **kwargs) -> Dict:
    """Get user account details by user ID"""
    headers = kwargs.get("headers") or token_validator.get_headers()
    result = api_request("get", f"users/{user_id}/", headers=headers)
    return result

@with_auth_retry(max_retries=3)
def register_user(
    username: str,
    email: str,
    password: str,
    **kwargs
) -> Dict:
    """Register a new user - NO authentication required"""
    data = {
        "username": username,
        "email": email,
        "password": password
    }
    headers = kwargs.get("headers") or {}
    result = api_request("post", "users/", json=data, headers=headers)
    return result

@with_auth_retry(max_retries=3)
def update_user_account(
    user_id: int,
    email: Optional[str] = None,
    password: Optional[str] = None,
    **kwargs
) -> Dict:
    """Update user account details"""
    data = {}
    if email is not None:
        data["email"] = email
    if password is not None:
        data["password"] = password

    headers = kwargs.get("headers") or token_validator.get_headers()
    result = api_request("put", f"users/{user_id}/", json=data, headers=headers)
    return result

@with_auth_retry(max_retries=3)
def logout_user(**kwargs) -> Dict:
    """Logout user by state reset, no server-side action"""
    headers = kwargs.get("headers") or token_validator.get_headers()
    result = api_request("post", "auth/logout/", headers=headers)
    return result

@with_auth_retry(max_retries=3)
def delete_user_account(user_id: int, **kwargs) -> Dict:
    """Delete user account by user ID"""
    headers = kwargs.get("headers") or token_validator.get_headers()
    result = api_request("delete", f"users/{user_id}/", headers=headers)
    return result

@with_auth_retry(max_retries=3)
def validate_user_token(token: str) -> Dict:
    """Validate JWT token and return user info or error dict"""
    headers = {"Authorization": f"Bearer {token}"}
    result = api_request("post", "auth/validate/token/", headers=headers)
    return result

def validate_user_information(username: str, email: str) -> Dict:
    """Validate user information before registration"""
    try:
        response = requests.post(
            f"{API_BASE_URL.rstrip('/')}/token/verify/", 
            data={"token": token}
            )
        result = handle_api_response(response)
        if "error" in result:
            return result
        return result.get("data")
    except Exception as e:
        return format_error_response(e)
    
@with_auth_retry(max_retries=3)
def refresh_user_token(old_token: str) -> Dict:
    """Refresh JWT token using the API and return new token or error dict"""
    try:
        response = requests.post(
            f"{API_BASE_URL.rstrip('/')}/token/refresh/", 
            data={"refresh": old_token}
            )
        return handle_api_response(response)
    except Exception as e:
        return format_error_response(e)

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
    """UI handler to load user account details - extracts user_id from auth_state"""
    from core.utils.utility_files import is_authenticated, get_auth_headers
    
    if not is_authenticated(auth_state):
        return {"error": "Not authenticated"}
    
    user_data = auth_state.get("user")
    if not user_data or not user_data.get("id"):
        return {"error": "User ID not found in session"}
    
    headers = get_auth_headers(auth_state)
    result = get_user_account_details(user_data["id"], headers=headers)
    
    if isinstance(result, dict) and "error" in result:
        return {"error": result['error']}
    
    account_data = result if isinstance(result, dict) else result.get("data", {})
    return account_data, "Account details loaded"

def ui_handle_account_update(email: str, password: str, auth_state: Dict) -> str:
    """UI handler to update user account - extracts user_id from auth_state"""
    from core.utils.utility_files import is_authenticated, get_auth_headers
    
    if not is_authenticated(auth_state):
        return "❌ Not authenticated"
    
    user_data = auth_state.get("user")
    if not user_data or not user_data.get("id"):
        return "❌ User ID not found in session"
    
    headers = get_auth_headers(auth_state)
    result = update_user_account(
        user_data["id"],
        email=email if email else None,
        password=password if password else None,
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
    
    user_data = auth_state.get("user")
    if not user_data or not user_data.get("id"):
        return auth_state, "❌ User ID not found in session"
    
    headers = get_auth_headers(auth_state)
    result = delete_user_account(user_data["id"], headers=headers)
    
    if isinstance(result, dict) and "error" in result:
        return auth_state, f"❌ Error: {result['error']}"
    
    # Clear auth state after deletion
    cleared_state = init_auth_state()
    return cleared_state, "✅ Account deleted successfully"