#!/usr/bin/env python3
"""
Add missing methods to crisis CRUD
"""

# Read the current crisis CRUD
with open('app/crud/crisis.py', 'r') as f:
    content = f.read()

# Check if count_resources method exists
if 'async def count_resources' not in content:
    print("❌ count_resources method is missing from crisis CRUD")
    
    # Find where to insert the method (after get_recommended_resources)
    if 'async def get_recommended_resources' in content:
        # Insert count_resources after get_recommended_resources
        import re
        pattern = r'(async def get_recommended_resources.*?)(?=async def|\Z)'
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

'''
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        print("✅ Added count_resources method")
    else:
        print("❌ Could not find get_recommended_resources method to insert after")

# Write the updated content
with open('app/crud/crisis.py', 'w') as f:
    f.write(content)

print("✅ Updated crisis CRUD with missing methods")
