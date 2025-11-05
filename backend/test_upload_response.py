#!/usr/bin/env python3
"""
Test to see the exact backend response structure
"""

import requests
import json

BASE_URL = "http://localhost:8001/api/v1"

def test_upload_response():
    # Login first to get token
    login_data = {
        "email": "developer_test@example.com",
        "password": "DeveloperPass123!"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code != 200:
        print("❌ Login failed")
        return
        
    token = response.json()['access_token']
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    print("🔍 TESTING UPLOAD RESPONSE STRUCTURE")
    print("=" * 50)
    
    # Test the correct payload
    payload = {
        "file_name": "test.jpg",
        "original_filename": "test.jpg", 
        "file_size": 1024000,
        "mime_type": "image/jpeg",
        "file_type": "image"
    }
    
    response = requests.post(
        f"{BASE_URL}/uploads/presigned-url",
        json=payload,
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("✅ Backend response structure:")
        print(json.dumps(data, indent=2))
        
        print("\n📋 Response fields:")
        for key, value in data.items():
            print(f"  - {key}: {value}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_upload_response()
