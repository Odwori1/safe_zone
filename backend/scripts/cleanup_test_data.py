#!/usr/bin/env python3
"""
Clean up any existing test crisis data
"""

import asyncio
import asyncpg

async def cleanup_test_data():
    print("🧹 Cleaning up test crisis data...")
    
    connection = await asyncpg.connect(
        user="safe_zone_app_user",
        password="secure_app_password_2024",
        database="safe_zone",
        host="localhost",
        port=5433
    )
    
    test_user_id = "8808956b-11fb-4253-91ef-98b9902ffbc8"
    
    # Set user context first
    await connection.execute("SELECT set_current_user_id($1);", test_user_id)
    
    # Delete any existing test data
    tables = ['user_crisis_preferences', 'emergency_contacts', 'safety_plans', 'wellness_checkins', 'crisis_alerts']
    
    for table in tables:
        try:
            result = await connection.execute(f"DELETE FROM {table} WHERE user_id = $1", test_user_id)
            if "DELETE" in result:
                print(f"✅ Cleaned up {table}: {result}")
        except Exception as e:
            print(f"⚠️ Could not clean up {table}: {e}")
    
    await connection.close()
    print("🎉 Cleanup completed!")

if __name__ == "__main__":
    asyncio.run(cleanup_test_data())
