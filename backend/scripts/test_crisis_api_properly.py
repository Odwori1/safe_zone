#!/usr/bin/env python3
"""
Test crisis API endpoints with proper authentication
"""

import asyncio
import aiohttp
import json
import os

async def test_crisis_api_properly():
    print("🌐 Testing Crisis API Endpoints with Proper Auth...")
    
    # Get token from environment or use the one from get_new_token.py output
    token = os.getenv('TEST_TOKEN')
    if not token:
        print("❌ No TEST_TOKEN environment variable set")
        print("Run: export TEST_TOKEN='your_token_here'")
        return
    
    base_url = "http://localhost:8001/api/v1/crisis-support"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        
        print("1. Testing GET /resources (should work without user context):")
        try:
            async with session.get(f"{base_url}/resources", headers=headers) as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ SUCCESS: Retrieved {len(data)} crisis resources")
                    for resource in data[:2]:  # Show first 2
                        print(f"     - {resource.get('name')} ({resource.get('category')})")
                else:
                    error_text = await response.text()
                    print(f"   Response: {error_text}")
        except Exception as e:
            print(f"   ❌ FAILED: {e}")
        
        print("\n2. Testing GET /preferences (check if exists):")
        try:
            async with session.get(f"{base_url}/preferences", headers=headers) as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print("   ✅ Preferences exist, testing update...")
                    
                    # Test update
                    update_data = {
                        "preferred_language": "en",
                        "country_code": "US",
                        "emergency_contact_instructions": "Updated via API",
                        "medical_information": "Updated info",
                        "consent_to_contact": True
                    }
                    
                    async with session.put(f"{base_url}/preferences", headers=headers, json=update_data) as put_response:
                        print(f"   Update Status: {put_response.status}")
                        if put_response.status == 200:
                            print("   ✅ SUCCESS: Preferences updated via API!")
                        else:
                            error_text = await put_response.text()
                            print(f"   Update Error: {error_text}")
                
                elif response.status == 404:
                    print("   No preferences found, testing create...")
                    
                    # Test create
                    create_data = {
                        "preferred_language": "en",
                        "country_code": "US",
                        "emergency_contact_instructions": "Call emergency contacts",
                        "medical_information": "None",
                        "consent_to_contact": True
                    }
                    
                    async with session.post(f"{base_url}/preferences", headers=headers, json=create_data) as post_response:
                        print(f"   Create Status: {post_response.status}")
                        if post_response.status == 200:
                            data = await post_response.json()
                            print("   ✅ SUCCESS: Preferences created via API!")
                        else:
                            error_text = await post_response.text()
                            print(f"   Create Error: {error_text}")
                
                else:
                    error_text = await response.text()
                    print(f"   Unexpected status: {error_text}")
                    
        except Exception as e:
            print(f"   ❌ FAILED: {e}")
        
        print("\n3. Testing emergency contacts:")
        contact_data = {
            "name": "API Test Contact",
            "relationship": "Friend",
            "phone_number": "+1234567890",
            "email": "test@example.com",
            "is_primary": True,
            "can_receive_alerts": True,
            "notes": "Created via API"
        }
        
        try:
            async with session.post(f"{base_url}/emergency-contacts", headers=headers, json=contact_data) as response:
                print(f"   Create Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print("   ✅ SUCCESS: Emergency contact created via API!")
                    
                    # Test retrieval
                    async with session.get(f"{base_url}/emergency-contacts", headers=headers) as get_response:
                        if get_response.status == 200:
                            contacts = await get_response.json()
                            print(f"   ✅ Retrieved {len(contacts)} emergency contacts")
                        else:
                            print(f"   ❌ Failed to retrieve contacts: {get_response.status}")
                else:
                    error_text = await response.text()
                    print(f"   Create Error: {error_text}")
                    
        except Exception as e:
            print(f"   ❌ FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(test_crisis_api_properly())
