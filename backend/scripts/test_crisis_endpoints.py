#!/usr/bin/env python3
"""
Test all crisis support system endpoints
"""
import asyncio
import aiohttp
import json

async def test_crisis_endpoints():
    """Test all crisis endpoints with the JWT token"""
    
    # Use your actual JWT token
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4ODA4OTU2Yi0xMWZiLTQyNTMtOTFlZi05OGI5OTAyZmZiYzgiLCJlbWFpbCI6ImRldmVsb3Blcl90ZXN0QGV4YW1wbGUuY29tIiwiZXhwIjoxNzYxOTQzMTQ2fQ.Qkp3BnRZ-A9ytjVbmUxmHbwa4v0N-h6JNUy7k9Kp6sQ"
    headers = {"Authorization": f"Bearer {token}"}
    base_url = "http://localhost:8001/api/v1"
    
    async with aiohttp.ClientSession(headers=headers) as session:
        print("🚀 Testing Crisis Support System Endpoints...")
        
        endpoints = [
            "/crisis-support/resources/",
            "/crisis-support/emergency-contacts/", 
            "/crisis-support/safety-plans/",
            "/crisis-support/wellness-checkins/",
            "/crisis-support/preferences/",
            # Try different variations for crisis-alerts
            "/crisis-support/crisis-alerts/",
            "/crisis-support/crisis-alerts",
            "/crisis-alerts/",
            "/crisis-alerts"
        ]
        
        for endpoint in endpoints:
            try:
                print(f"\n🔍 Testing {endpoint}...")
                async with session.get(f"{base_url}{endpoint}") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        print(f"✅ SUCCESS: {endpoint}")
                        if 'total' in data:
                            print(f"   📊 Total items: {data['total']}")
                        elif isinstance(data, list):
                            print(f"   📊 Items: {len(data)}")
                        else:
                            print(f"   📊 Response keys: {list(data.keys())}")
                    else:
                        print(f"❌ {endpoint}: Status {resp.status}")
                        if resp.status == 404:
                            print(f"   Endpoint not found")
                        else:
                            error_text = await resp.text()
                            print(f"   Error: {error_text}")
            except Exception as e:
                print(f"❌ {endpoint}: Exception - {e}")
        
        print("\n🎉 Crisis endpoints testing completed!")

if __name__ == "__main__":
    asyncio.run(test_crisis_endpoints())
