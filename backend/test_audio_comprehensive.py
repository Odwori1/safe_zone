#!/usr/bin/env python3
"""
COMPREHENSIVE AUDIO SYSTEM TEST
Next Developer: Run this FIRST to diagnose all audio issues
"""
import requests
import json
import sys
import os

# Add the backend directory to Python path so we can import app modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_audio_system_comprehensive():
    print("🎵 COMPREHENSIVE AUDIO SYSTEM DIAGNOSIS")
    print("=" * 50)
    
    # 1. Test Authentication
    print("1. Testing Authentication...")
    try:
        login_data = {'email': 'test_bc64ceba@example.com', 'password': 'securepassword123'}
        response = requests.post('http://localhost:8001/api/v1/auth/login', json=login_data)
        
        if response.status_code != 200:
            print(f"❌ Authentication failed: {response.text}")
            return False
        
        token = response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        print("✅ Authentication working")
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False

    # 2. Test Uploads Endpoint Availability
    print("\n2. Testing Uploads Endpoint...")
    try:
        # Try to access uploads endpoint
        response = requests.get('http://localhost:8001/api/v1/uploads/', headers=headers)
        print(f"Uploads endpoint status: {response.status_code}")
        
        if response.status_code == 404:
            print("❌ Uploads endpoint not registered in main.py")
        elif response.status_code == 200:
            print("✅ Uploads endpoint available")
        else:
            print(f"⚠️ Uploads endpoint: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Uploads endpoint error: {e}")

    # 3. Test Audio Posts Endpoint
    print("\n3. Testing Audio Posts Endpoint...")
    try:
        response = requests.get('http://localhost:8001/api/v1/posts/audio', headers=headers)
        print(f"Audio posts endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Audio posts endpoint working")
            audio_posts = response.json()
            print(f"   Found {len(audio_posts)} audio posts")
        else:
            print(f"❌ Audio posts endpoint failed: {response.text}")
    except Exception as e:
        print(f"❌ Audio posts endpoint error: {e}")

    # 4. Test Create Audio Post (without file first)
    print("\n4. Testing Audio Post Creation...")
    try:
        audio_post_data = {
            'content': 'Test audio post description',
            'content_type': 'audio',
            'visibility': 'public',
            'is_anonymous': False,
            # 'audio_url' would normally come from upload
        }
        
        response = requests.post('http://localhost:8001/api/v1/posts/', 
                               json=audio_post_data, headers=headers)
        print(f"Audio post creation status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Audio post creation working")
            post_data = response.json()
            print(f"   Created post ID: {post_data['id']}")
            print(f"   Content type: {post_data.get('content_type')}")
        else:
            print(f"❌ Audio post creation failed: {response.text}")
    except Exception as e:
        print(f"❌ Audio post creation error: {e}")

    # 5. Test Schema Imports
    print("\n5. Testing Schema Imports...")
    try:
        # Try to import audio schemas
        from app.schemas.post import PostCreate, PostResponse
        print("✅ Post schema imports working")
        
        # Check if audio-related attributes exist
        post_create = PostCreate(
            content="test",
            content_type="text",  # Default value
            visibility="public",
            is_anonymous=False
        )
        print("✅ PostCreate schema instantiated")
        
    except ImportError as e:
        print(f"❌ Schema import error: {e}")
        print("   Check post.py vs post_audio.py conflicts")
    except Exception as e:
        print(f"❌ Schema instantiation error: {e}")

    # 6. Test Router Registration
    print("\n6. Testing Router Registration...")
    try:
        response = requests.get('http://localhost:8001/docs')
        if response.status_code == 200:
            print("✅ API docs available")
            # Check if uploads tag exists in docs
            if 'uploads' in response.text.lower():
                print("✅ Uploads endpoints documented")
            else:
                print("❌ Uploads endpoints missing from docs")
                
            # Check if audio endpoints exist in docs
            if '/api/v1/posts/audio' in response.text:
                print("✅ Audio posts endpoint documented")
            else:
                print("❌ Audio posts endpoint missing from docs")
        else:
            print("❌ API docs unavailable")
    except Exception as e:
        print(f"❌ Router test error: {e}")

    # 7. Test Database Schema for Audio Support
    print("\n7. Testing Database Schema...")
    try:
        # Test if we can query for audio posts
        response = requests.get('http://localhost:8001/api/v1/posts/', headers=headers)
        if response.status_code == 200:
            all_posts = response.json()
            audio_posts = [p for p in all_posts if p.get('content_type') == 'audio']
            print(f"✅ Database query working - Found {len(audio_posts)} audio posts in all posts")
        else:
            print(f"❌ Database query failed: {response.text}")
    except Exception as e:
        print(f"❌ Database test error: {e}")

    # 8. Test CRUD Operations
    print("\n8. Testing CRUD Operations...")
    try:
        # Test getting a single post to check CRUD operations
        if all_posts and len(all_posts) > 0:
            test_post_id = all_posts[0]['id']
            response = requests.get(f'http://localhost:8001/api/v1/posts/{test_post_id}', headers=headers)
            if response.status_code == 200:
                print("✅ Single post retrieval working")
            else:
                print(f"❌ Single post retrieval failed: {response.text}")
        else:
            print("⚠️ No posts available to test single retrieval")
    except Exception as e:
        print(f"❌ CRUD test error: {e}")

    # 9. Summary
    print("\n" + "=" * 50)
    print("🎵 AUDIO SYSTEM DIAGNOSIS COMPLETE")
    print("\nNEXT ACTIONS REQUIRED BASED ON TEST RESULTS:")
    print("1. Fix router registration in main.py if uploads endpoint missing")
    print("2. Resolve schema conflicts (post.py vs post_audio.py) if import errors")
    print("3. Implement S3 storage in app/core/storage.py")
    print("4. Complete uploads endpoints in app/api/endpoints/uploads.py")
    print("5. Update CRUD operations for audio in app/crud/post.py")
    print("6. Fix test imports in test_audio_support.py")
    
    return True

if __name__ == "__main__":
    test_audio_system_comprehensive()
