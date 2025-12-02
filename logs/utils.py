# Log CRUD operations
from core.auth.decorators import with_auth_retry
from core.auth.token_validator import token_validator
from core.utils.utility_files import api_request
from plants.models import Log

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