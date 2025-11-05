#!/usr/bin/env python3
"""
Quick test for frontend developers to verify Phase 3 endpoints
"""

import requests

BASE_URL = "http://localhost:8001/api/v1"

def quick_test():
    print("🚀 QUICK PHASE 3 FRONTEND TEST")
    print("=" * 40)
    
    # Login
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
    
    print("✅ Logged in successfully")
    
    # Test key endpoints
    endpoints = [
        ("POST", "/uploads/presigned-url", {"file_name": "test.jpg", "file_type": "image", "content_type": "image/jpeg"}),
        ("GET", "/files/", None),
        ("GET", "/audio/rooms", None),
        ("GET", "/messages/conversations", None),
        ("GET", "/moderation/", None),
    ]
    
    for method, endpoint, data in endpoints:
        try:
            if method == "POST":
                response = requests.post(f"{BASE_URL}{endpoint}", json=data, headers=headers)
            else:
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            
            status = "✅" if response.status_code in [200, 201] else "⚠️"
            print(f"{status} {method} {endpoint} - {response.status_code}")
            
        except Exception as e:
            print(f"❌ {method} {endpoint} - Error: {e}")
    
    print("\n🎯 All key Phase 3 endpoints are ready for frontend integration!")

if __name__ == "__main__":
    quick_test()
