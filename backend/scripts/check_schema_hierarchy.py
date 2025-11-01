#!/usr/bin/env python3
"""
Check the schema inheritance hierarchy
"""

# Read the schemas file
with open('app/schemas/crisis.py', 'r') as f:
    content = f.read()

# Find all UserCrisisPreferences related classes
import re

print("🔍 UserCrisisPreferences Schema Hierarchy:")
patterns = [
    r'class UserCrisisPreferencesBase.*?\n\n',
    r'class UserCrisisPreferencesCreate.*?\n\n', 
    r'class UserCrisisPreferencesInDB.*?\n\n',
    r'class UserCrisisPreferencesResponse.*?\n\n'
]

for pattern in patterns:
    matches = re.findall(pattern, content, re.DOTALL)
    for match in matches:
        print("=" * 50)
        print(match)
