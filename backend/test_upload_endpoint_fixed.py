#!/usr/bin/env python3
"""
Test the upload endpoint with the correct field names
"""

import requests
import json

BASE_URL = "http://localhost:8001/api/v1"

def test_upload_endpoint_fixed():
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
    
    print("🔍 TESTING UPLOAD ENDPOINT WITH CORRECT FIELDS")
    print("=" * 50)
    
    # Test the correct payload based on error messages
    correct_payload = {
        "file_name": "test.jpg",        # Required by backend
        "original_filename": "test.jpg", # Required by backend  
        "file_size": 1024000,
        "mime_type": "image/jpeg",
        "file_type": "image"
    }
    
    print(f"🧪 Correct payload: {correct_payload}")
    response = requests.post(
        f"{BASE_URL}/uploads/presigned-url",
        json=correct_payload,
        headers=headers
    )
    print(f"   Status: {response.status_code}")
    if response.status_code != 200:
        print(f"   Error: {response.text}")
    else:
        print(f"   ✅ Success: {response.json()}")

if __name__ == "__main__":
    test_upload_endpoint_fixed()
