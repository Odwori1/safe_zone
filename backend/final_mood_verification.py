#!/usr/bin/env python3
"""
Final comprehensive verification of Mood Tracker
"""

import requests
import json

def final_verification():
    print("🎯 FINAL MOOD TRACKER VERIFICATION")
    print("=" * 50)
    
    credentials = {
        "email": "api_test@example.com", 
        "password": "testpassword123"
    }
    
    try:
        # 1. Authentication
        print("1. 🔐 Testing Authentication...")
        auth_response = requests.post(
            "http://localhost:8001/api/v1/auth/login",
            json=credentials
        )
        
        if auth_response.status_code == 200:
            token = auth_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("   ✅ Authentication: SUCCESS")
        else:
            print("   ❌ Authentication: FAILED")
            return False
        
        # 2. Test all mood endpoints
        print("2. 📊 Testing Mood Endpoints...")
        
        # Create mood entry
        mood_data = {
            "mood": "accomplished", 
            "intensity": 9,
            "notes": "Successfully completed Phase 2, Item 7!"
        }
        
        create_response = requests.post(
            "http://localhost:8001/api/v1/mood/entries/",
            json=mood_data,
            headers=headers
        )
        
        if create_response.status_code in [200, 201]:
            entry_id = create_response.json()["id"]
            print("   ✅ Create Mood Entry: SUCCESS")
        else:
            print("   ❌ Create Mood Entry: FAILED")
            return False
        
        # Get mood entries
        entries_response = requests.get(
            "http://localhost:8001/api/v1/mood/entries/",
            headers=headers
        )
        
        if entries_response.status_code == 200:
            entries = entries_response.json()
            print(f"   ✅ Get Mood Entries: SUCCESS ({entries['total']} entries)")
        else:
            print("   ❌ Get Mood Entries: FAILED")
            return False
        
        # Get mood statistics
        stats_response = requests.get(
            "http://localhost:8001/api/v1/mood/stats/",
            headers=headers
        )
        
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f"   ✅ Get Mood Stats: SUCCESS ({stats['total_entries']} total)")
        else:
            print("   ❌ Get Mood Stats: FAILED")
            return False
        
        # Update mood entry
        update_data = {"mood": "proud", "intensity": 10}
        update_response = requests.put(
            f"http://localhost:8001/api/v1/mood/entries/{entry_id}",
            json=update_data,
            headers=headers
        )
        
        if update_response.status_code == 200:
            print("   ✅ Update Mood Entry: SUCCESS")
        else:
            print("   ❌ Update Mood Entry: FAILED")
            return False
        
        # Delete mood entry
        delete_response = requests.delete(
            f"http://localhost:8001/api/v1/mood/entries/{entry_id}",
            headers=headers
        )
        
        if delete_response.status_code == 200:
            print("   ✅ Delete Mood Entry: SUCCESS")
        else:
            print("   ❌ Delete Mood Entry: FAILED")
            return False
        
        print("=" * 50)
        print("🎉 ALL MOOD TRACKER ENDPOINTS VERIFIED!")
        print("📋 Ready to proceed to Phase 2, Item 8: Crisis Resources")
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    final_verification()
