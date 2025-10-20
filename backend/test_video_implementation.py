#!/usr/bin/env python3
"""
Test Video Implementation - Phase 3, Item 2
"""
import requests
import json

def test_video_implementation():
    print("🎬 TESTING VIDEO IMPLEMENTATION")
    print("=" * 40)
    
    # 1. Authenticate
    login_data = {'email': 'test_bc64ceba@example.com', 'password': 'securepassword123'}
    response = requests.post('http://localhost:8001/api/v1/auth/login', json=login_data)
    
    if response.status_code != 200:
        print(f"❌ Authentication failed: {response.text}")
        return False
    
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    print("✅ Authentication working")

    # 2. Test Video Upload URL Generation
    print("\n2. Testing Video Upload URL Generation...")
    try:
        upload_request = {
            "filename": "test_video.mp4",
            "duration": 120,
            "width": 1920,
            "height": 1080
        }
        
        response = requests.post(
            'http://localhost:8001/api/v1/uploads/video/upload-url',
            json=upload_request,
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ Video upload URL generation working")
            upload_data = response.json()
            print(f"   - Upload URL: {upload_data.get('upload_url')}")
            print(f"   - File ID: {upload_data.get('file_id')}")
        else:
            print(f"❌ Video upload URL generation failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Video upload URL test error: {e}")

    # 3. Test Video Post Creation
    print("\n3. Testing Video Post Creation...")
    try:
        video_post_data = {
            'content': 'Test video post with upload system',
            'content_type': 'video',
            'visibility': 'public',
            'is_anonymous': False,
            'video_url': '/uploads/test_video.mp4',
            'video_duration': 120,
            'thumbnail_url': '/uploads/test_video_thumbnail.jpg',
            'video_width': 1920,
            'video_height': 1080,
            'file_size': 5242880,  # 5MB
            'mime_type': 'video/mp4'
        }
        
        response = requests.post('http://localhost:8001/api/v1/posts/', 
                               json=video_post_data, headers=headers)
        
        if response.status_code == 200:
            print("✅ Video post creation working")
            post_data = response.json()
            print(f"   - Created post ID: {post_data['id']}")
            print(f"   - Content type: {post_data.get('content_type')}")
            print(f"   - Video URL: {post_data.get('video_url')}")
        else:
            print(f"❌ Video post creation failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Video post creation error: {e}")

    # 4. Test Video Posts Endpoint
    print("\n4. Testing Video Posts Endpoint...")
    try:
        response = requests.get('http://localhost:8001/api/v1/posts/video', headers=headers)
        if response.status_code == 200:
            video_posts = response.json()
            print(f"✅ Video posts endpoint working - Found {len(video_posts)} video posts")
        else:
            print(f"❌ Video posts endpoint failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Video posts endpoint error: {e}")

    # 5. Test API Documentation for Video Endpoints
    print("\n5. Testing API Documentation...")
    try:
        response = requests.get('http://localhost:8001/docs')
        if response.status_code == 200:
            print("✅ API documentation available")
            if '/api/v1/uploads/video/upload-url' in response.text:
                print("✅ Video upload endpoints documented")
            else:
                print("❌ Video upload endpoints missing from docs")
        else:
            print(f"❌ API docs unavailable: {response.status_code}")
    except Exception as e:
        print(f"❌ API docs test error: {e}")

    print("\n" + "=" * 40)
    print("🎬 VIDEO IMPLEMENTATION TEST COMPLETE")
    
    return True

if __name__ == "__main__":
    test_video_implementation()
