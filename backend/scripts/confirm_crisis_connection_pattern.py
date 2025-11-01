#!/usr/bin/env python3
"""
Confirm that crisis CRUD doesn't use the proper database pattern
"""

import asyncio
import asyncpg

async def confirm_crisis_connection_pattern():
    print("🔍 Confirming Crisis CRUD Connection Pattern...")
    
    # Check crisis CRUD file for connection patterns
    with open('app/crud/crisis.py', 'r') as f:
        content = f.read()
    
    # Count usage patterns
    direct_conn_count = content.count('async with database.pool.acquire() as conn:')
    database_method_count = content.count('database.execute(') + content.count('database.fetch') + content.count('database.fetchrow') + content.count('database.fetchval')
    
    print(f"📊 Connection Pattern Usage in Crisis CRUD:")
    print(f"   Direct conn.execute(): {direct_conn_count} occurrences")
    print(f"   Database class methods: {database_method_count} occurrences")
    
    # Check if crisis CRUD passes user_id to database methods
    if 'user_id=' in content:
        print("✅ Crisis CRUD passes user_id parameter")
    else:
        print("❌ Crisis CRUD does NOT pass user_id parameter")
    
    # Check specific methods
    print("\n🔍 Specific method patterns:")
    import re
    
    # Find all async def methods
    methods = re.findall(r'async def (\w+).*?async with database\.pool\.acquire', content, re.DOTALL)
    print(f"Methods using direct connection: {methods}")
    
    # Check if any use database class methods
    database_methods = re.findall(r'async def (\w+).*?database\.(execute|fetch|fetchrow|fetchval)', content, re.DOTALL)
    print(f"Methods using database class: {database_methods}")

if __name__ == "__main__":
    asyncio.run(confirm_crisis_connection_pattern())
