#!/usr/bin/env python3
"""
Create the fixed crisis CRUD file with proper RLS context setting
"""

import os

# Read the original crisis CRUD
with open('app/crud/crisis.py', 'r') as f:
    original_content = f.read()

# Replace all direct connection patterns with proper context setting
fixed_content = original_content

# Replace all instances of:
# async with database.pool.acquire() as conn:
# With:
# async with database.pool.acquire() as conn:
#     await conn.execute("SELECT set_current_user_id($1);", str(user_id))

# This is a complex replacement, so let's do it method by method
# First, let's create a backup
backup_file = 'app/crud/crisis.py.backup'
with open(backup_file, 'w') as f:
    f.write(original_content)
print(f"✅ Backup created: {backup_file}")

# Now create the fixed version
fixed_lines = []
lines = original_content.split('\n')
i = 0

while i < len(lines):
    line = lines[i]
    fixed_lines.append(line)
    
    # Look for async with database.pool.acquire() pattern
    if 'async with database.pool.acquire() as conn:' in line:
        # Check if this is in a method that has user_id parameter
        # Look backward to find the method definition
        j = i - 1
        method_has_user_id = False
        while j >= 0 and j > i - 10:  # Look back 10 lines max
            if 'async def' in lines[j] and 'user_id' in lines[j]:
                method_has_user_id = True
                break
            j -= 1
        
        if method_has_user_id:
            # Add the set_current_user_id call after the connection acquire
            fixed_lines.append(' ' * 12 + 'await conn.execute("SELECT set_current_user_id($1);", str(user_id))')
    
    i += 1

fixed_content = '\n'.join(fixed_lines)

# Write the fixed content
fixed_file = 'app/crud/crisis_fixed.py'
with open(fixed_file, 'w') as f:
    f.write(fixed_content)

print(f"✅ Fixed version created: {fixed_file}")
print("📋 Review the fixed file and then replace the original:")
print("cp app/crud/crisis_fixed.py app/crud/crisis.py")
