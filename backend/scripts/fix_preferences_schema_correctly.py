#!/usr/bin/env python3
"""
Fix the UserCrisisPreferences schema to match the actual database structure
"""

# Read the schemas
with open('app/schemas/crisis.py', 'r') as f:
    content = f.read()

# Remove the id field from UserCrisisPreferencesInDB since the table doesn't have it
old_class = '''class UserCrisisPreferencesInDB(TimeStampedSchema):
    """User crisis preferences schema as stored in database"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    preferred_language: str
    country_code: Optional[str] = None
    emergency_contact_instructions: Optional[str] = None
    medical_information: Optional[str] = None
    consent_to_contact: bool'''

new_class = '''class UserCrisisPreferencesInDB(TimeStampedSchema):
    """User crisis preferences schema as stored in database"""
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    preferred_language: str
    country_code: Optional[str] = None
    emergency_contact_instructions: Optional[str] = None
    medical_information: Optional[str] = None
    consent_to_contact: bool'''

if old_class in content:
    content = content.replace(old_class, new_class)
    print("✅ Removed id field from UserCrisisPreferencesInDB (table doesn't have id column)")
else:
    print("⚠️ UserCrisisPreferencesInDB already fixed or has different structure")

# Write back
with open('app/schemas/crisis.py', 'w') as f:
    f.write(content)

print("✅ Schema now matches database structure")
