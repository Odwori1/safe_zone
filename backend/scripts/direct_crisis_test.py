#!/usr/bin/env python3
"""
Direct test of crisis endpoints with detailed error reporting
"""

import asyncio
import aiohttp
import os

async def direct_test():
    token = os.getenv('TEST_TOKEN')
    if not token:
        print("❌ No TEST_TOKEN environment variable")
        print("Run: export TEST_TOKEN='your_token_here'")
        return
    
    print(f"🔑 Using token: {token[:20]}...")
    
    base_url = "http://localhost:8001/api/v1/crisis-support"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        print("\n1. Testing crisis resources (public endpoint):")
        async with session.get(f"{base_url}/resources", headers=headers) as resp:
            print(f"   Status: {resp.status}")
            if resp.status == 200:
                data = await resp.json()
                print(f"   ✅ SUCCESS: {len(data)} resources")
                for resource in data[:2]:
                    print(f"     - {resource.get('name')}")
            else:
                error = await resp.text()
                print(f"   ❌ FAILED: {error}")
        
        print("\n2. Testing crisis preferences:")
        async with session.get(f"{base_url}/preferences", headers=headers) as resp:
            print(f"   Status: {resp.status}")
            if resp.status == 200:
                data = await resp.json()
                print(f"   ✅ SUCCESS: Preferences retrieved")
                print(f"     User ID: {data.get('user_id')}")
                print(f"     Language: {data.get('preferred_language')}")
            elif resp.status == 404:
                print("   ℹ️  No preferences found (this is normal for first time)")
            else:
                error = await resp.text()
                print(f"   ❌ FAILED: {error}")
        
        print("\n3. Testing emergency contacts:")
        async with session.get(f"{base_url}/emergency-contacts", headers=headers) as resp:
            print(f"   Status: {resp.status}")
            if resp.status == 200:
                data = await resp.json()
                print(f"   ✅ SUCCESS: {len(data)} contacts")
            else:
                error = await resp.text()
                print(f"   ❌ FAILED: {error}")

if __name__ == "__main__":
    asyncio.run(direct_test())
