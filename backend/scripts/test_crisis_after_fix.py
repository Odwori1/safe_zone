#!/usr/bin/env python3
"""
Test crisis endpoints after the RLS fix
"""

import asyncio
import asyncpg
from app.database.database import database

async def test_crisis_after_fix():
    print("🧪 Testing Crisis Endpoints After Fix...")
    
    test_user_id = "8808956b-11fb-4253-91ef-98b9902ffbc8"
    
    # Test using the actual crisis CRUD
    from app.crud.crisis import crisis_crud
    
    try:
        await database.connect()
        
        print("1. Testing create_user_crisis_preferences:")
        from app.schemas.crisis import UserCrisisPreferencesCreate
        
        preferences_data = UserCrisisPreferencesCreate(
            preferred_language="en",
            country_code="US", 
            emergency_contact_instructions="Call emergency contacts",
            medical_information="None",
            consent_to_contact=True
        )
        
        result = await crisis_crud.create_user_crisis_preferences(test_user_id, preferences_data)
        if result:
            print("   ✅ SUCCESS: Crisis preferences created!")
            print(f"   Result: {dict(result)}")
        else:
            print("   ❌ FAILED: No result returned")
            
        # Clean up
        await database.execute("DELETE FROM user_crisis_preferences WHERE user_id = $1", test_user_id, user_id=test_user_id)
        
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await database.close()

if __name__ == "__main__":
    asyncio.run(test_crisis_after_fix())
