"""
Root-level conftest.py that imports fixtures from tests/conftest.py
This ensures all fixtures are available to all test directories.
"""
import os
import django
from pathlib import Path

# Ensure Django is set up before running tests
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Import all fixtures from tests.conftest
from tests.conftest import (
    UserFactory, PlantFactory, LogFactory,
    api_client, authenticated_client,
    test_user, test_user_2,
    test_plant, test_plant_2,
    test_log, test_logs,
    api_client_with_user, api_client_with_user_2,
    valid_plant_data, valid_log_data, valid_user_data, valid_login_data
)

__all__ = [
    'UserFactory', 'PlantFactory', 'LogFactory',
    'api_client', 'authenticated_client',
    'test_user', 'test_user_2',
    'test_plant', 'test_plant_2',
    'test_log', 'test_logs',
    'api_client_with_user', 'api_client_with_user_2',
    'valid_plant_data', 'valid_log_data', 'valid_user_data', 'valid_login_data'
]
