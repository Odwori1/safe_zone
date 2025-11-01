#!/usr/bin/env python3
"""
Deep investigation of the preferences schema issue
"""

# Read the crisis schemas
with open('app/schemas/crisis.py', 'r') as f:
    content = f.read()

print("🔍 Current UserCrisisPreferencesInDB schema:")
import re
match = re.search(r'class UserCrisisPreferencesInDB.*?(?=class|\Z)', content, re.DOTALL)
if match:
    print(match.group(0))

print("\n🔍 Checking what TimeStampedSchema contains:")
# Find TimeStampedSchema definition
with open('app/schemas/base.py', 'r') as f:
    base_content = f.read()
    ts_match = re.search(r'class TimeStampedSchema.*?(?=class|\Z)', base_content, re.DOTALL)
    if ts_match:
        print(ts_match.group(0))

print("\n🔍 Checking UserCrisisPreferencesResponse inheritance:")
if 'UserCrisisPreferencesResponse(UserCrisisPreferencesInDB)' in content:
    print("✅ Response inherits from InDB")
else:
    print("❌ Response inheritance issue")

# Let's manually test the schema creation
print("\n🧪 Manual schema test:")
from app.schemas.crisis import UserCrisisPreferencesResponse

# Create test data that matches what the database returns
test_data = {
    'user_id': '8808956b-11fb-4253-91ef-98b9902ffbc8',
    'preferred_language': 'en',
    'country_code': 'US',
    'emergency_contact_instructions': 'Test',
    'medical_information': 'Test',
    'consent_to_contact': True,
    'created_at': '2025-11-01T08:14:54.018941+00:00',
    'updated_at': '2025-11-01T08:30:35.124540+00:00'
}

try:
    response = UserCrisisPreferencesResponse(**test_data)
    print("✅ Manual test SUCCESS!")
except Exception as e:
    print(f"❌ Manual test FAILED: {e}")
