#!/usr/bin/env python3
"""
Investigate how crisis CRUD operations handle database connections
"""

import asyncio
import asyncpg

async def investigate_crisis_crud():
    print("🔍 Investigating Crisis CRUD Operations...")
    
    connection = await asyncpg.connect(
        user="safe_zone_app_user",
        password="secure_app_password_2024",
        database="safe_zone",
        host="localhost",
        port=5433
    )
    
    # Check the crisis CRUD file to see how it uses the database
    print("📋 Checking crisis CRUD implementation...")
    try:
        with open('app/crud/crisis.py', 'r') as f:
            crisis_crud_code = f.read()
            
        # Look for database usage patterns
        if 'database.execute' in crisis_crud_code:
            print("✅ Crisis CRUD uses database.execute")
        if 'database.fetch' in crisis_crud_code:
            print("✅ Crisis CRUD uses database.fetch")
        if 'user_id=' in crisis_crud_code:
            print("✅ Crisis CRUD passes user_id parameter")
        else:
            print("❌ Crisis CRUD may not pass user_id parameter")
            
        # Check specific patterns
        import re
        create_patterns = re.findall(r'async def create.*?user_id.*?database\.', crisis_crud_code, re.DOTALL)
        print(f"Found {len(create_patterns)} create patterns with user_id")
        
    except FileNotFoundError:
        print("❌ crisis.py CRUD file not found")
    
    # Test the specific issue: WITH CHECK vs USING in RLS policies
    print("\n🧪 Testing RLS Policy Behavior:")
    test_user_id = "8808956b-11fb-4253-91ef-98b9902ffbc8"
    
    # Test 1: Check if set_current_user_id works for crisis tables
    print("1. Testing crisis table with set_current_user_id:")
    await connection.execute("SELECT set_current_user_id($1);", test_user_id)
    
    try:
        # This should fail due to WITH CHECK policy
        result = await connection.execute('''
            INSERT INTO user_crisis_preferences 
            (user_id, preferred_contact_method, allow_crisis_alerts)
            VALUES ($1, 'email', true)
        ''', test_user_id)
        print(f"   ✅ INSERT worked: {result}")
    except Exception as e:
        print(f"   ❌ INSERT failed: {e}")
        if "WITH CHECK" in str(e):
            print("   💡 CONFIRMED: WITH CHECK policy is blocking the insert")
    
    # Test 2: Check if working tables have the same issue
    print("2. Testing working table (journals) with set_current_user_id:")
    await connection.execute("SELECT set_current_user_id($1);", test_user_id)
    
    try:
        result = await connection.execute('''
            INSERT INTO journals 
            (user_id, title, content, mood, visibility)
            VALUES ($1, 'Test Journal', 'Test content', 'neutral', 'private')
        ''', test_user_id)
        print(f"   ✅ Journals INSERT worked: {result}")
    except Exception as e:
        print(f"   ❌ Journals INSERT failed: {e}")
    
    await connection.close()

if __name__ == "__main__":
    asyncio.run(investigate_crisis_crud())
