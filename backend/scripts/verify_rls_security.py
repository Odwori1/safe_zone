#!/usr/bin/env python3
"""
Verify RLS security is working for crisis tables
"""

import asyncio
import asyncpg

async def verify_rls_security():
    print("🔐 Verifying RLS Security for Crisis Tables...")
    
    connection = await asyncpg.connect(
        user="safe_zone_app_user",
        password="secure_app_password_2024",
        database="safe_zone",
        host="localhost",
        port=5433
    )
    
    test_user_1 = "8808956b-11fb-4253-91ef-98b9902ffbc8"
    test_user_2 = "11111111-1111-1111-1111-111111111111"  # Different user
    
    crisis_tables = ['user_crisis_preferences', 'emergency_contacts', 'safety_plans', 'wellness_checkins']
    
    for table in crisis_tables:
        print(f"\n📋 Testing {table}:")
        
        # Test User 1 can see their data
        await connection.execute("SELECT set_current_user_id($1);", test_user_1)
        user1_data = await connection.fetch(f"SELECT COUNT(*) as count FROM {table}")
        print(f"   User 1 sees: {user1_data[0]['count']} records")
        
        # Test User 1 cannot insert data for User 2
        try:
            if table == 'user_crisis_preferences':
                await connection.execute(f"""
                    INSERT INTO {table} (user_id, preferred_language, country_code)
                    VALUES ($1, 'en', 'US')
                """, test_user_2)
            elif table == 'emergency_contacts':
                await connection.execute(f"""
                    INSERT INTO {table} (user_id, name, phone_number)
                    VALUES ($1, 'Test', '+1234567890')
                """, test_user_2)
            print(f"   ❌ SECURITY BREACH: User 1 can insert for User 2 in {table}")
        except Exception as e:
            if "row-level security policy" in str(e):
                print(f"   ✅ SECURITY WORKING: User 1 cannot insert for User 2 in {table}")
            else:
                print(f"   ⚠️  Other error: {e}")
    
    await connection.close()
    print("\n🎉 RLS Security Verification Completed!")

if __name__ == "__main__":
    asyncio.run(verify_rls_security())
