"""
Test AI personalization CRUD operations
"""

import asyncio
from datetime import time
from app.database.database import database
from app.crud.ai_personalization import ai_personalization_crud

async def test_crud_operations():
    """Test basic CRUD operations"""
    print("🧪 TESTING AI PERSONALIZATION CRUD OPERATIONS")
    print("=" * 50)

    await database.connect()

    try:
        # Get a test user
        async with database.pool.acquire() as conn:
            user = await conn.fetchrow("SELECT id FROM users LIMIT 1")
            if not user:
                print("❌ No users found for testing")
                return False
            user_id = user['id']
            print(f"✅ Testing with user: {user_id}")

        # Test 1: Health check
        health_ok = await ai_personalization_crud.health_check(user_id)
        if health_ok:
            print("✅ CRUD health check passed")
        else:
            print("❌ CRUD health check failed")
            return False

        # Test 2: Get coping strategies
        strategies = await ai_personalization_crud.get_coping_strategies()
        if strategies and len(strategies) > 0:
            print(f"✅ Coping strategies retrieval works: {len(strategies)} strategies found")
        else:
            print("❌ Coping strategies retrieval failed")
            return False

        # Test 3: Get notification preferences
        preferences = await ai_personalization_crud.get_notification_preferences(user_id, user_id)
        if preferences is not None:  # Can be None if no preferences set yet
            print("✅ Notification preferences retrieval works")
        else:
            print("✅ Notification preferences not set (expected for new user)")

        # Test 4: Update notification preferences with proper time objects
        pref_data = {
            "optimal_morning_time": time(8, 30),  # Use time object, not string
            "optimal_evening_time": time(19, 30), 
            "receive_wellness_tips": True,
            "max_daily_notifications": 3
        }
        updated_prefs = await ai_personalization_crud.update_notification_preferences(user_id, pref_data)
        if updated_prefs and updated_prefs['optimal_morning_time'].strftime('%H:%M') == '08:30':
            print("✅ Notification preferences update works")
        else:
            print("❌ Notification preferences update failed")
            return False

        print("🎉 ALL AI PERSONALIZATION CRUD TESTS PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ CRUD test failed: {e}")
        return False
    finally:
        if database.pool:
            await database.pool.close()

if __name__ == "__main__":
    success = asyncio.run(test_crud_operations())
    exit(0 if success else 1)
