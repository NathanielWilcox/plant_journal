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