#!/usr/bin/env python3
"""
Fix the UserCrisisPreferencesResponse schema properly
"""

# Read the schemas
with open('app/schemas/crisis.py', 'r') as f:
    content = f.read()

# Find and fix UserCrisisPreferencesInDB to include id field
if 'class UserCrisisPreferencesInDB' in content and 'id: UUID' not in content:
    print("Fixing UserCrisisPreferencesInDB...")
    
    # Replace the entire class definition
    old_class = '''class UserCrisisPreferencesInDB(UserCrisisPreferencesBase):
    """User crisis preferences schema for database records"""
    user_id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True'''
    
    new_class = '''class UserCrisisPreferencesInDB(UserCrisisPreferencesBase):
    """User crisis preferences schema for database records"""
    id: UUID
    user_id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True'''
    
    content = content.replace(old_class, new_class)
    print("✅ Fixed UserCrisisPreferencesInDB")

# Write back
with open('app/schemas/crisis.py', 'w') as f:
    f.write(content)

print("✅ Schema fixed - UserCrisisPreferencesInDB now includes id field")
