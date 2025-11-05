#!/usr/bin/env python3
"""
Debug the complete upload process to identify where it fails
"""

import requests
import json

BASE_URL = "http://localhost:8001/api/v1"

def debug_upload_process():
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
    
    print("🔍 DEBUGGING COMPLETE UPLOAD PROCESS")
    print("=" * 60)
    
    # 1. Get presigned URL
    print("\n1. 📤 GETTING PRESIGNED URL...")
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
    
    if response.status_code != 200:
        print(f"❌ Failed to get presigned URL: {response.status_code}")
        print(f"Error: {response.text}")
        return
        
    presigned_data = response.json()
    print("✅ Presigned URL received:")
    print(json.dumps(presigned_data, indent=2))
    
    # 2. Test the actual file upload
    print("\n2. 🚀 TESTING FILE UPLOAD TO PRESIGNED URL...")
    
    # Create a small test file content
    test_content = b"fake image content for testing"
    
    upload_headers = {
        'Content-Type': presigned_data['headers']['Content-Type']
    }
    
    print(f"Upload URL: {presigned_data['presigned_url']}")
    print(f"Method: {presigned_data['method']}")
    print(f"Headers: {upload_headers}")
    
    # Try uploading to the presigned URL
    full_upload_url = f"http://localhost:8001{presigned_data['presigned_url']}"
    print(f"Full URL: {full_upload_url}")
    
    upload_response = requests.put(
        full_upload_url,
        data=test_content,
        headers=upload_headers
    )
    
    print(f"Upload response status: {upload_response.status_code}")
    print(f"Upload response headers: {dict(upload_response.headers)}")
    
    if upload_response.status_code >= 200 and upload_response.status_code < 300:
        print("✅ File upload successful!")
        
        # 3. Test if we can access the uploaded file
        print("\n3. 🔍 TESTING FILE ACCESS...")
        access_url = f"http://localhost:8001{presigned_data['presigned_url']}"
        access_response = requests.get(access_url)
        print(f"File access status: {access_response.status_code}")
        
    else:
        print(f"❌ File upload failed: {upload_response.status_code}")
        print(f"Upload error: {upload_response.text}")

if __name__ == "__main__":
    debug_upload_process()
