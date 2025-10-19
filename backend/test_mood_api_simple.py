#!/usr/bin/env python3
"""
Simple test for Mood API endpoints
"""

import requests
import json

def test_mood_endpoints():
    print("🧪 Testing Mood API Endpoints...")
    
    # Test if mood endpoints are registered
    try:
        response = requests.get("http://localhost:8001/docs")
        if response.status_code == 200:
            if "mood" in response.text.lower():
                print("✅ Mood endpoints registered in API docs")
            else:
                print("⚠️  Mood endpoints not found in docs (may need server restart)")
        else:
            print("⚠️  Cannot access API docs")
    except Exception as e:
        print(f"⚠️  Cannot connect to server: {e}")
        return
    
    # Test OpenAPI schema for mood endpoints
    try:
        response = requests.get("http://localhost:8001/openapi.json")
        if response.status_code == 200:
            openapi_spec = response.json()
            mood_paths = [path for path in openapi_spec.get('paths', {}).keys() if 'mood' in path]
            if mood_paths:
                print("✅ Mood endpoints found in OpenAPI spec:")
                for path in mood_paths:
                    print(f"   - {path}")
            else:
                print("❌ No mood endpoints found in OpenAPI spec")
        else:
            print("⚠️  Cannot access OpenAPI spec")
    except Exception as e:
        print(f"⚠️  Error checking OpenAPI spec: {e}")

if __name__ == "__main__":
    test_mood_endpoints()
