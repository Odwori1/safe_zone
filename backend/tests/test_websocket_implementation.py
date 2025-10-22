#!/usr/bin/env python3
"""
TEST WEBSOCKET IMPLEMENTATION
"""
import asyncio
import websockets
import json
import uuid

async def test_websocket_connection():
    """Test WebSocket connection and authentication"""
    
    print("🔌 TESTING WEBSOCKET IMPLEMENTATION")
    print("=" * 50)
    
    # First, we need to get a valid JWT token
    import requests
    
    # Register and login to get token
    email = f"ws_test_{uuid.uuid4().hex[:8]}@example.com"
    username = f"ws_user_{uuid.uuid4().hex[:8]}"
    password = "securepassword123"
    
    print(f"1. CREATING TEST USER: {email}")
    
    # Register
    response = requests.post(
        "http://localhost:8001/api/v1/auth/register",
        json={
            "email": email,
            "username": username,
            "password": password,
            "full_name": "WebSocket Test User"
        }
    )
    
    if response.status_code != 200:
        print(f"❌ Registration failed: {response.text}")
        return
    
    print("✅ User registered")
    
    # Login to get token
    response = requests.post(
        "http://localhost:8001/api/v1/auth/login", 
        json={
            "email": email,
            "password": password
        }
    )
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.text}")
        return
    
    token_data = response.json()
    access_token = token_data.get('access_token')
    
    if not access_token:
        print("❌ No access token in response")
        return
    
    print(f"✅ Got access token: {access_token[:20]}...")
    
    print("\n2. TESTING WEBSOCKET CONNECTION...")
    
    try:
        # Try to connect to WebSocket with token
        async with websockets.connect(
            f"ws://localhost:8001/ws?token={access_token}",
            ping_interval=20,
            ping_timeout=20
        ) as websocket:
            print("✅ WebSocket connection established!")
            
            # Test sending a message
            test_message = {
                "type": "test",
                "content": "Hello WebSocket"
            }
            
            await websocket.send(json.dumps(test_message))
            print("✅ Test message sent")
            
            # Try to receive a response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"✅ Received response: {response}")
            except asyncio.TimeoutError:
                print("⚠️  No response received (might be normal)")
                
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ WebSocket connection failed: {e}")
        print("   This might mean:")
        print("   - WebSocket endpoint not enabled")
        print("   - Authentication failed") 
        print("   - CORS issues")
    except Exception as e:
        print(f"❌ WebSocket error: {e}")

def check_websocket_files():
    """Check WebSocket implementation files"""
    print("\n3. CHECKING WEBSOCKET FILES:")
    print("-" * 30)
    
    import os
    
    ws_files = {
        "websocket.py": "app/api/endpoints/websocket.py",
        "websocket_auth.py": "app/services/websocket_auth.py", 
        "connection_manager.py": "app/services/connection_manager_enhanced.py",
        "redis_service.py": "app/services/redis_service.py"
    }
    
    for name, path in ws_files.items():
        exists = os.path.exists(path)
        status = "✅" if exists else "❌"
        print(f"   {status} {name}: {path}")
        
        if exists:
            size = os.path.getsize(path)
            print(f"        Size: {size} bytes")

if __name__ == "__main__":
    check_websocket_files()
    asyncio.run(test_websocket_connection())
