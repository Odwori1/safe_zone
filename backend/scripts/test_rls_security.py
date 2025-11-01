#!/usr/bin/env python3
"""
Test that RLS security is properly enforcing user isolation
"""

import asyncio
import asyncpg

async def test_rls_security():
    print("🔐 Testing RLS Security Enforcement...")
    
    connection = await asyncpg.connect(
        user="safe_zone_app_user",
        password="secure_app_password_2024",
        database="safe_zone",
        host="localhost",
        port=5433
    )
    
    test_user_1 = "8808956b-11fb-4253-91ef-98b9902ffbc8"
    test_user_2 = "00000000-0000-0000-0000-000000000000"  # Different user
    
    print("1. Testing User 1 can access their own data:")
    await connection.execute("SELECT set_current_user_id($1);", test_user_1)
    
    try:
        result = await connection.fetch("SELECT * FROM user_crisis_preferences WHERE user_id = $1", test_user_1)
        print(f"   ✅ User 1 can see their data: {len(result)} records")
    except Exception as e:
        print(f"   ❌ User 1 cannot see their data: {e}")
    
    print("\n2. Testing User 1 CANNOT access User 2's data:")
    try:
        result = await connection.fetch("SELECT * FROM user_crisis_preferences WHERE user_id = $1", test_user_2)
        print(f"   ❌ SECURITY BREACH: User 1 can see User 2's data: {len(result)} records")
    except Exception as e:
        print(f"   ✅ SECURITY WORKING: User 1 cannot see User 2's data - {e}")
    
    print("\n3. Testing User 2 context:")
    await connection.execute("SELECT set_current_user_id($1);", test_user_2)
    
    try:
        result = await connection.fetch("SELECT * FROM user_crisis_preferences WHERE user_id = $1", test_user_1)
        print(f"   ❌ SECURITY BREACH: User 2 can see User 1's data: {len(result)} records")
    except Exception as e:
        print(f"   ✅ SECURITY WORKING: User 2 cannot see User 1's data - {e}")
    
    await connection.close()
    print("\n🎉 RLS SECURITY TEST COMPLETED!")

if __name__ == "__main__":
    asyncio.run(test_rls_security())
