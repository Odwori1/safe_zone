#!/usr/bin/env python3
"""
Check all crisis-related schemas for issues
"""

# Read the schemas
with open('app/schemas/crisis.py', 'r') as f:
    content = f.read()

# Check all response schemas that should have id fields
response_schemas = [
    'EmergencyContactResponse',
    'SafetyPlanResponse', 
    'WellnessCheckinResponse',
    'CrisisAlertResponse'
]

for schema in response_schemas:
    if f'class {schema}' in content:
        if 'id: UUID' not in content:
            print(f"❌ {schema} missing id field")
        else:
            print(f"✅ {schema} has id field")

print("\n🔍 Checking UserCrisisPreferences inheritance:")
if 'UserCrisisPreferencesResponse(UserCrisisPreferencesInDB)' in content:
    print("✅ UserCrisisPreferencesResponse inherits from UserCrisisPreferencesInDB")
else:
    print("❌ UserCrisisPreferencesResponse inheritance issue")

if 'id: UUID' in content and 'class UserCrisisPreferencesInDB' in content:
    print("✅ UserCrisisPreferencesInDB has id field")
else:
    print("❌ UserCrisisPreferencesInDB missing id field")
