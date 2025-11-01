#!/usr/bin/env python3
"""
Get a new JWT token for testing
"""

import aiohttp
import asyncio
import json

async def get_new_token():
    print("🔑 Getting new JWT token...")
    
    login_data = {
        "email": "developer_test@example.com",
        "password": "DeveloperPass123!"
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                "http://localhost:8001/api/v1/auth/login",
                json=login_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    token = data.get('access_token')
                    print(f"✅ New token: {token}")
                    return token
                else:
                    print(f"❌ Login failed: {response.status}")
                    error_text = await response.text()
                    print(f"Error: {error_text}")
                    return None
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return None

if __name__ == "__main__":
    token = asyncio.run(get_new_token())
    if token:
        print(f"\n📋 Use this token for testing:")
        print(f"export TEST_TOKEN='{token}'")
