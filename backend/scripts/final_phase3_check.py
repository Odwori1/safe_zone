#!/usr/bin/env python3
"""
Final comprehensive Phase 3 status check
"""

import asyncpg
import asyncio
import requests

async def final_check():
    print("🎯 FINAL PHASE 3 COMPREHENSIVE CHECK")
    print("=" * 60)
    
    # 1. Check database tables
    print("\n1. 🗄️  DATABASE TABLES CHECK")
    conn = await asyncpg.connect(
        host='127.0.0.1',
        port=5433,
        user='safe_zone_app_user',
        password='secure_app_password_2024',
        database='safe_zone'
    )
    
    phase3_tables = [
        'file_uploads', 'conversations', 'messages',
        'audio_rooms', 'audio_room_participants', 'content_reports', 'moderation_reports'
    ]
    
    for table in phase3_tables:
        exists = await conn.fetchval(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = $1)",
            table
        )
        status = "✅" if exists else "❌"
        print(f"   {status} {table}")
    
    await conn.close()
    
    # 2. Check API endpoints
    print("\n2. 🌐 API ENDPOINTS CHECK")
    
    # Login first
    login_data = {
        "email": "developer_test@example.com",
        "password": "DeveloperPass123!"
    }
    
    response = requests.post("http://localhost:8001/api/v1/auth/login", json=login_data)
    if response.status_code != 200:
        print("   ❌ Cannot login - stopping check")
        return
        
    token = response.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    endpoints = {
        "Audio Rooms": "/audio/rooms",
        "File Upload": "/uploads/presigned-url", 
        "Files": "/files/",
        "Conversations": "/messages/conversations",
        "Moderation": "/moderation/",
        "Posts": "/posts"
    }
    
    for name, endpoint in endpoints.items():
        try:
            if endpoint == "/uploads/presigned-url":
                response = requests.post(f"http://localhost:8001/api/v1{endpoint}", 
                                       json={"file_name": "test.txt", "file_type": "document"},
                                       headers=headers)
            else:
                response = requests.get(f"http://localhost:8001/api/v1{endpoint}", headers=headers)
            
            status = "✅" if response.status_code in [200, 201] else "⚠️" if response.status_code in [404, 405] else "❌"
            print(f"   {status} {name}: {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {name}: {endpoint} - Error: {e}")
    
    print("\n3. 📊 FINAL ASSESSMENT")
    print("   Based on the checks above:")
    print("   - If all tables exist ✅ → Database ready")
    print("   - If endpoints work ✅ → API ready") 
    print("   - Any ❌ indicates issues to fix")
    print("   - ⚠️  indicates endpoint might exist but method wrong")

if __name__ == "__main__":
    asyncio.run(final_check())
