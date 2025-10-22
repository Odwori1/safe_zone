#!/usr/bin/env python3
"""
CHECK WEBSOCKET AUTHENTICATION
"""
import asyncio
import websockets
import json
import uuid
import requests

async def test_websocket_auth_detailed():
    """Test WebSocket authentication in detail"""
    
    print("🔐 TESTING WEBSOCKET AUTHENTICATION")
    print("=" * 50)
    
    # Create test user and get token
    email = f"ws_auth_test_{uuid.uuid4().hex[:8]}@example.com"
    username = f"ws_auth_user_{uuid.uuid4().hex[:8]}"
    password = "securepassword123"
    
    print(f"1. CREATING TEST USER: {email}")
    
    # Register
    response = requests.post(
        "http://localhost:8001/api/v1/auth/register",
        json={
            "email": email,
            "username": username,
            "password": password,
            "full_name": "WebSocket Auth Test User"
        }
    )
    
    if response.status_code != 200:
        print(f"❌ Registration failed: {response.text}")
        return
    
    user_data = response.json()
    user_id = user_data.get('id')
    print(f"✅ User registered with ID: {user_id}")
    
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
    
    print("\n2. TESTING WEBSOCKET ENDPOINTS...")
    
    # Test different WebSocket endpoint patterns
    endpoints = [
        "/ws",
        "/api/v1/ws", 
        "/websocket",
        "/api/v1/websocket"
    ]
    
    for endpoint in endpoints:
        print(f"\nTesting endpoint: {endpoint}")
        
        try:
            async with websockets.connect(
                f"ws://localhost:8001{endpoint}?token={access_token}",
                ping_interval=20,
                ping_timeout=20
            ) as websocket:
                print(f"✅ Connected to {endpoint}")
                
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
            print(f"❌ Connection failed with status: {e.status_code}")
            if e.status_code == 403:
                print("   🔒 FORBIDDEN: Authentication failed")
            elif e.status_code == 404:
                print("   📍 NOT FOUND: Endpoint doesn't exist")
        except Exception as e:
            print(f"❌ Connection error: {e}")

def check_websocket_auth_implementation():
    """Check WebSocket authentication implementation"""
    
    print("\n3. CHECKING WEBSOCKET AUTH IMPLEMENTATION:")
    print("-" * 40)
    
    try:
        with open("app/api/endpoints/websocket.py", "r") as f:
            content = f.read()
        
        # Check authentication patterns
        auth_patterns = [
            "token" in content,
            "jwt" in content.lower(),
            "auth" in content.lower(),
            "verify" in content,
            "authenticate" in content
        ]
        
        auth_count = sum(auth_patterns)
        print(f"   Authentication patterns found: {auth_count}/5")
        
        # Check specific authentication code
        if "WebSocketAuth" in content:
            print("   ✅ Using WebSocketAuth class")
        if "verify_websocket_token" in content:
            print("   ✅ Using verify_websocket_token function")
        if "HTTPException" in content and "403" in content:
            print("   ✅ 403 Forbidden exceptions defined")
            
        # Check the actual endpoint path
        import re
        match = re.search(r'@router\.websocket\("([^"]+)"', content)
        if match:
            print(f"   📍 WebSocket endpoint: {match.group(1)}")
        else:
            print("   ❌ Could not find WebSocket endpoint path")
            
    except Exception as e:
        print(f"Error reading websocket.py: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket_auth_detailed())
    check_websocket_auth_implementation()
