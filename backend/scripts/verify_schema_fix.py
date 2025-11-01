#!/usr/bin/env python3
"""
Verify the schema fix worked
"""

import asyncio
import aiohttp
import os

async def verify_fix():
    token = os.getenv('TEST_TOKEN')
    if not token:
        print("❌ No TEST_TOKEN")
        return
    
    base_url = "http://localhost:8001/api/v1/crisis-support"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    async with aiohttp.ClientSession() as session:
        print("Testing preferences endpoint after schema fix:")
        async with session.get(f"{base_url}/preferences", headers=headers) as resp:
            print(f"Status: {resp.status}")
            if resp.status == 200:
                data = await resp.json()
                print("✅ SUCCESS! Preferences endpoint working!")
                print(f"   User ID: {data.get('user_id')}")
                print(f"   ID: {data.get('id')}")
                print(f"   Language: {data.get('preferred_language')}")
            else:
                error = await resp.text()
                print(f"❌ Still failing: {error}")

if __name__ == "__main__":
    asyncio.run(verify_fix())
