#!/usr/bin/env python3
"""
Debug the preferences schema issue
"""

import asyncio
import asyncpg
from app.database.database import database

async def debug_preferences():
    print("🔍 Debugging Preferences Schema Issue...")
    
    test_user_id = "8808956b-11fb-4253-91ef-98b9902ffbc8"
    
    # First, let's see what the database actually returns
    connection = await asyncpg.connect(
        user="safe_zone_app_user",
        password="secure_app_password_2024",
        database="safe_zone",
        host="localhost",
        port=5433
    )
    
    await connection.execute("SELECT set_current_user_id($1);", test_user_id)
    
    print("1. Database structure of user_crisis_preferences:")
    columns = await connection.fetch('''
        SELECT column_name, data_type, is_nullable 
        FROM information_schema.columns 
        WHERE table_name = 'user_crisis_preferences'
        ORDER BY ordinal_position
    ''')
    
    for col in columns:
        print(f"   - {col['column_name']}: {col['data_type']} {'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'}")
    
    print("\n2. Actual data in user_crisis_preferences:")
    data = await connection.fetch("SELECT * FROM user_crisis_preferences WHERE user_id = $1", test_user_id)
    for row in data:
        print("   Row data:")
        for key, value in row.items():
            print(f"     {key}: {value} ({type(value)})")
    
    await connection.close()
    
    print("\n3. Testing crisis CRUD method directly:")
    from app.crud.crisis import crisis_crud
    try:
        await database.connect()
        result = await crisis_crud.get_user_crisis_preferences(test_user_id)
        print(f"   CRUD result type: {type(result)}")
        if result:
            print(f"   CRUD result keys: {list(result.keys())}")
            print(f"   CRUD result data: {dict(result)}")
    except Exception as e:
        print(f"   CRUD error: {e}")
    finally:
        await database.close()

if __name__ == "__main__":
    asyncio.run(debug_preferences())
