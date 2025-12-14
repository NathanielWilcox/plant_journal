#!/usr/bin/env python
"""
Query all users from the database
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 70)
print("ALL USERS IN DATABASE")
print("=" * 70)

users = User.objects.all()
print(f"Total users: {users.count()}\n")

if users.exists():
    for user in users:
        print(f"ID: {user.id}")
        print(f"  Username: {user.username}")
        print(f"  Email: {user.email}")
        print(f"  Display Name: {user.display_name}")
        print(f"  Is Staff: {user.is_staff}")
        print(f"  Is Active: {user.is_active}")
        print(f"  Date Joined: {user.date_joined}")
        print()
else:
    print("No users found")
