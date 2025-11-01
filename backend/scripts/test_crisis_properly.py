#!/usr/bin/env python3
"""
Test crisis system with proper data handling
"""

import asyncio
import asyncpg
from app.database.database import database

async def test_crisis_properly():
    print("🧪 Testing Crisis System Properly...")
    
    test_user_id = "8808956b-11fb-4253-91ef-98b9902ffbc8"
    
    from app.crud.crisis import crisis_crud
    from app.schemas.crisis import UserCrisisPreferencesCreate, EmergencyContactCreate, SafetyPlanCreate, WellnessCheckinCreate
    from datetime import date
    
    try:
        await database.connect()
        
        print("1. Checking existing crisis preferences:")
        existing_prefs = await crisis_crud.get_user_crisis_preferences(test_user_id)
        if existing_prefs:
            print("   ✅ Preferences already exist, testing update...")
            # Test update instead
            update_data = UserCrisisPreferencesCreate(
                preferred_language="en",
                country_code="US", 
                emergency_contact_instructions="Updated instructions",
                medical_information="Updated info",
                consent_to_contact=True
            )
            result = await crisis_crud.update_user_crisis_preferences(test_user_id, update_data)
            if result:
                print("   ✅ SUCCESS: Crisis preferences updated!")
            else:
                print("   ❌ FAILED: Update failed")
        else:
            print("   ❌ No existing preferences found")
        
        print("\n2. Testing emergency contact creation:")
        contact_data = EmergencyContactCreate(
            name="Test Emergency Contact",
            relationship="Friend",
            phone_number="+1234567890",
            email="emergency@example.com",
            is_primary=True,
            can_receive_alerts=True,
            notes="Test contact"
        )
        
        result = await crisis_crud.create_emergency_contact(test_user_id, contact_data)
        if result:
            print("   ✅ SUCCESS: Emergency contact created!")
            contact_id = result['id']
            
            # Test retrieval
            contacts = await crisis_crud.get_emergency_contacts(test_user_id)
            print(f"   Retrieved {len(contacts)} emergency contacts")
        else:
            print("   ❌ FAILED: Emergency contact creation failed")
        
        print("\n3. Testing safety plan creation:")
        safety_plan_data = SafetyPlanCreate(
            plan_name="My Safety Plan",
            warning_signs=["Feeling overwhelmed"],
            internal_coping_strategies=["Deep breathing"],
            external_coping_strategies=["Call friend"],
            social_contacts=["Friend: +1234567890"],
            professional_contacts=["Therapist"],
            environment_safety="Safe environment",
            reasons_for_living=["Family"]
        )
        
        result = await crisis_crud.create_safety_plan(test_user_id, safety_plan_data)
        if result:
            print("   ✅ SUCCESS: Safety plan created!")
            plans = await crisis_crud.get_safety_plans(test_user_id)
            print(f"   Retrieved {len(plans)} safety plans")
        else:
            print("   ❌ FAILED: Safety plan creation failed")
        
        print("\n4. Testing wellness checkin creation:")
        checkin_data = WellnessCheckinCreate(
            checkin_date=date.today(),
            mood_rating=7,
            anxiety_level=3,
            sleep_quality=4,
            safety_concerns=False,
            coping_strategies_used=["meditation"],
            support_needed=False
        )
        
        result = await crisis_crud.create_wellness_checkin(test_user_id, checkin_data)
        if result:
            print("   ✅ SUCCESS: Wellness checkin created!")
            checkins = await crisis_crud.get_wellness_checkins(test_user_id)
            print(f"   Retrieved {len(checkins)} wellness checkins")
        else:
            print("   ❌ FAILED: Wellness checkin creation failed")
        
        print("\n🎉 CRISIS SYSTEM TEST COMPLETED!")
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await database.close()

if __name__ == "__main__":
    asyncio.run(test_crisis_properly())
