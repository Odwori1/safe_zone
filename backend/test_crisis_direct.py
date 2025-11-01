#!/usr/bin/env python3
"""
Test crisis system directly via database
"""
import asyncio
from app.database.database import database
from uuid import uuid4, UUID

async def test_crisis_direct():
    """Test crisis system directly"""
    await database.connect()
    
    # Use the test user ID
    user_id = UUID('a1a6ae52-69bb-4bba-82e1-da79c8340517')
    
    async with database.pool.acquire() as conn:
        print("🧪 DIRECT CRISIS SYSTEM TEST")
        print("=============================")
        
        # 1. Test creating crisis preferences
        print("1. Creating crisis preferences...")
        try:
            result = await conn.fetchrow('''
                INSERT INTO user_crisis_preferences 
                (user_id, preferred_language, country_code, consent_to_contact)
                VALUES ($1, $2, $3, $4)
                RETURNING *
            ''', user_id, 'en', 'US', True)
            print("   ✅ Preferences created")
        except Exception as e:
            print(f"   ⚠️  Preferences error: {e}")
        
        # 2. Test creating emergency contact
        print("2. Creating emergency contact...")
        try:
            result = await conn.fetchrow('''
                INSERT INTO emergency_contacts 
                (user_id, name, relationship, phone_number, is_primary)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING *
            ''', user_id, 'Test Contact', 'Friend', '+1-555-0001', True)
            print("   ✅ Emergency contact created")
        except Exception as e:
            print(f"   ⚠️  Contact error: {e}")
        
        # 3. Test creating safety plan
        print("3. Creating safety plan...")
        try:
            result = await conn.fetchrow('''
                INSERT INTO safety_plans 
                (user_id, plan_name)
                VALUES ($1, $2)
                RETURNING *
            ''', user_id, 'Test Safety Plan')
            print("   ✅ Safety plan created")
        except Exception as e:
            print(f"   ⚠️  Safety plan error: {e}")
        
        # 4. Count records
        print("\n4. Counting records...")
        tables = ['user_crisis_preferences', 'emergency_contacts', 'safety_plans', 'wellness_checkins', 'crisis_alerts']
        for table in tables:
            count = await conn.fetchval(f'SELECT COUNT(*) FROM {table} WHERE user_id = $1', user_id)
            print(f"   {table}: {count} records")
        
        print("🎉 DIRECT TEST COMPLETED!")

if __name__ == "__main__":
    asyncio.run(test_crisis_direct())
