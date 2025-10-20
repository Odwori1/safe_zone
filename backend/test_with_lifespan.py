#!/usr/bin/env python3
"""
Test that properly initializes database like FastAPI lifespan
"""
import asyncio
import requests
from app.database.database import init_db, close_db

async def test_with_proper_init():
    print("🧪 TESTING WITH PROPER DATABASE INIT")
    print("=" * 50)
    
    # Initialize database like FastAPI lifespan
    print("1. Initializing database...")
    await init_db()
    
    # Now test the endpoints
    print("2. Testing video posts endpoint...")
    try:
        # Authenticate
        login_data = {'email': 'test_bc64ceba@example.com', 'password': 'securepassword123'}
        response = requests.post('http://localhost:8001/api/v1/auth/login', json=login_data)
        token = response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Test video posts
        response = requests.get('http://localhost:8001/api/v1/posts/video', headers=headers)
        print(f"   Video posts status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ Video posts working: {len(response.json())} posts")
        else:
            print(f"   ❌ Video posts failed: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Test error: {e}")
    
    # Cleanup
    print("3. Closing database...")
    await close_db()
    print("✅ Test complete")

if __name__ == "__main__":
    asyncio.run(test_with_proper_init())
