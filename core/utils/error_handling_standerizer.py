from typing import Dict, Any, Optional
from requests import Response
from django.core.exceptions import ValidationError

class APIError(Exception):
    """Base exception for API errors"""
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

def handle_api_response(response: Response) -> Dict[str, Any]:
    """
    Standardized API response handler
    Returns dict with success/error information
    """
    try:
        if response.status_code in (200, 201):
            print("Successful API Response:", response.json())
            return {"success": True, "data": response.json()}
        elif response.status_code == 204:
            print("No Content Response")
            return {"success": True, "data": None}
        elif response.status_code == 400:
            # Bad request - try to extract meaningful error message
            try:
                error_data = response.json()
                print(f"[DEBUG] 400 error_data: {error_data}")
                # Handle various error formats
                if isinstance(error_data, dict):
                    # Check if there's an "error" key (custom format)
                    if "error" in error_data:
                        return {"error": str(error_data["error"]), "status_code": 400}
                    # DRF returns field errors as dict like {"field": ["error message"]}
                    error_msg = next(iter(error_data.values())) if error_data else "Invalid input"
                    if isinstance(error_msg, list):
                        error_msg = error_msg[0]
                    print(f"[DEBUG] Extracted error message: {error_msg}")
                    return {"error": str(error_msg), "status_code": 400}
                else:
                    return {"error": "Invalid input", "status_code": 400}
            except Exception as e:
                print(f"[DEBUG] Exception in 400 handler: {e}, response.text: {response.text}")
                return {"error": response.text or "Bad request", "status_code": 400}
        elif response.status_code == 401:
            print("Authentication failed - token expired or invalid")
            return {"error": "Unauthorized", "status_code": 401, "is_auth_error": True}
        elif response.status_code == 404:
            print("Resource not found")
            return {"error": "Resource not found", "status_code": 404}
        else:
            return {
                "error": f"API error: {response.status_code}",
                "details": response.text,
                "status_code": response.status_code
            }
    except Exception as e:
        print("Error handling API response:", e)
        return {"error": str(e), "status_code": 500}

def format_error_response(error: Exception) -> Dict[str, Any]:
    """
    Standardized error response formatter
    """
    if isinstance(error, ValidationError):
        print("Validation Error:", error)
        return {"error": "Validation Error", "details": str(error)}
    elif isinstance(error, APIError):
        print("API IsInstance Error:", error)
        return {"error": error.message, "status_code": error.status_code}
    else:
        print("Unhandled Exception:", error)
        return {"error": str(error), "status_code": 500}