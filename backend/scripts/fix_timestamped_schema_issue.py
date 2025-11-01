#!/usr/bin/env python3
"""
Fix the TimeStampedSchema inheritance issue for UserCrisisPreferencesInDB
"""

# Read the crisis schemas
with open('app/schemas/crisis.py', 'r') as f:
    content = f.read()

# Replace UserCrisisPreferencesInDB to NOT inherit from TimeStampedSchema
# since the table doesn't have an id column
old_class = '''class UserCrisisPreferencesInDB(TimeStampedSchema):
    """User crisis preferences schema as stored in database"""
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    preferred_language: str
    country_code: Optional[str] = None
    emergency_contact_instructions: Optional[str] = None
    medical_information: Optional[str] = None
    consent_to_contact: bool'''

new_class = '''class UserCrisisPreferencesInDB(BaseModel):
    """User crisis preferences schema as stored in database"""
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    preferred_language: str
    country_code: Optional[str] = None
    emergency_contact_instructions: Optional[str] = None
    medical_information: Optional[str] = None
    consent_to_contact: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None'''

if old_class in content:
    content = content.replace(old_class, new_class)
    print("✅ Fixed UserCrisisPreferencesInDB to not inherit from TimeStampedSchema")
else:
    print("⚠️ UserCrisisPreferencesInDB already fixed or has different structure")

# Write back
with open('app/schemas/crisis.py', 'w') as f:
    f.write(content)

print("✅ Schema inheritance fixed")
