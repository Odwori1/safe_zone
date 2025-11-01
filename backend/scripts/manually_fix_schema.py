#!/usr/bin/env python3
"""
Manually fix the UserCrisisPreferencesInDB schema
"""

# Read the schemas file
with open('app/schemas/crisis.py', 'r') as f:
    lines = f.readlines()

# Find and fix the UserCrisisPreferencesInDB class
fixed_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    fixed_lines.append(line)
    
    # Look for UserCrisisPreferencesInDB class
    if 'class UserCrisisPreferencesInDB' in line:
        # Skip any id field lines in this class
        i += 1
        while i < len(lines) and not lines[i].strip().startswith('class '):
            if 'id: UUID' not in lines[i]:
                fixed_lines.append(lines[i])
            i += 1
        continue
    
    i += 1

# Write the fixed content
with open('app/schemas/crisis.py', 'w') as f:
    f.writelines(fixed_lines)

print("✅ Manually ensured UserCrisisPreferencesInDB has no id field")
