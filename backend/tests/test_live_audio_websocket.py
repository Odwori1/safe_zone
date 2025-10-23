#!/usr/bin/env python3
"""
Comprehensive WebSocket Tests for Live Audio Rooms
Following EXACT same patterns as messaging WebSocket tests
"""
import asyncio
import json
import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.database.database import init_db
from app.core.security import create_access_token

client = TestClient(app)

def test_websocket_authentication():
    """Test WebSocket authentication requirements"""
    print("🔐 TESTING WEBSOCKET AUTHENTICATION")
    print("=" * 50)
    
    # Test without token
    with client.websocket_connect("/api/v1/audio/test-room/ws") as websocket:
        try:
            websocket.receive_json()
            print("❌ No token rejection: FAILED")
        except:
            print("✅ No token rejection: PASSED")
    
    # Test with invalid token
    with client.websocket_connect("/api/v1/audio/test-room/ws?token=invalid") as websocket:
        try:
            websocket.receive_json()
            print("❌ Invalid token rejection: FAILED")
        except:
            print("✅ Invalid token rejection: PASSED")
    
    print("✅ WebSocket authentication tests completed")

def test_room_creation_api():
    """Test REST API for room creation"""
    print("\n🏠 TESTING ROOM CREATION API")
    print("=" * 50)
    
    # Get auth token for a test user
    from app.database.database import database
    async def get_test_user():
        await init_db()
        async with database.pool.acquire() as conn:
            user = await conn.fetchrow("SELECT id, email FROM users LIMIT 1")
            return user
    
    user = asyncio.run(get_test_user())
    token = create_access_token({"sub": str(user['id']), "email": user['email']})
    
    # Test room creation
    response = client.post(
        "/api/v1/audio/rooms",
        json={
            "title": "WebSocket Test Room",
            "description": "Test room for WebSocket functionality",
            "visibility": "public",
            "max_participants": 10,
            "room_type": "support"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        room_data = response.json()
        print(f"✅ Room creation API: PASSED (Room ID: {room_data['id']})")
        return room_data['id']
    else:
        print(f"❌ Room creation API: FAILED - {response.status_code}")
        return None

def test_room_joining_api(room_id, token):
    """Test REST API for room joining"""
    print("\n👥 TESTING ROOM JOINING API")
    print("=" * 50)
    
    response = client.post(
        f"/api/v1/audio/rooms/{room_id}/join",
        json={"role": "participant"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        print("✅ Room joining API: PASSED")
        return True
    else:
        print(f"❌ Room joining API: FAILED - {response.status_code}")
        return False

def test_room_participants_api(room_id, token):
    """Test REST API for getting participants"""
    print("\n📊 TESTING PARTICIPANTS API")
    print("=" * 50)
    
    response = client.get(
        f"/api/v1/audio/rooms/{room_id}/participants",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        participants_data = response.json()
        print(f"✅ Participants API: PASSED ({len(participants_data['participants'])} participants)")
        return True
    else:
        print(f"❌ Participants API: FAILED - {response.status_code}")
        return False

def test_room_listing_api(token):
    """Test REST API for room listing"""
    print("\n📋 TESTING ROOM LISTING API")
    print("=" * 50)
    
    response = client.get(
        "/api/v1/audio/rooms",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        rooms_data = response.json()
        print(f"✅ Room listing API: PASSED ({len(rooms_data)} rooms)")
        return True
    else:
        print(f"❌ Room listing API: FAILED - {response.status_code}")
        return False

def run_comprehensive_tests():
    """Run all comprehensive tests"""
    print("🚀 COMPREHENSIVE LIVE AUDIO ROOMS TEST SUITE")
    print("=" * 60)
    
    # Get test user and token
    from app.database.database import database
    async def setup():
        await init_db()
        async with database.pool.acquire() as conn:
            user = await conn.fetchrow("SELECT id, email FROM users LIMIT 1")
            return user, create_access_token({"sub": str(user['id']), "email": user['email']})
    
    user, token = asyncio.run(setup())
    
    # Run tests
    test_websocket_authentication()
    room_id = test_room_creation_api()
    
    if room_id:
        test_room_joining_api(room_id, token)
        test_room_participants_api(room_id, token)
    
    test_room_listing_api(token)
    
    print("\n" + "=" * 60)
    print("🎉 COMPREHENSIVE TEST SUITE COMPLETED")

if __name__ == "__main__":
    run_comprehensive_tests()
