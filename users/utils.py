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
    """Register a new user"""
    data = {
        "username": username,
        "email": email,
        "password": password
    }
    headers = kwargs.get("headers") or token_validator.get_headers()
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