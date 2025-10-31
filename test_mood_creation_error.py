#!/usr/bin/env python3
"""
Test to reproduce the exact mood creation error
"""
import requests
import json

# Test data that should work
test_data = {
    "mood": "calm",
    "intensity": 7,
    "notes": "Test mood entry",
    "triggers": ["testing"],
    "activities": ["debugging"]
}

# First get auth token
login_data = {
    "email": "developer_test@example.com",
    "password": "DeveloperPass123!"
}

try:
    # Login
    login_response = requests.post(
        "http://localhost:8001/api/v1/auth/login",
        json=login_data
    )
    
    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        print(f"✅ Got token: {token[:20]}...")
        
        # Try to create mood entry
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        create_response = requests.post(
            "http://localhost:8001/api/v1/mood/entries/",
            json=test_data,
            headers=headers
        )
        
        print(f"📤 Create request status: {create_response.status_code}")
        print(f"📥 Create response: {create_response.text}")
        
    else:
        print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
        
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
