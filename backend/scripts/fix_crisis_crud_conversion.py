import asyncpg
import json

# Test the current data to see what's causing the issue
async def test_crisis_data():
    try:
        conn = await asyncpg.connect(
            host='127.0.0.1',
            port=5433,
            database='safe_zone',
            user='safe_zone_app_user',
            password='secure_app_password_2024'
        )
        
        print("🔍 Testing crisis resources data structure...")
        
        # Get a few resources to see their structure
        resources = await conn.fetch("SELECT * FROM crisis_resources LIMIT 3")
        
        for i, resource in enumerate(resources):
            print(f"\nResource {i+1}:")
            for key, value in dict(resource).items():
                print(f"  {key}: {value} (type: {type(value)})")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

import asyncio
asyncio.run(test_crisis_data())
