#!/usr/bin/env python3
"""
Check how crisis endpoints handle database connections
"""

import asyncio
import asyncpg

async def check_crisis_endpoints():
    print("🔍 Checking Crisis Endpoints Implementation...")
    
    connection = await asyncpy.connect(
        user="safe_zone_app_user",
        password="secure_app_password_2024",
        database="safe_zone",
        host="localhost",
        port=5433
    )
    
    # Let's see what happens when we try to use crisis tables
    # with the current database pattern
    test_user_id = "8808956b-11fb-4253-91ef-98b9902ffbc8"
    
    print("🧪 Testing crisis table access patterns:")
    
    # Test 1: Using set_current_user_id (working approach)
    print("1. Using set_current_user_id approach:")
    await connection.execute("SELECT set_current_user_id($1);", test_user_id)
    
    try:
        result = await connection.execute('''
            INSERT INTO user_crisis_preferences 
            (user_id, preferred_contact_method, allow_crisis_alerts)
            VALUES ($1, 'email', true)
        ''', test_user_id)
        print(f"   ✅ INSERT with set_current_user_id: {result}")
    except Exception as e:
        print(f"   ❌ INSERT with set_current_user_id failed: {e}")
    
    # Test 2: Using direct SET (crisis table expectation)
    print("2. Using direct SET approach:")
    await connection.execute(f"SET app.current_user_id TO '{test_user_id}'")
    
    try:
        result = await connection.execute('''
            INSERT INTO user_crisis_preferences 
            (user_id, preferred_contact_method, allow_crisis_alerts)
            VALUES ($1, 'email', true)
        ''', test_user_id)
        print(f"   ✅ INSERT with direct SET: {result}")
    except Exception as e:
        print(f"   ❌ INSERT with direct SET failed: {e}")
    
    # Check the actual crisis endpoint implementation
    print("\n📋 Checking crisis endpoint code pattern:")
    
    # Let's see if crisis endpoints use the database class differently
    try:
        with open('app/api/endpoints/crisis.py', 'r') as f:
            crisis_code = f.read()
            # Look for database usage patterns
            if 'database.execute' in crisis_code:
                print("   ✅ Crisis endpoints use database.execute")
            if 'database.fetch' in crisis_code:
                print("   ✅ Crisis endpoints use database.fetch")
            if 'user_id=' in crisis_code:
                print("   ✅ Crisis endpoints pass user_id parameter")
            else:
                print("   ❌ Crisis endpoints may not pass user_id parameter")
    except FileNotFoundError:
        print("   ❌ crisis.py endpoint file not found")
    
    await connection.close()

if __name__ == "__main__":
    asyncio.run(check_crisis_endpoints())
