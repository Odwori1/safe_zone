#!/usr/bin/env python3
"""
CORRECT Phase 3 Testing Guide - Use ACTUAL endpoints
"""
import requests
import json

def correct_testing_guide():
    print("🎯 CORRECT PHASE 3 TESTING GUIDE")
    print("=" * 45)
    print("Testing ACTUAL endpoints that exist in the system")
    print("")
    
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
    
    print("✅ Authentication working")
    print("")
    
    # CORRECT ENDPOINTS TO TEST
    correct_endpoints = [
        ("🎙️ Live Audio Rooms", "GET", "/api/v1/audio/rooms"),
        ("🎙️ Create Audio Room", "POST", "/api/v1/audio/rooms"),
        ("📤 Upload System", "POST", "/api/v1/uploads/presigned-url"),
        ("📁 Files System", "GET", "/api/v1/files/"),
        ("💬 Messaging - Conversations", "POST", "/api/v1/messages/conversations"),
        ("🛡️ Moderation Stats", "GET", "/api/v1/moderation/"),
        ("🛡️ Create Report", "POST", "/api/v1/moderation/reports"),
        ("📝 Create Post (supports audio/video)", "POST", "/api/v1/posts/"),
    ]
    
    print("🔍 TESTING CORRECT ENDPOINTS:")
    print("")
    
    for name, method, endpoint in correct_endpoints:
        print(f"{name}")
        print(f"  Endpoint: {method} {endpoint}")
        
        try:
            url = f"http://localhost:8001{endpoint}"
            
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=5)
            else:
                # Use appropriate payloads
                if "audio/rooms" in endpoint:
                    payload = {
                        "title": "Correct Test Room",
                        "description": "Testing correct endpoint",
                        "visibility": "public", 
                        "max_participants": 10,
                        "room_type": "support"
                    }
                elif "uploads" in endpoint:
                    payload = {
                        "file_name": "correct-test.mp3",
                        "file_type": "audio",
                        "original_filename": "correct-test.mp3",
                        "file_size": 1024,
                        "mime_type": "audio/mpeg"
                    }
                elif "messages" in endpoint:
                    payload = {"is_group": False, "title": "Correct Test"}
                elif "moderation/reports" in endpoint:
                    payload = {
                        "content_type": "post",
                        "content_id": "12345678-1234-1234-1234-123456789012",
                        "reason": "Correct test",
                        "description": "Testing correct endpoint"
                    }
                elif "posts" in endpoint:
                    payload = {
                        "content": "Test post that can have audio/video attachments",
                        "mood": "neutral",
                        "visibility": "public",
                        "is_anonymous": False
                    }
                else:
                    payload = {}
                
                response = requests.post(url, headers=headers, json=payload, timeout=5)
            
            if response.status_code == 200:
                print("  ✅ WORKING")
                if response.text and len(response.text) < 100:
                    print(f"  Response: {response.text}")
            else:
                print(f"  ❌ Status: {response.status_code}")
                if response.text:
                    print(f"  Error: {response.text[:80]}")
                    
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
        
        print("")

def explain_architecture():
    print("")
    print("🏗️ ARCHITECTURE EXPLANATION")
    print("=" * 45)
    print("")
    print("📋 HOW OUR SYSTEM WORKS:")
    print("")
    print("🎙️ Audio/Video Posts:")
    print("  - We DON'T have separate /audio/posts or /video/posts endpoints")
    print("  - We use SINGLE /api/v1/posts/ endpoint for ALL post types")
    print("  - Posts can have file attachments (audio, video, images)")
    print("")
    print("📤 File Uploads:")
    print("  - SINGLE /api/v1/uploads/presigned-url for ALL file types")
    print("  - Use 'file_type' parameter: 'audio', 'video', 'image', 'document'")
    print("")
    print("💬 Messaging:")
    print("  - Conversations: /api/v1/messages/conversations")
    print("  - Messages: /api/v1/messages/conversations/{id}/messages")
    print("")
    print("🎙️ Audio Rooms:")
    print("  - /api/v1/audio/rooms (NOT /audio-rooms)")
    print("")
    print("🛡️ Moderation:")
    print("  - Stats: /api/v1/moderation/")
    print("  - Reports: /api/v1/moderation/reports")
    print("")

if __name__ == "__main__":
    correct_testing_guide()
    explain_architecture()
