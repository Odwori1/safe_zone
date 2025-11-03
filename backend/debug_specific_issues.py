#!/usr/bin/env python3
"""
Debug specific Phase 3 issues without assuming database problems
"""
import requests
import json

def debug_phase3_issues():
    print("🔍 DEBUGGING SPECIFIC PHASE 3 ISSUES")
    print("=" * 45)
    
    # Get token
    login_response = requests.post(
        "http://localhost:8001/api/v1/auth/login",
        json={
            "email": "developer_test@example.com",
            "password": "DeveloperPass123!"
        }
    )
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Logged in successfully")
    
    # Test 1: Messaging system
    print("\n1. Testing messaging system...")
    
    # Create conversation
    conv_response = requests.post(
        "http://localhost:8001/api/v1/messages/conversations",
        headers=headers,
        json={"is_group": False, "title": "Debug Test"}
    )
    
    if conv_response.status_code == 200:
        conv_id = conv_response.json()["id"]
        print(f"   ✅ Conversation created: {conv_id}")
        
        # Try to create message
        msg_response = requests.post(
            f"http://localhost:8001/api/v1/messages/conversations/{conv_id}/messages",
            headers=headers,
            json={"content": "Debug test message", "content_type": "text"}
        )
        
        if msg_response.status_code == 200:
            print("   ✅ Message creation SUCCESSFUL!")
            print(f"   Message: {msg_response.json()}")
        else:
            print(f"   ❌ Message creation failed: {msg_response.status_code}")
            print(f"   Response: {msg_response.text}")
    else:
        print(f"   ❌ Conversation creation failed: {conv_response.status_code}")
        print(f"   Response: {conv_response.text}")
    
    # Test 2: Uploads system
    print("\n2. Testing uploads system...")
    
    upload_response = requests.post(
        "http://localhost:8001/api/v1/uploads/presigned-url",
        headers=headers,
        json={
            "file_name": "test.mp3",
            "file_type": "audio",
            "original_filename": "test.mp3",
            "file_size": 1024,
            "mime_type": "audio/mpeg"
        }
    )
    
    if upload_response.status_code == 200:
        print("   ✅ Uploads presigned URL SUCCESSFUL!")
        print(f"   Response: {upload_response.json()}")
    else:
        print(f"   ❌ Uploads failed: {upload_response.status_code}")
        print(f"   Response: {upload_response.text}")

if __name__ == "__main__":
    debug_phase3_issues()
