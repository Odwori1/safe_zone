"""
Test professional directory CRUD operations
"""

import asyncio
from app.database.database import database
from app.crud.professional_directory import professional_directory_crud

async def test_crud_operations():
    """Test basic CRUD operations"""
    print("🧪 TESTING PROFESSIONAL DIRECTORY CRUD OPERATIONS")
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
        health_ok = await professional_directory_crud.health_check(user_id)
        if health_ok:
            print("✅ CRUD health check passed")
        else:
            print("❌ CRUD health check failed")
            return False

        # Test 2: Create professional profile
        profile_data = {
            "professional_title": "Licensed Therapist",
            "license_number": "TEST123",
            "license_state": "CA", 
            "years_of_experience": 5,
            "hourly_rate": 150.00,
            "bio": "Test professional profile",
            "approach": "Cognitive Behavioral Therapy",
            "specialties": ["anxiety", "depression"],
            "professional_email": "test@example.com"
        }

        profile = await professional_directory_crud.create_professional_profile(user_id, profile_data)
        if profile:
            print("✅ Professional profile creation works")
            profile_id = profile['id']
        else:
            print("❌ Professional profile creation failed")
            return False

        # Test 3: Get professional profile
        retrieved_profile = await professional_directory_crud.get_professional_profile(user_id, user_id)
        if retrieved_profile and retrieved_profile['professional_title'] == "Licensed Therapist":
            print("✅ Professional profile retrieval works")
        else:
            print("❌ Professional profile retrieval failed")
            return False

        # Test 4: Get professional directory
        directory = await professional_directory_crud.get_professional_directory(user_id)
        if isinstance(directory, list):
            print(f"✅ Professional directory retrieval works (found {len(directory)} listings)")
        else:
            print("❌ Professional directory retrieval failed")
            return False

        print("🎉 ALL CRUD TESTS PASSED!")
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
