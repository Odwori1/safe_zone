#!/usr/bin/env python3
"""
Check if all endpoints are properly registered
"""
import requests

def check_endpoints():
    base_url = "http://localhost:8001"
    token = "your_token_here"  # Replace with actual token
    
    headers = {"Authorization": f"Bearer {token}"}
    
    endpoints_to_check = [
        "/api/v1/users",
        "/api/v1/mood", 
        "/api/v1/uploads/files",
        "/api/v1/messages/conversations",
        "/api/v1/posts"  # This one works for comparison
    ]
    
    print("🔍 CHECKING ENDPOINT REGISTRATION")
    
    for endpoint in endpoints_to_check:
        url = base_url + endpoint
        try:
            response = requests.get(url, headers=headers, timeout=5)
            print(f"{endpoint}: {response.status_code} - {response.text[:100]}")
        except Exception as e:
            print(f"{endpoint}: ERROR - {e}")

if __name__ == "__main__":
    check_endpoints()
