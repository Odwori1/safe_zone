#!/usr/bin/env python3
"""
Fix the crisis schemas to match the database structure
"""

# Read the current crisis schemas
with open('app/schemas/crisis.py', 'r') as f:
    content = f.read()

# Check if UserCrisisPreferencesResponse has id field
if 'id: UUID' not in content:
    print("❌ UserCrisisPreferencesResponse missing id field")
    
    # Find UserCrisisPreferencesResponse and add id field
    import re
    pattern = r'(class UserCrisisPreferencesResponse.*?)(\n    user_id: UUID)'
    replacement = r'\1\n    id: UUID\n\2'
    content = re.sub(pattern, replacement, content)
    print("✅ Added id field to UserCrisisPreferencesResponse")

# Write the updated content
with open('app/schemas/crisis.py', 'w') as f:
    f.write(content)

print("✅ Updated crisis schemas")
