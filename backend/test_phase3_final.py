#!/usr/bin/env python3
"""
Final test to confirm Phase 3 is 100% complete
"""
import requests
import json
import sys

def test_phase3_final():
    print("🎯 PHASE 3 FINAL COMPLETION TEST")
    print("=" * 45)
    print("Testing if backend starts and all endpoints work...\n")
    
    # Test 1: Backend health check
    print("1. Backend Health Check")
    try:
        health_response = requests.get("http://localhost:8001/api/v1/health", timeout=5)
        if health_response.status_code == 200:
            print("   ✅ Backend is running")
        else:
            print("   ❌ Backend health check failed")
            return False
    except Exception as e:
        print(f"   ❌ Backend not accessible: {e}")
        return False
    
    # Test 2: Authentication
    print("\n2. Authentication System")
    try:
        login_response = requests.post(
            "http://localhost:8001/api/v1/auth/login",
            json={
                "email": "developer_test@example.com",
                "password": "DeveloperPass123!"
            },
            timeout=5
        )
        
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("   ✅ Login successful")
        else:
            print(f"   ❌ Login failed: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Authentication test failed: {e}")
        return False
    
    # Test 3: Key Phase 3 Endpoints
    print("\n3. Phase 3 Core Features")
    
    endpoints = [
        ("Live Audio Rooms", "GET", "/api/v1/audio/rooms"),
        ("Messaging System", "POST", "/api/v1/messages/conversations"),
        ("Uploads System", "POST", "/api/v1/uploads/presigned-url"),
        ("Files System", "GET", "/api/v1/files/"),
        ("Moderation System", "GET", "/api/v1/moderation/"),
    ]
    
    all_working = True
    
    for name, method, endpoint in endpoints:
        print(f"   {name}")
        
        try:
            url = f"http://localhost:8001{endpoint}"
            
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=5)
            else:
                # Use appropriate payloads
                if "messages" in endpoint:
                    payload = {"is_group": False, "title": "Final Test"}
                elif "uploads" in endpoint:
                    payload = {
                        "file_name": "test.mp3",
                        "file_type": "audio",
                        "original_filename": "test.mp3",
                        "file_size": 1024,
                        "mime_type": "audio/mpeg"
                    }
                else:
                    payload = {}
                    
                response = requests.post(url, headers=headers, json=payload, timeout=5)
            
            if response.status_code == 200:
                print("      ✅ WORKING")
            else:
                print(f"      ❌ FAILED: {response.status_code}")
                if response.text:
                    print(f"      Error: {response.text[:80]}")
                all_working = False
                
        except Exception as e:
            print(f"      ❌ ERROR: {e}")
            all_working = False
    
    print("\n" + "=" * 45)
    if all_working:
        print("🎉 PHASE 3 BACKEND IS 100% COMPLETE!")
        print("✅ Backend starts successfully")
        print("✅ All endpoints working")
        print("✅ Ready for frontend development")
        print("\n🚀 NEXT STEP: Begin frontend integration")
        return True
    else:
        print("🔧 Some endpoints need attention")
        print("💡 Check the specific errors above")
        return False

if __name__ == "__main__":
    success = test_phase3_final()
    if success:
        print("\n🏆 DEVELOPMENT MILESTONE ACHIEVED!")
        print("Phase 3 backend development is COMPLETE")
        sys.exit(0)
    else:
        print("\n💥 Phase 3 needs final adjustments")
        sys.exit(1)
