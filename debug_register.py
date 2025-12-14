#!/usr/bin/env python
"""Debug registration"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Patch api_request to log
import core.utils.utility_files as uf
original_api_request = uf.api_request.__wrapped__  # Get the unwrapped version

def debug_api_request(method, path, **kwargs):
    print(f"\n[API] {method.upper()} {path}")
    result = original_api_request(method, path, **kwargs)
    print(f"[RESULT] {result}")
    return result

uf.api_request = debug_api_request

# Now test registration
from users.utils import register_user

print("=" * 70)
print("Testing registration with missing email...")
print("=" * 70)

result = register_user("testuser", "", "password123")
print(f"\nFinal result: {result}")
print(f"Type: {type(result)}")
