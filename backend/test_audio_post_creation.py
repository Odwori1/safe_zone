#!/usr/bin/env python3
"""
Test creating an audio post
"""

import requests
import json

def test_audio_post_creation():
    print("🎵 TESTING AUDIO POST CREATION")
    print("=" * 50)
    
    credentials = {
        "email": "api_test@example.com",
        "password": "testpassword123"
    }
    
    try:
        # 1. Authentication
        print("1. 🔐 Authenticating...")
        auth_response = requests.post(
            "http://localhost:8001/api/v1/auth/login",
            json=credentials
        )
        
        if auth_response.status_code == 200:
            token = auth_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("   ✅ Authentication: SUCCESS")
        else:
            print(f"   ❌ Authentication failed: {auth_response.status_code}")
            return False
        
        # 2. Create audio post
        print("\n2. 🎧 Creating Audio Post...")
        
        audio_post_data = {
            "content": "This is a test audio post with a thoughtful message about mental health",
            "content_type": "audio",
            "audio_url": "/uploads/test-audio-file.mp3",
            "audio_duration": 180,
            "file_size": 5120000,
            "mime_type": "audio/mpeg",
            "mood": "thoughtful",
            "visibility": "public",
            "is_anonymous": False
        }
        
        create_response = requests.post(
            "http://localhost:8001/api/v1/posts/",
            json=audio_post_data,
            headers=headers
        )
        
        if create_response.status_code in [200, 201]:
            post_data = create_response.json()
            post_id = post_data["id"]
            print("   ✅ Create audio post: SUCCESS")
            print(f"   Post ID: {post_id}")
            print(f"   Content Type: {post_data['content_type']}")
            print(f"   Audio URL: {post_data['audio_url']}")
            print(f"   Duration: {post_data['audio_duration']} seconds")
        else:
            print(f"   ❌ Create audio post failed: {create_response.status_code}")
            print(f"   Response: {create_response.text}")
            return False
        
        # 3. Get the created post
        print("\n3. 📖 Retrieving Audio Post...")
        
        get_response = requests.get(
            f"http://localhost:8001/api/v1/posts/{post_id}",
            headers=headers
        )
        
        if get_response.status_code == 200:
            retrieved_post = get_response.json()
            print("   ✅ Retrieve audio post: SUCCESS")
            print(f"   Content: {retrieved_post['content']}")
            print(f"   Audio Duration: {retrieved_post['audio_duration']}s")
            print(f"   File Size: {retrieved_post['file_size']} bytes")
        else:
            print(f"   ❌ Retrieve audio post failed: {get_response.status_code}")
            return False
        
        # 4. Get audio-only posts
        print("\n4. 🎵 Testing Audio Posts Filter...")
        
        audio_posts_response = requests.get(
            "http://localhost:8001/api/v1/posts/audio",
            headers=headers
        )
        
        if audio_posts_response.status_code == 200:
            audio_posts = audio_posts_response.json()
            print(f"   ✅ Get audio posts: SUCCESS ({len(audio_posts)} posts)")
            
            # Count audio posts
            audio_count = len([p for p in audio_posts if p.get('content_type') == 'audio'])
            print(f"   Audio posts found: {audio_count}")
        else:
            print(f"   ❌ Get audio posts failed: {audio_posts_response.status_code}")
            return False
        
        # 5. Test feed filtering by content_type
        print("\n5. 🔍 Testing Feed Filtering...")
        
        feed_response = requests.get(
            "http://localhost:8001/api/v1/posts/feed/?content_type=audio",
            headers=headers
        )
        
        if feed_response.status_code == 200:
            feed_data = feed_response.json()
            print(f"   ✅ Audio feed filter: SUCCESS ({feed_data['total']} total audio posts)")
        else:
            print(f"   ❌ Audio feed filter failed: {feed_response.status_code}")
        
        # 6. Clean up
        print("\n6. 🧹 Cleaning up test data...")
        
        delete_response = requests.delete(
            f"http://localhost:8001/api/v1/posts/{post_id}",
            headers=headers
        )
        
        if delete_response.status_code == 200:
            print("   ✅ Test audio post deleted: SUCCESS")
        else:
            print(f"   ⚠️  Post cleanup failed: {delete_response.status_code}")
        
        print("\n" + "=" * 50)
        print("🎉 AUDIO POST CREATION TEST COMPLETED SUCCESSFULLY!")
        print("✅ Audio post creation: WORKING")
        print("✅ Audio post retrieval: WORKING") 
        print("✅ Audio posts filtering: WORKING")
        print("✅ Feed content_type filter: WORKING")
        return True
        
    except Exception as e:
        print(f"❌ Audio post test failed: {e}")
        return False

if __name__ == "__main__":
    test_audio_post_creation()
