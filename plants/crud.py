from core.auth import token_validator
from core.auth.decorators import with_auth_retry
from core.utils.utility_files import api_request
from .models import Plant

# Plant CRUD operations

@with_auth_retry(max_retries=3)
def create_plant(
    name,
    category,
    care_level=None,
    watering_schedule=None,
    sunlight_preference=None,
    location=None,
    pot_size="medium",
    owner_id=None,
    **kwargs
):
    """Create a new plant entry with validation against Plant model choices."""

    # Convert choices into sets for quick lookup
    valid_categories = {c[0] for c in Plant.CATEGORY_CHOICES}
    valid_pot_sizes = {p[0] for p in Plant.POT_SIZE_CHOICES}
    valid_watering = {w[0] for w in Plant.WATERING_SCHEDULE_CHOICES}
    valid_sunlight = {s[0] for s in Plant.SUNLIGHT_PREFERENCE_CHOICES}

    # Validate inputs
    if category not in valid_categories:
        return {"error": f"Invalid category '{category}'", "status_code": 400}
    if pot_size not in valid_pot_sizes:
        return {"error": f"Invalid pot size '{pot_size}'", "status_code": 400}
    if watering_schedule and watering_schedule not in valid_watering:
        return {"error": f"Invalid watering schedule '{watering_schedule}'", "status_code": 400}
    if sunlight_preference and sunlight_preference not in valid_sunlight:
        return {"error": f"Invalid sunlight preference '{sunlight_preference}'", "status_code": 400}

    # Build payload, dropping None values
    data = {
        "name": name,
        "category": category,
        "care_level": care_level,
        "watering_schedule": watering_schedule,
        "sunlight_preference": sunlight_preference,
        "location": location,
        "pot_size": pot_size,
        "owner": owner_id,
    }
    data = {k: v for k, v in data.items() if v is not None}

    # Merge headers safely
    headers = kwargs.get("headers") or token_validator.get_headers()
    params = kwargs.get("params")

    # Make request
    result = api_request("post", "plants/", json=data, headers=headers, params=params)

    return result

@with_auth_retry(max_retries=3)
def list_plants(**kwargs):
    """List all plants - returns list of plants or error dict"""

    # Merge headers safely: use decorator-injected headers if present
    headers = kwargs.get("headers") or token_validator.get_headers()
    # Only forward params if explicitly provided
    params = kwargs.get("params")

    result = api_request("get", "plants/", headers=headers, params=params)

    # api_request already extracts data, so result is the list directly
    if isinstance(result, dict) and "error" in result:
        return result  # Return error as-is
    
    # Result is the list of plants (or wrapped in data key from serializer)
    if isinstance(result, dict) and "data" in result:
        return result["data"]
    elif isinstance(result, list):
        return result
    else:
        return []  # Empty list if unexpected format

@with_auth_retry(max_retries=3)
def update_plant(
    plant_id,
    category=None,
    care_level=None,
    location=None,
    pot_size=None,
    **kwargs
):
    """Update an existing plant with validation against Plant model choices."""

    valid_categories = {c[0] for c in Plant.CATEGORY_CHOICES}
    valid_pot_sizes = {p[0] for p in Plant.POT_SIZE_CHOICES}

    # Only validate if a non-empty value is provided
    if category not in (None, "") and category not in valid_categories:
        return {"error": f"Invalid category '{category}'", "status_code": 400}
    if pot_size not in (None, "") and pot_size not in valid_pot_sizes:
        return {"error": f"Invalid pot size '{pot_size}'", "status_code": 400}

    # Build payload, stripping out None and empty strings
    data = {
        "category": category,
        "care_level": care_level,
        "location": location,
        "pot_size": pot_size,
    }
    data = {k: v for k, v in data.items() if v not in (None, "", [])}

    headers = kwargs.get("headers") or token_validator.get_headers()
    params = kwargs.get("params")

    result = api_request("patch", f"plants/{plant_id}/", json=data, headers=headers, params=params)
    return result


@with_auth_retry(max_retries=3)
def delete_plant(plant_id, **kwargs):
    """Delete a plant and cascade logs/photos."""

    headers = kwargs.get("headers") or token_validator.get_headers()
    params = kwargs.get("params")

    result = api_request("delete", f"plants/{plant_id}/", headers=headers, params=params)

    return result

