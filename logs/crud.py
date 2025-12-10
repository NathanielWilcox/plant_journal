from core.auth.decorators import with_auth_retry
from core.auth.token_validator import token_validator
from core.utils.utility_files import api_request
from plants.models import Log

# Log CRUD operations

@with_auth_retry(max_retries=3)
def create_log(plant_id, log_type, sunlight_hours=None,
               photo=None, health_issue=None, **kwargs):
    """Create a new log entry"""
    data = {
        "plant": plant_id,
        "log_type": log_type
    }
    if sunlight_hours is not None:
        data["sunlight_hours"] = sunlight_hours
    if health_issue is not None:
        data["health_issue"] = health_issue

    headers = kwargs.get("headers") or token_validator.get_headers()
    params = kwargs.get("params")

    result = api_request("post", "logs/", json=data, headers=headers, params=params)
    if isinstance(result, dict) and "error" in result:
        return result

    log_data = result.get("data", result)

    return log_data


@with_auth_retry(max_retries=3)
def list_logs(**kwargs):
    """List all logs"""
    headers = kwargs.get("headers") or token_validator.get_headers()
    params = kwargs.get("params")

    result = api_request("get", "logs/", headers=headers, params=params)
    if isinstance(result, dict) and "error" in result:
        return result
    return {"data": result.get("data", result)}

@with_auth_retry(max_retries=3)
def list_logs_for_plant(plant_id, **kwargs):
    """List all logs for a specific plant"""
    headers = kwargs.get("headers") or token_validator.get_headers()
    result = api_request('get', f'plants/{plant_id}/logs/', headers=headers, params=kwargs)

    if isinstance(result, dict) and "error" in result:
        return result

    # Expecting a list of logs (or wrapped in data)
    if isinstance(result, dict) and "data" in result:
        return {"data": result["data"]}
    if isinstance(result, list):
        return {"data": result}

    return {"data": []}

@with_auth_retry(max_retries=3)
def update_log(log_id, log_type, water_amount=None, sunlight_hours=None, **kwargs):
    """Update an existing log entry"""
    data = {
        "log_type": log_type,
    }
    if water_amount is not None:
        data["water_amount"] = water_amount
    if sunlight_hours is not None:
        data["sunlight_hours"] = sunlight_hours

    headers = kwargs.get("headers") or token_validator.get_headers()
    params = kwargs.get("params")

    result = api_request("patch", f"logs/{log_id}/", json=data, headers=headers, params=params)
    if isinstance(result, dict) and "error" in result:
        return result

    log_data = result.get("data", result)

    return log_data

# --- Delete log function (commented out for now because why would you delete a log) ---
# @with_auth_retry(max_retries=3)
# def delete_log(log_id, **kwargs):
#     """Delete a log entry (photos auto-deleted by backend)"""
#     headers = kwargs.get("headers") or token_validator.get_headers()
#     params = kwargs.get("params")

#     result = api_request("delete", f"logs/{log_id}/", headers=headers, params=params)
#     if isinstance(result, dict) and "error" in result:
#         return result
#     return {"success": "Log deleted successfully"}
