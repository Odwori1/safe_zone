import requests
import json

print("🔍 DEBUGGING ACTUAL ISSUE")
print("=" * 50)

# Get auth token
auth_response = requests.post(
    'http://localhost:8001/api/v1/auth/login',
    json={'email': 'test_bc64ceba@example.com', 'password': 'securepassword123'}
)

if auth_response.status_code == 200:
    token = auth_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # Create a test post
    post_response = requests.post(
        'http://localhost:8001/api/v1/posts/',
        headers=headers,
        json={
            "content": "Debug post",
            "content_type": "text",
            "mood": "calm",
            "visibility": "public",
            "is_anonymous": False
        }
    )
    
    if post_response.status_code == 200:
        post_id = post_response.json()['id']
        print(f"✅ Test post created: {post_id}")
        
        # Try the upload endpoint with detailed error info
        upload_response = requests.post(
            f'http://localhost:8001/api/v1/files/posts/{post_id}/presigned-upload',
            headers=headers,
            json={
                "filename": "test.mp4",
                "file_type": "video", 
                "mime_type": "video/mp4",
                "file_size": 10485760,
                "duration": 60
            }
        )
        
        print(f"Response status: {upload_response.status_code}")
        if upload_response.status_code != 200:
            print(f"Error response: {upload_response.text}")
        else:
            print("✅ Success!")
            print(f"Response: {upload_response.json()}")
            
