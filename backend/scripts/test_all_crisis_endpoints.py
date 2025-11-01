#!/usr/bin/env python3
"""
Test all crisis endpoints comprehensively
"""

import asyncio
import aiohttp
import json
import os
from datetime import date

async def test_all_crisis_endpoints():
    print("🌐 Comprehensive Crisis API Test...")
    
    token = os.getenv('TEST_TOKEN')
    if not token:
        print("❌ No TEST_TOKEN set. Run: export TEST_TOKEN='your_token'")
        return
    
    base_url = "http://localhost:8001/api/v1/crisis-support"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        
        print("1. Testing crisis resources endpoints:")
        try:
            # Get all resources
            async with session.get(f"{base_url}/resources", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ GET /resources: {len(data)} resources")
                else:
                    error = await response.text()
                    print(f"   ❌ GET /resources failed: {response.status} - {error}")
        except Exception as e:
            print(f"   ❌ GET /resources error: {e}")
        
        print("\n2. Testing crisis preferences endpoints:")
        try:
            # Check if preferences exist
            async with session.get(f"{base_url}/preferences", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    print("   ✅ GET /preferences: Preferences exist")
                    
                    # Update preferences
                    update_data = {
                        "preferred_language": "en",
                        "country_code": "US", 
                        "emergency_contact_instructions": "Call emergency contacts first",
                        "medical_information": "No known conditions",
                        "consent_to_contact": True
                    }
                    async with session.put(f"{base_url}/preferences", headers=headers, json=update_data) as put_resp:
                        if put_resp.status == 200:
                            print("   ✅ PUT /preferences: Updated successfully")
                        else:
                            error = await put_resp.text()
                            print(f"   ❌ PUT /preferences failed: {put_resp.status} - {error}")
                
                elif response.status == 404:
                    print("   ℹ️  GET /preferences: No preferences found")
                    # Create preferences
                    create_data = {
                        "preferred_language": "en",
                        "country_code": "US",
                        "emergency_contact_instructions": "Call emergency contacts",
                        "medical_information": "None",
                        "consent_to_contact": True
                    }
                    async with session.post(f"{base_url}/preferences", headers=headers, json=create_data) as post_resp:
                        if post_resp.status == 200:
                            print("   ✅ POST /preferences: Created successfully")
                        else:
                            error = await post_resp.text()
                            print(f"   ❌ POST /preferences failed: {post_resp.status} - {error}")
                else:
                    error = await response.text()
                    print(f"   ❌ GET /preferences failed: {response.status} - {error}")
                    
        except Exception as e:
            print(f"   ❌ Preferences error: {e}")
        
        print("\n3. Testing emergency contacts endpoints:")
        try:
            # Create a contact
            contact_data = {
                "name": "Test Contact",
                "relationship": "Friend", 
                "phone_number": "+1234567890",
                "email": "friend@example.com",
                "is_primary": False,
                "can_receive_alerts": True,
                "notes": "Test contact"
            }
            async with session.post(f"{base_url}/emergency-contacts", headers=headers, json=contact_data) as response:
                if response.status == 200:
                    data = await response.json()
                    contact_id = data.get('id')
                    print(f"   ✅ POST /emergency-contacts: Created contact {contact_id}")
                    
                    # Get all contacts
                    async with session.get(f"{base_url}/emergency-contacts", headers=headers) as get_resp:
                        if get_resp.status == 200:
                            contacts = await get_resp.json()
                            print(f"   ✅ GET /emergency-contacts: {len(contacts)} contacts")
                        else:
                            error = await get_resp.text()
                            print(f"   ❌ GET /emergency-contacts failed: {get_resp.status} - {error}")
                else:
                    error = await response.text()
                    print(f"   ❌ POST /emergency-contacts failed: {response.status} - {error}")
                    
        except Exception as e:
            print(f"   ❌ Emergency contacts error: {e}")
        
        print("\n4. Testing safety plans endpoints:")
        try:
            safety_plan_data = {
                "plan_name": "My Safety Plan",
                "warning_signs": ["Feeling overwhelmed", "Isolating myself"],
                "internal_coping_strategies": ["Deep breathing", "Mindfulness"],
                "external_coping_strategies": ["Go for a walk", "Call a friend"],
                "social_contacts": ["Friend: +1234567890"],
                "professional_contacts": ["Therapist: Dr. Smith"],
                "environment_safety": "Remove sharp objects",
                "reasons_for_living": ["Family", "Future goals"]
            }
            async with session.post(f"{base_url}/safety-plans", headers=headers, json=safety_plan_data) as response:
                if response.status == 201:
                    data = await response.json()
                    plan_id = data.get('id')
                    print(f"   ✅ POST /safety-plans: Created plan {plan_id}")
                    
                    # Get all plans
                    async with session.get(f"{base_url}/safety-plans", headers=headers) as get_resp:
                        if get_resp.status == 200:
                            plans = await get_resp.json()
                            print(f"   ✅ GET /safety-plans: {len(plans)} plans")
                        else:
                            error = await get_resp.text()
                            print(f"   ❌ GET /safety-plans failed: {get_resp.status} - {error}")
                else:
                    error = await response.text()
                    print(f"   ❌ POST /safety-plans failed: {response.status} - {error}")
                    
        except Exception as e:
            print(f"   ❌ Safety plans error: {e}")
        
        print("\n5. Testing wellness checkins endpoints:")
        try:
            checkin_data = {
                "checkin_date": str(date.today()),
                "mood_rating": 7,
                "anxiety_level": 3,
                "sleep_quality": 4,
                "safety_concerns": False,
                "coping_strategies_used": ["exercise", "meditation"],
                "support_needed": False
            }
            async with session.post(f"{base_url}/wellness-checkins", headers=headers, json=checkin_data) as response:
                if response.status == 201:
                    data = await response.json()
                    checkin_id = data.get('id')
                    print(f"   ✅ POST /wellness-checkins: Created checkin {checkin_id}")
                    
                    # Get all checkins
                    async with session.get(f"{base_url}/wellness-checkins", headers=headers) as get_resp:
                        if get_resp.status == 200:
                            checkins = await get_resp.json()
                            print(f"   ✅ GET /wellness-checkins: {len(checkins)} checkins")
                        else:
                            error = await get_resp.text()
                            print(f"   ❌ GET /wellness-checkins failed: {get_resp.status} - {error}")
                else:
                    error = await response.text()
                    print(f"   ❌ POST /wellness-checkins failed: {response.status} - {error}")
                    
        except Exception as e:
            print(f"   ❌ Wellness checkins error: {e}")
        
        print("\n🎉 Comprehensive test completed!")

if __name__ == "__main__":
    asyncio.run(test_all_crisis_endpoints())
