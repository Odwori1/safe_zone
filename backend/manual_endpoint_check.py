#!/usr/bin/env python3
"""
Manual endpoint verification for Phase 3 features
"""

import requests
import json

BASE_URL = "http://localhost:8001/api/v1"

def manual_test():
    # First get auth token
    login_data = {
        "email": "developer_test@example.com",
        "password": "DeveloperPass123!"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        return None
        
    token_data = response.json()
    token = token_data['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🔍 MANUAL ENDPOINT VERIFICATION")
    print("=" * 40)
    
    # Test each endpoint category
    endpoints = {
        "Audio Endpoints": [
            "/uploads/audio/presigned-url",
            "/audio/posts"
        ],
        "Video Endpoints": [
            "/uploads/video/presigned-url", 
            "/video/posts"
        ],
        "File Upload": [
            "/uploads/file/presigned-url",
            "/uploads/image/presigned-url",
            "/files/my-files"
        ],
        "Messaging": [
            "/messages/conversations",
            "/messages/send"
        ],
        "Audio Rooms": [
            "/audio-rooms",
            "/audio-rooms/active"
        ],
        "Moderation": [
            "/moderation/reports",
            "/moderation/queue"
        ]
    }
    
    for category, category_endpoints in endpoints.items():
        print(f"\n📂 {category}:")
        for endpoint in category_endpoints:
            try:
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
                status = "✅" if response.status_code in [200, 405] else "❌"
                print(f"  {status} {endpoint} - Status: {response.status_code}")
            except Exception as e:
                print(f"  ❌ {endpoint} - Error: {e}")

if __name__ == "__main__":
    manual_test()
