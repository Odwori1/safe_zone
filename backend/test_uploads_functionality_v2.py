#!/usr/bin/env python3
"""
Test uploads functionality specifically - UPDATED for correct endpoints
"""
import requests
import json

def test_uploads_functionality():
    print("📁 TESTING UPLOADS FUNCTIONALITY")
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
    
    # 2. Test upload URL generation (main endpoint)
    print("\n2. Testing upload URL generation...")
    try:
        upload_request = {
            "filename": "test_audio.mp3",
            "duration": 60
        }
        
        response = requests.post(
            'http://localhost:8001/api/v1/uploads/audio/upload-url',
            json=upload_request,
            headers=headers
        )
        
        if response.status_code == 200:
            print("   ✅ Upload URL generation working")
            upload_data = response.json()
            print(f"   - Upload URL: {upload_data.get('upload_url', 'N/A')}")
            print(f"   - File ID: {upload_data.get('file_id', 'N/A')}")
        else:
            print(f"   ❌ Upload URL generation failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"   ❌ Upload URL test error: {e}")
    
    # 3. Test file uploads list
    print("\n3. Testing file uploads list...")
    try:
        response = requests.get('http://localhost:8001/api/v1/uploads/files', headers=headers)
        if response.status_code == 200:
            uploads = response.json()
            print(f"   ✅ File uploads list working - Found {len(uploads)} uploads")
            for upload in uploads[:2]:  # Show first 2 uploads
                print(f"   - {upload.get('filename', 'N/A')} (ID: {upload.get('id', 'N/A')})")
        else:
            print(f"   ❌ File uploads list failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ File uploads test error: {e}")
    
    # 4. Test API documentation for uploads section
    print("\n4. Testing API documentation...")
    try:
        response = requests.get('http://localhost:8001/docs')
        if response.status_code == 200:
            if 'uploads' in response.text:
                print("   ✅ Uploads endpoints documented in API docs")
                # Check for specific upload endpoints
                if '/api/v1/uploads/audio/upload-url' in response.text:
                    print("   ✅ Audio upload URL endpoint documented")
                else:
                    print("   ❌ Audio upload URL endpoint missing")
            else:
                print("   ❌ Uploads endpoints missing from API docs")
        else:
            print(f"   ❌ API docs unavailable: {response.status_code}")
    except Exception as e:
        print(f"   ❌ API docs test error: {e}")
    
    # 5. Test creating an audio post with the upload
    print("\n5. Testing audio post creation...")
    try:
        audio_post_data = {
            'content': 'Test audio post with upload',
            'content_type': 'audio',
            'visibility': 'public',
            'is_anonymous': False,
            'audio_url': '/uploads/test_audio.mp3',  # Mock URL for testing
            'audio_duration': 60,
            'file_size': 1024000,  # 1MB mock
            'mime_type': 'audio/mpeg'
        }
        
        response = requests.post('http://localhost:8001/api/v1/posts/', 
                               json=audio_post_data, headers=headers)
        
        if response.status_code == 200:
            print("   ✅ Audio post creation working")
            post_data = response.json()
            print(f"   - Created post ID: {post_data['id']}")
            print(f"   - Content type: {post_data.get('content_type')}")
        else:
            print(f"   ❌ Audio post creation failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Audio post creation error: {e}")
    
    print("\n" + "=" * 40)
    print("📁 UPLOADS FUNCTIONALITY TEST COMPLETE")
    
    return True

if __name__ == "__main__":
    test_uploads_functionality()
