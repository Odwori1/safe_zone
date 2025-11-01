#!/usr/bin/env python3
"""
Check what crisis data already exists
"""

import asyncio
import asyncpg

async def check_existing_crisis_data():
    print("🔍 Checking existing crisis data...")
    
    connection = await asyncpg.connect(
        user="safe_zone_app_user",
        password="secure_app_password_2024",
        database="safe_zone",
        host="localhost",
        port=5433
    )
    
    test_user_id = "8808956b-11fb-4253-91ef-98b9902ffbc8"
    
    # Check user_crisis_preferences
    print("📋 user_crisis_preferences:")
    await connection.execute("SELECT set_current_user_id($1);", test_user_id)
    prefs = await connection.fetch("SELECT * FROM user_crisis_preferences")
    for pref in prefs:
        print(f"   User: {pref['user_id']}, Language: {pref.get('preferred_language')}")
    
    # Check all crisis tables
    crisis_tables = ['emergency_contacts', 'safety_plans', 'wellness_checkins', 'crisis_alerts']
    
    for table in crisis_tables:
        print(f"\n📋 {table}:")
        try:
            data = await connection.fetch(f"SELECT * FROM {table} LIMIT 5")
            print(f"   Found {len(data)} records")
            for record in data:
                print(f"     - User: {record.get('user_id')}, ID: {record.get('id')}")
        except Exception as e:
            print(f"   Error: {e}")
    
    await connection.close()

if __name__ == "__main__":
    asyncio.run(check_existing_crisis_data())
