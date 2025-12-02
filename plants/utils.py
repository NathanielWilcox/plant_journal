import json, os
from typing import Dict, List, Optional
from core.settings import BASE_DIR
from plants.crud import create_plant, update_plant
from core.auth import token_validator
from core.auth.decorators import with_auth_retry
from core.utils.utility_files import api_request

CARE_DB_PATH = os.path.join(BASE_DIR, "plants", "care_db.json")

# --- Helper: update care info when species changes ---
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

