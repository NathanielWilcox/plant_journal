import json, os
from typing import Dict, List, Optional
from core.settings import BASE_DIR
from plants.crud import create_plant, update_plant
from core.auth import token_validator
from core.auth.decorators import with_auth_retry
from core.utils.utility_files import api_request

CARE_DB_PATH = os.path.join(BASE_DIR, "plants", "care_db.json")

# --- Helper: update care info when category changes ---
def update_care_info(category: str) -> str:
    """Update care info based on category selection."""
    templates = load_plant_templates()
    category_info = templates["plants_by_category"].get(category, {})
    return {
        'watering_schedule': category_info.get('watering_schedule', ''),
        'sunlight_preference': category_info.get('sunlight_preference', ''),
        'placeholder_species': category_info.get('placeholder_species', '')
    }

# --- Load care_db.json and provide accessors ---
def load_plant_templates() -> Dict:
    """Load the plant templates from care_db.json"""
    json_path = os.path.join(os.path.dirname(__file__), 'care_db.json')
    with open(json_path, 'r') as f:
        return json.load(f)

# --- Accessor functions ---
def get_plant_template(category: str) -> Optional[Dict]:
    """Get care template for a category."""
    templates = load_plant_templates()
    return templates["plants_by_category"].get(category)

# --- Additional utility functions ---
def get_category_placeholder(category: str) -> str:
    """Return placeholder species for a category."""
    templates = load_plant_templates()
    category_info = templates["plants_by_category"].get(category, {})
    if isinstance(category_info, dict):
        return category_info.get("placeholder_species", "")
    return ""


# --- Enum accessors ---
def get_watering_schedules() -> List[str]:
    """Get list of valid watering schedules"""
    templates = load_plant_templates()
    return templates.get('watering_schedule_enum', [])

# --- Enum accessors ---
def get_sunlight_preferences() -> List[str]:
    """Get list of valid sunlight preferences"""
    templates = load_plant_templates()
    return templates.get('sunlight_preference_enum', [])

# --- Suggest care instructions ---
def suggest_plant_care(name: str, category: str = None) -> Optional[Dict]:
    """
    Suggest care instructions for a plant based on its name and optionally category.
    Returns a dictionary with watering_schedule and sunlight_preference if found.
    """
    templates = load_plant_templates()

    template = templates["plants_by_category"].get(category)
    if template:
        return {
            'watering_schedule': template['watering_schedule'],
            'sunlight_preference': template['sunlight_preference']
        }
    return None

def get_all_categories() -> List[str]:
    """Return all category names from care_db.json"""
    templates = load_plant_templates()
    return list(templates.get("plants_by_category", {}).keys())

def get_category_placeholder(category: str) -> str:
    """Return placeholder species for a given category"""
    templates = load_plant_templates()
    category_info = templates.get("plants_by_category", {}).get(category, {})
    return category_info.get("placeholder_species", "")

def handle_update(pid, category, care_level, location, pot_size):
    # Call your update_plant function and return the result
    return update_plant(
        plant_id=pid,
        category=category,
        care_level=care_level,
        location=location,
        pot_size=pot_size
    )

# ============================================================================
# UI HANDLER WRAPPERS (for Gradio interface)
# ============================================================================

def ui_load_user_plants(auth_state: Dict) -> tuple:
    """UI handler to load all user plants"""
    from core.utils.utility_files import is_authenticated, get_auth_headers
    
    if not is_authenticated(auth_state):
        return [], "Error: Not authenticated"
    
    headers = get_auth_headers(auth_state)
    result = api_request("GET", "/plants/", headers=headers)
    
    if isinstance(result, dict) and "error" in result:
        return [], f"Error: {result['error']}"
    
    plants_list = result if isinstance(result, list) else result.get("data", [])
    return plants_list, "Plants loaded successfully"

def ui_handle_create_plant(name: str, category: str, care_level: str, location: str, pot_size: str, auth_state: Dict) -> str:
    """UI handler to create a new plant"""
    from core.utils.utility_files import is_authenticated, get_auth_headers
    
    if not is_authenticated(auth_state):
        return "Error: Not authenticated"
    
    headers = get_auth_headers(auth_state)
    result = api_request(
        "POST",
        "/plants/",
        headers=headers,
        json={
            "name": name,
            "category": category,
            "care_level": care_level,
            "location": location,
            "pot_size": pot_size
        }
    )
    
    if isinstance(result, dict) and "error" in result:
        return f"Error: {result['error']}"
    
    return f"Plant '{name}' created successfully"

def ui_handle_update_plant(plant_id: int, category: str, care_level: str, location: str, pot_size: str, auth_state: Dict) -> str:
    """UI handler to update plant details"""
    from core.utils.utility_files import is_authenticated, get_auth_headers
    
    if not is_authenticated(auth_state):
        return "Error: Not authenticated"
    
    headers = get_auth_headers(auth_state)
    result = api_request(
        "patch",
        f"plants/{plant_id}/",
        headers=headers,
        json={
            "category": category,
            "care_level": care_level,
            "location": location,
            "pot_size": pot_size
        }
    )
    
    if isinstance(result, dict) and "error" in result:
        return f"Error: {result['error']}"
    
    return "Plant updated successfully"

def ui_handle_delete_plant(plant_id: int, confirmed: bool, auth_state: Dict) -> str:
    """UI handler to delete a plant - requires confirmation checkbox"""
    from core.utils.utility_files import is_authenticated, get_auth_headers
    
    if not is_authenticated(auth_state):
        return "❌ Error: Not authenticated"
    
    if not confirmed:
        return "⚠️ Please confirm deletion"
    
    headers = get_auth_headers(auth_state)
    result = api_request("delete", f"plants/{plant_id}/", headers=headers)
    
    if isinstance(result, dict) and "error" in result:
        return f"Error: {result['error']}"
    
    return "Plant deleted successfully"

