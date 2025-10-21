import requests
import json

print("🔍 ANALYZING CURRENT IMPLEMENTATION PATTERNS")
print("=" * 50)

# Get auth token
auth_response = requests.post(
    'http://localhost:8001/api/v1/auth/login',
    json={'email': 'test_bc64ceba@example.com', 'password': 'securepassword123'}
)
token = auth_response.json()['access_token']

# Create a test post to see file handling
print("1. Testing post creation with file reference...")
post_data = {
    "content": "Test post for file analysis",
    "content_type": "video", 
    "mood": "calm",
    "visibility": "public",
    "is_anonymous": False,
    "video_url": "/uploads/test_video.mp4",
    "file_size": 10485760,
    "mime_type": "video/mp4"
}

post_response = requests.post(
    'http://localhost:8001/api/v1/posts/',
    headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
    json=post_data
)

if post_response.status_code == 200:
    post = post_response.json()
    print(f"✅ Post created: {post['id']}")
    print(f"   - Video URL: {post.get('video_url')}")
    print(f"   - Content Type: {post.get('content_type')}")
    
    # Check if file is stored locally or referenced
    if post.get('video_url', '').startswith('/uploads/'):
        print("   ⚠️  INSECURE: Direct file reference to local storage")
    else:
        print("   ✅ Secure file reference pattern")
else:
    print(f"❌ Post creation failed: {post_response.status_code}")

print("\n2. Checking current file upload endpoints...")
# Let's examine the actual endpoint implementations
import inspect
import importlib
import sys

try:
    # Dynamically import and check the uploads module
    spec = importlib.util.spec_from_file_location("uploads", "app/api/endpoints/uploads.py")
    uploads_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(uploads_module)
    
    # Check if we have direct file handling
    for name, obj in inspect.getmembers(uploads_module):
        if hasattr(obj, '__code__'):
            source = inspect.getsource(obj)
            if 'UploadFile' in source and 'file.file' in source:
                print(f"   ⚠️  INSECURE: Direct file handling in {name}")
            elif 'presigned' in source.lower():
                print(f"   ✅ Secure: Presigned URL pattern in {name}")
                
except Exception as e:
    print(f"   Could not analyze source: {e}")

print("=" * 50)
