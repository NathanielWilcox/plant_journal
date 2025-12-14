#!/usr/bin/env python
"""
Direct test of registration endpoint to see error response
"""
import requests
import json

API_BASE = "http://127.0.0.1:8000/api"

# Test with invalid data
print("=" * 70)
print("Test 1: Missing email")
print("=" * 70)
response = requests.post(
    f"{API_BASE}/auth/register/",
    json={
        "username": "testuser123",
        "email": "",  # Missing
        "password": "password123"
    }
)
print(f"Status: {response.status_code}")
print(f"Body: {response.text}")
print(f"JSON: {response.json() if response.text else 'No content'}")

print("\n" + "=" * 70)
print("Test 2: Missing username")
print("=" * 70)
response = requests.post(
    f"{API_BASE}/auth/register/",
    json={
        "username": "",  # Missing
        "email": "test@example.com",
        "password": "password123"
    }
)
print(f"Status: {response.status_code}")
print(f"Body: {response.text}")
print(f"JSON: {response.json() if response.text else 'No content'}")

print("\n" + "=" * 70)
print("Test 3: Valid data (new user)")
print("=" * 70)
import random
rand_id = random.randint(10000, 99999)
response = requests.post(
    f"{API_BASE}/auth/register/",
    json={
        "username": f"newuser{rand_id}",
        "email": f"newuser{rand_id}@example.com",
        "password": "password123"
    }
)
print(f"Status: {response.status_code}")
print(f"Body: {response.text}")
print(f"JSON: {response.json() if response.text else 'No content'}")

print("\n" + "=" * 70)
print("Test 4: Duplicate username")
print("=" * 70)
response = requests.post(
    f"{API_BASE}/auth/register/",
    json={
        "username": f"newuser{rand_id}",  # Same as previous
        "email": f"anothermail{rand_id}@example.com",  # Different email
        "password": "password123"
    }
)
print(f"Status: {response.status_code}")
print(f"Body: {response.text}")
print(f"JSON: {response.json() if response.text else 'No content'}")
