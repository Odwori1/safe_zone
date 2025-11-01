#!/usr/bin/env python3
"""
Force fix the UserCrisisPreferencesInDB schema
"""

# Read the crisis schemas
with open('app/schemas/crisis.py', 'r') as f:
    lines = f.readlines()

# Find and completely replace UserCrisisPreferencesInDB
fixed_lines = []
i = 0
in_problem_class = False
replaced = False

while i < len(lines):
    line = lines[i]
    
    # Look for the start of UserCrisisPreferencesInDB
    if 'class UserCrisisPreferencesInDB' in line and not replaced:
        print("Found UserCrisisPreferencesInDB - replacing completely...")
        fixed_lines.append('class UserCrisisPreferencesInDB(BaseModel):\n')
        fixed_lines.append('    """User crisis preferences schema as stored in database"""\n')
        fixed_lines.append('    model_config = ConfigDict(from_attributes=True)\n')
        fixed_lines.append('    \n')
        fixed_lines.append('    user_id: UUID\n')
        fixed_lines.append('    preferred_language: str\n')
        fixed_lines.append('    country_code: Optional[str] = None\n')
        fixed_lines.append('    emergency_contact_instructions: Optional[str] = None\n')
        fixed_lines.append('    medical_information: Optional[str] = None\n')
        fixed_lines.append('    consent_to_contact: bool\n')
        fixed_lines.append('    created_at: Optional[datetime] = None\n')
        fixed_lines.append('    updated_at: Optional[datetime] = None\n')
        fixed_lines.append('\n')
        
        # Skip the old class definition
        in_problem_class = True
        i += 1
        while i < len(lines) and (lines[i].strip() != '' or 'class ' not in lines[i]):
            i += 1
        replaced = True
        continue
    
    # Skip lines if we're in the old class
    if in_problem_class:
        if lines[i].strip() == '' or 'class ' in lines[i]:
            in_problem_class = False
        else:
            i += 1
            continue
    
    fixed_lines.append(line)
    i += 1

# Write the fixed content
with open('app/schemas/crisis.py', 'w') as f:
    f.writelines(fixed_lines)

print("✅ Force-fixed UserCrisisPreferencesInDB schema")
