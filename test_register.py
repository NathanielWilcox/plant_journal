#!/usr/bin/env python
"""Test registration endpoint"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

import requests
from django.conf import settings

API_URL = "http://127.0.0.1:8000/api/auth/register/"

# Test 1: Missing fields
print("Test 1: Missing email field")
response = requests.post(API_URL, json={"username": "testuser", "password": "testpass123"})
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}\n")

# Test 2: Valid registration
print("Test 2: Valid registration")
response = requests.post(API_URL, json={
    "username": "testuser2",
    "email": "test@example.com",
    "password": "testpass123"
})
print(f"Status: {response.status_code}")
print(f"Response keys: {response.json().keys() if response.status_code == 201 else response.json()}\n")

# Test 3: Duplicate username
print("Test 3: Duplicate username")
response = requests.post(API_URL, json={
    "username": "testuser2",
    "email": "test2@example.com",
    "password": "testpass123"
})
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
