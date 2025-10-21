import requests
import json

print("📁 TESTING CURRENT UPLOAD FLOW (PHASE 3)")
print("=" * 50)

# Get auth token
auth_response = requests.post(
    'http://localhost:8001/api/v1/auth/login',
    json={'email': 'test_bc64ceba@example.com', 'password': 'securepassword123'}
)
token = auth_response.json()['access_token']
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

# Test current upload URL generation
print("1. Testing current upload URL generation...")
upload_response = requests.post(
    'http://localhost:8001/api/v1/uploads/video/upload-url',
    headers=headers,
    json={'filename': 'test_video.mp4', 'duration': 60}
)

if upload_response.status_code == 200:
    upload_data = upload_response.json()
    print(f"✅ Upload URL generation working")
    print(f"   - Upload URL: {upload_data['upload_url']}")
    print(f"   - Method: {upload_data.get('method', 'PUT')}")
    print(f"   - File ID: {upload_data['file_id']}")
    
    # Check if this is direct upload (security issue) or presigned
    if 'presigned' in upload_data['upload_url'].lower() or 'amazonaws.com' in upload_data['upload_url']:
        print("   🔒 SECURE: Using presigned URL pattern")
    else:
        print("   ⚠️  INSECURE: Direct upload to application server detected")
else:
    print(f"❌ Upload URL generation failed: {upload_response.status_code}")
    print(upload_response.text)

# Test current file upload endpoint
print("\n2. Testing current file upload endpoint...")
# This would test the actual file upload, but let's check the endpoint definition first
print("   Checking endpoint security pattern...")

# Let's examine what the current upload endpoint does
import subprocess
result = subprocess.run([
    'curl', '-s', 'http://localhost:8001/docs#/uploads/upload_video_file_video__filename__put'
], capture_output=True, text=True)

if 'Direct file upload to application' in result.stdout:
    print("   ⚠️  INSECURE: Direct file upload detected")
else:
    print("   ✅ Secure pattern (needs verification)")

print("=" * 50)
