#!/usr/bin/env python3
"""
Quick test to verify crisis fixes
"""

import asyncio
import aiohttp
import os

async def quick_test():
    print("🚀 Quick Crisis System Test")
    
    token = os.getenv('TEST_TOKEN')
    if not token:
        print("❌ No TEST_TOKEN")
        return
    
    base_url = "http://localhost:8001/api/v1/crisis-support"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    async with aiohttp.ClientSession() as session:
        
        print("1. Testing resources endpoint:")
        async with session.get(f"{base_url}/resources", headers=headers) as resp:
            print(f"   Status: {resp.status}")
            if resp.status == 200:
                data = await resp.json()
                print(f"   ✅ Resources: {len(data)} items")
            else:
                error = await resp.text()
                print(f"   ❌ Error: {error[:100]}...")
        
        print("\n2. Testing preferences endpoint:")
        async with session.get(f"{base_url}/preferences", headers=headers) as resp:
            print(f"   Status: {resp.status}")
            if resp.status == 200:
                data = await resp.json()
                print(f"   ✅ Preferences: User {data.get('user_id')}")
            else:
                error = await resp.text()
                print(f"   ❌ Error: {error[:100]}...")
        
        print("\n3. Testing emergency contacts:")
        async with session.get(f"{base_url}/emergency-contacts", headers=headers) as resp:
            print(f"   Status: {resp.status}")
            if resp.status == 200:
                data = await resp.json()
                print(f"   ✅ Contacts: {len(data)} items")
            else:
                error = await resp.text()
                print(f"   ❌ Error: {error[:100]}...")

if __name__ == "__main__":
    asyncio.run(quick_test())
