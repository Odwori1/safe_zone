#!/usr/bin/env python3
"""
Manually fix the crisis schemas
"""

# Read the schemas
with open('app/schemas/crisis.py', 'r') as f:
    lines = f.readlines()

# Find and fix UserCrisisPreferencesResponse
fixed_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    fixed_lines.append(line)
    
    # Look for UserCrisisPreferencesResponse class
    if 'class UserCrisisPreferencesResponse' in line:
        # The next line should be the first field - add id field before it
        j = i + 1
        while j < len(lines) and lines[j].strip() == "":
            j += 1
        
        if j < len(lines) and 'user_id: UUID' in lines[j]:
            fixed_lines.append('    id: UUID\n')
    
    i += 1

# Write the fixed content
with open('app/schemas/crisis.py', 'w') as f:
    f.writelines(fixed_lines)

print("✅ Fixed UserCrisisPreferencesResponse schema")
