#!/usr/bin/env python3
"""
Check how working endpoints handle database connections
"""

import asyncio
import asyncpg

async def check_working_endpoints():
    print("🔍 Checking Working Endpoints Database Pattern...")
    
    # Let's examine the posts endpoint to see how it handles RLS
    print("📋 Checking posts endpoint pattern:")
    
    connection = await asyncpg.connect(
        user="safe_zone_app_user",
        password="secure_app_password_2024",
        database="safe_zone",
        host="localhost",
        port=5433
    )
    
    # Check if posts table uses the same RLS pattern
    posts_policies = await connection.fetch('''
        SELECT policyname, cmd, qual
        FROM pg_policies 
        WHERE tablename = 'posts'
    ''')
    
    print("Posts table RLS policies:")
    for policy in posts_policies:
        print(f"  - {policy['policyname']}: {policy['qual']}")
    
    # Check the actual database.py to see how it's used
    print("\n🔧 Checking database.py usage pattern:")
    
    # Let's test what happens when we use the database class methods
    test_user_id = "8808956b-11fb-4253-91ef-98b9902ffbc8"
    
    print("Testing database.execute with user_id:")
    from app.database.database import database
    
    try:
        await database.connect()
        
        # Test the working pattern
        result = await database.execute(
            "SELECT id FROM posts LIMIT 1", 
            user_id=test_user_id
        )
        print(f"✅ Database.execute with user_id worked: {result}")
        
    except Exception as e:
        print(f"❌ Database.execute failed: {e}")
    finally:
        await database.close()
    
    await connection.close()

if __name__ == "__main__":
    asyncio.run(check_working_endpoints())
