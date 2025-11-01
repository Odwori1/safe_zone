#!/usr/bin/env python3
"""
Test the crisis fix by manually setting user context
"""

import asyncio
import asyncpg

async def test_crisis_fix():
    print("🧪 Testing Crisis Fix...")
    
    connection = await asyncpg.connect(
        user="safe_zone_app_user",
        password="secure_app_password_2024",
        database="safe_zone",
        host="localhost",
        port=5433
    )
    
    test_user_id = "8808956b-11fb-4253-91ef-98b9902ffbc8"
    
    # Test 1: Without setting context (should fail)
    print("1. Testing WITHOUT user context:")
    try:
        result = await connection.execute('''
            INSERT INTO user_crisis_preferences 
            (user_id, preferred_language, country_code, emergency_contact_instructions,
             medical_information, consent_to_contact)
            VALUES ($1, 'en', 'US', 'Call emergency contacts', 'None', true)
        ''', test_user_id)
        print(f"   ✅ INSERT worked: {result}")
    except Exception as e:
        print(f"   ❌ INSERT failed: {e}")
    
    # Test 2: With set_current_user_id (should work)
    print("2. Testing WITH set_current_user_id:")
    await connection.execute("SELECT set_current_user_id($1);", test_user_id)
    try:
        result = await connection.execute('''
            INSERT INTO user_crisis_preferences 
            (user_id, preferred_language, country_code, emergency_contact_instructions,
             medical_information, consent_to_contact)
            VALUES ($1, 'en', 'US', 'Call emergency contacts', 'None', true)
        ''', test_user_id)
        print(f"   ✅ INSERT worked: {result}")
        
        # Clean up
        await connection.execute("DELETE FROM user_crisis_preferences WHERE user_id = $1", test_user_id)
    except Exception as e:
        print(f"   ❌ INSERT failed: {e}")
    
    # Test 3: Using database class method (should work)
    print("3. Testing WITH database.execute method:")
    from app.database.database import database
    try:
        await database.connect()
        result = await database.execute('''
            INSERT INTO user_crisis_preferences 
            (user_id, preferred_language, country_code, emergency_contact_instructions,
             medical_information, consent_to_contact)
            VALUES ($1, 'en', 'US', 'Call emergency contacts', 'None', true)
        ''', test_user_id, user_id=test_user_id)
        print(f"   ✅ INSERT worked: {result}")
        
        # Clean up
        await database.execute("DELETE FROM user_crisis_preferences WHERE user_id = $1", test_user_id, user_id=test_user_id)
    except Exception as e:
        print(f"   ❌ INSERT failed: {e}")
    finally:
        await database.close()
    
    await connection.close()

if __name__ == "__main__":
    asyncio.run(test_crisis_fix())
