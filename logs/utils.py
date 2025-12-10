# Log CRUD operations
from core.auth.decorators import with_auth_retry
from core.auth.token_validator import token_validator
from core.utils.utility_files import api_request
from plants.models import Log
from .crud import create_log, update_log, list_logs_for_plant

# --- Helper: retrieve available log types ---
@with_auth_retry(max_retries=3)
def get_log_types(**kwargs):
    """Retrieve available log types from the backend"""
    headers = kwargs.get("headers") or token_validator.get_headers()
    params = kwargs.get("params")

    result = api_request("get", "logs/log_types/", headers=headers, params=params)
    if isinstance(result, dict) and "error" in result:
        return result
    return {"data": result.get("data", result)}

# --- Normalize log data function ---
@with_auth_retry(max_retries=3)
def normalize_log_data(log_data, **kwargs):
    """Normalize log data structure for frontend consumption"""
    if not isinstance(log_data, dict):
        return {"error": "Invalid log data format"}

    normalized = {
        "id": log_data.get("id"),
        "plant_id": log_data.get("plant"),
        "log_type": log_data.get("log_type"),
        "timestamp": log_data.get("timestamp"),
        "sunlight_hours": log_data.get("sunlight_hours"),
        "health_issue": log_data.get("health_issue"),
    }
    return normalized

# --- Search plant issues function ---
@with_auth_retry(max_retries=3)
def search_plant_issues(query, **kwargs):
    """Search for plant health issues in existing logs"""
    if not query:
        return []

    headers = kwargs.get("headers") or token_validator.get_headers()
    params = kwargs.get("params")

    result = api_request("get", "logs/", headers=headers, params=params)
    if isinstance(result, dict) and "error" in result:
        return []

    issues_list = []
    for log in result if isinstance(result, list) else result.get("data", []):
        if log.get("log_type") == "health_issue":
            issues_list.append({
                "id": log["id"],
                "name": f"Health issue with {log.get('plant_name')}",
                "date": log.get("timestamp")
            })
    return issues_list
# --- Check plant exists function ---
@with_auth_retry(max_retries=3)
def check_plant_exists(plant_id, **kwargs):
    """Check if a plant exists by ID, returning structured result."""

    # Guard against None, empty, non-integer, or <= 0
    if plant_id is None:
        return {"exists": False, "error": "No plant ID provided"}
    try:
        pid = int(plant_id)
    except (TypeError, ValueError):
        return {"exists": False, "error": f"Invalid plant ID: {plant_id}"}
    if pid <= 0:
        return {"exists": False, "error": f"Invalid plant ID: {pid}"}

    # Merge headers safely
    headers = kwargs.get("headers") or token_validator.get_headers()
    params = kwargs.get("params")

    # Query backend via centralized helper
    result = api_request("get", f"plants/{pid}/", headers=headers, params=params)

    # Normalize return
    if isinstance(result, dict) and "error" in result:
        # Distinguish 404 vs other errors if your api_request includes status_code
        if result.get("status_code") == 404:
            return {"exists": False, "error": f"Plant {pid} not found"}
        return {"exists": False, "error": f"Lookup failed: {result.get('error')}"}

    return {"exists": True, "plant": result.get("data", result)}

# ============================================================================
# UI HANDLER FUNCTIONS FOR GRADIO
# ============================================================================

def ui_check_plant(plant_id: float, auth_state: dict) -> dict:
    """UI handler to check if plant exists - returns plant info or error dict"""
    from core.utils.utility_files import get_auth_headers
    
    if not plant_id or plant_id <= 0:
        return {"error": "Invalid plant ID"}
    
    headers = get_auth_headers(auth_state)
    result = check_plant_exists(plant_id=int(plant_id), headers=headers)
    return result

def ui_handle_create_log(plant_id: float, log_type: str, sunlight_hours: float, auth_state: dict) -> str:
    """UI handler for creating a log - returns status_message"""
    from core.utils.utility_files import is_authenticated, get_auth_headers
    
    if not is_authenticated(auth_state):
        return "❌ Not authenticated"
    
    if not plant_id or plant_id <= 0:
        return "⚠️ Valid plant ID is required"
    
    headers = get_auth_headers(auth_state)
    result = create_log(
        plant_id=int(plant_id),
        log_type=log_type,
        sunlight_hours=sunlight_hours if sunlight_hours else None,
        headers=headers
    )
    
    if isinstance(result, dict) and "error" in result:
        return f"❌ Failed to create log: {result['error']}"
    return "✅ Log created successfully!"

def ui_handle_update_log(log_id: float, log_type: str, sunlight_hours: float, auth_state: dict) -> str:
    """UI handler for updating a log - returns status_message"""
    from core.utils.utility_files import is_authenticated, get_auth_headers
    
    if not is_authenticated(auth_state):
        return "❌ Not authenticated"
    
    if not log_id or log_id <= 0:
        return "⚠️ Valid log ID is required"
    
    headers = get_auth_headers(auth_state)
    result = update_log(
        log_id=int(log_id),
        log_type=log_type,
        sunlight_hours=sunlight_hours if sunlight_hours else None,
        headers=headers
    )
    
    if isinstance(result, dict) and "error" in result:
        return f"❌ Failed to update log: {result['error']}"
    return "✅ Log updated successfully!"

def ui_load_plant_logs(plant_id: float, auth_state: dict) -> dict:
    """UI handler to load logs for a plant - returns logs dict or error"""
    from core.utils.utility_files import is_authenticated, get_auth_headers
    
    if not plant_id or plant_id <= 0:
        return {"error": "Invalid plant ID"}
    
    if not is_authenticated(auth_state):
        return {"error": "Not authenticated"}
    
    headers = get_auth_headers(auth_state)
    result = list_logs_for_plant(plant_id=int(plant_id), headers=headers)
    return result
