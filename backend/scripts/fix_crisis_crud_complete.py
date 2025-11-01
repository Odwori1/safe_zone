#!/usr/bin/env python3
"""
Add all missing methods to crisis CRUD
"""

import re

# Read the current crisis CRUD
with open('app/crud/crisis.py', 'r') as f:
    content = f.read()

# Add count_resources method if missing
if 'async def count_resources' not in content:
    print("Adding count_resources method...")
    # Find the end of the class methods to add it there
    # Look for the last method before the instance creation
    pattern = r'(\s+async def \w+.*?return.*?\n)(\n# Create instance)'
    
    replacement = r'''\1
    async def count_resources(self, category: Optional[str] = None,
                            geographic_scope: Optional[str] = None) -> int:
        """Count crisis resources with optional filtering"""
        async with database.pool.acquire() as conn:
            query = "SELECT COUNT(*) FROM crisis_resources WHERE is_active = true"
            params = []
            param_count = 0

            if category:
                param_count += 1
                query += f" AND category = ${param_count}"
                params.append(category)

            if geographic_scope:
                param_count += 1
                query += f" AND (geographic_scope = 'global' OR geographic_scope = ${param_count})"
                params.append(geographic_scope)

            return await conn.fetchval(query, *params)

\2'''
    
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    print("✅ Added count_resources method")

# Add count_user_contacts method if missing  
if 'async def count_user_contacts' not in content:
    print("Adding count_user_contacts method...")
    # Insert after count_resources
    pattern = r'(async def count_resources.*?return await conn\.fetchval\(query, \*params\)\s*\n)(\n\s+# =|\n\s+async def|\n# Create instance)'
    
    replacement = r'''\1

    async def count_user_contacts(self, user_id: UUID) -> int:
        """Count user's emergency contacts"""
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            return await conn.fetchval(
                "SELECT COUNT(*) FROM emergency_contacts WHERE user_id = $1",
                user_id
            )

\2'''
    
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    print("✅ Added count_user_contacts method")

# Write the updated content
with open('app/crud/crisis.py', 'w') as f:
    f.write(content)

print("✅ Updated crisis CRUD with all missing methods")
