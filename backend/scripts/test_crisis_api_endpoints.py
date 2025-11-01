#!/usr/bin/env python3
"""
Test the actual crisis API endpoints
"""

import asyncio
import aiohttp
import json

async def test_crisis_api_endpoints():
    print("🌐 Testing Crisis API Endpoints...")
    
    # Use the token from earlier
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4ODA4OTU2Yi0xMWZiLTQyNTMtOTFlZi05OGI5OTAyZmZiYzgiLCJlbWFpbCI6ImRldmVsb3Blcl90ZXN0QGV4YW1wbGUuY29tIiwiZXhwIjoxNzYxOTg0OTA0fQ.hlc9qhUbh8qPWpyQPF88B7N0G41IdMhJBj1fkLRN2es"
    
    base_url = "http://localhost:8001/api/v1/crisis-support"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        
        print("1. Testing GET /resources (public endpoint):")
        try:
            async with session.get(f"{base_url}/resources", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ SUCCESS: Retrieved {len(data)} crisis resources")
                else:
                    print(f"   ❌ FAILED: Status {response.status}")
        except Exception as e:
            print(f"   ❌ FAILED: {e}")
        
        print("\n2. Testing POST /preferences:")
        preferences_data = {
            "preferred_language": "en",
            "country_code": "US",
            "emergency_contact_instructions": "Call emergency contacts first",
            "medical_information": "No known conditions",
            "consent_to_contact": True
        }
        
        try:
            async with session.post(f"{base_url}/preferences", headers=headers, json=preferences_data) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ SUCCESS: Created crisis preferences")
                    print(f"   User ID: {data.get('user_id')}")
                else:
                    print(f"   ❌ FAILED: Status {response.status}")
                    error_text = await response.text()
                    print(f"   Error: {error_text}")
        except Exception as e:
            print(f"   ❌ FAILED: {e}")
        
        print("\n3. Testing GET /preferences:")
        try:
            async with session.get(f"{base_url}/preferences", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ SUCCESS: Retrieved crisis preferences")
                else:
                    print(f"   ❌ FAILED: Status {response.status}")
        except Exception as e:
            print(f"   ❌ FAILED: {e}")
        
        print("\n4. Testing POST /emergency-contacts:")
        contact_data = {
            "name": "API Test Contact",
            "relationship": "Family",
            "phone_number": "+1987654321",
            "email": "family@example.com",
            "is_primary": True,
            "can_receive_alerts": True,
            "notes": "Created via API test"
        }
        
        try:
            async with session.post(f"{base_url}/emergency-contacts", headers=headers, json=contact_data) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ SUCCESS: Created emergency contact")
                    print(f"   Contact ID: {data.get('id')}")
                else:
                    print(f"   ❌ FAILED: Status {response.status}")
                    error_text = await response.text()
                    print(f"   Error: {error_text}")
        except Exception as e:
            print(f"   ❌ FAILED: {e}")
        
        print("\n5. Testing GET /emergency-contacts:")
        try:
            async with session.get(f"{base_url}/emergency-contacts", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ SUCCESS: Retrieved {len(data)} emergency contacts")
                else:
                    print(f"   ❌ FAILED: Status {response.status}")
        except Exception as e:
            print(f"   ❌ FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(test_crisis_api_endpoints())
