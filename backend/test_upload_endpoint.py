#!/usr/bin/env python3
"""
Test the upload endpoint to see what fields it actually requires
"""

import requests
import json

BASE_URL = "http://localhost:8001/api/v1"

def test_upload_endpoint():
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
    
    print("🔍 TESTING UPLOAD ENDPOINT REQUIREMENTS")
    print("=" * 50)
    
    # Test different payloads to see what works
    test_payloads = [
        {
            "original_filename": "test.jpg",
            "file_size": 1024000,
            "mime_type": "image/jpeg",
            "file_type": "image"
        },
        {
            "file_name": "test.jpg", 
            "file_size": 1024000,
            "file_type": "image"
        },
        {
            "filename": "test.jpg",
            "filesize": 1024000,
            "filetype": "image"
        }
    ]
    
    for i, payload in enumerate(test_payloads):
        print(f"\n🧪 Test {i+1}: {payload}")
        response = requests.post(
            f"{BASE_URL}/uploads/presigned-url",
            json=payload,
            headers=headers
        )
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.text}")
        else:
            print(f"   ✅ Success: {response.json()}")
            break

if __name__ == "__main__":
    test_upload_endpoint()
