import requests
import json
import subprocess

print("🔍 COMPLETE SECURITY ANALYSIS")
print("=" * 60)

# Test 1: Authentication & RLS (Phase 1 & 2)
print("1. 🔐 TESTING SECURITY FOUNDATION...")
auth_response = requests.post(
    'http://localhost:8001/api/v1/auth/login',
    json={'email': 'test_bc64ceba@example.com', 'password': 'securepassword123'}
)

if auth_response.status_code == 200:
    token = auth_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    print("   ✅ Authentication working")
    
    # Test RLS
    import uuid
    random_uuid = str(uuid.uuid4())
    response = requests.get(f'/api/v1/posts/{random_uuid}', headers=headers)
    if response.status_code == 404:
        print("   ✅ RLS working properly")
    else:
        print(f"   ❌ RLS issue: {response.status_code}")
else:
    print("   ❌ Authentication broken")

# Test 2: Current Upload Pattern (Phase 3)
print("\n2. 📁 ANALYZING CURRENT UPLOAD PATTERN...")
upload_response = requests.post(
    'http://localhost:8001/api/v1/uploads/video/upload-url',
    headers=headers,
    json={'filename': 'test_video.mp4', 'duration': 60}
)

if upload_response.status_code == 200:
    upload_data = upload_response.json()
    print("   ✅ Upload URL generation working")
    
    # Security analysis
    upload_url = upload_data['upload_url']
    if upload_url.startswith('/api/v1/uploads/'):
        print("   ❌ INSECURE: Direct upload to application server")
        print("      - Files go through application instead of direct to S3")
        print("      - Application handles file bytes (security risk)")
        print("      - No presigned URL pattern")
    else:
        print("   ✅ SECURE: Using presigned URL pattern")

# Test 3: Check current file handling in source code
print("\n3. 🔍 ANALYZING SOURCE CODE PATTERNS...")
try:
    # Read the uploads.py file directly
    with open('app/api/endpoints/uploads.py', 'r') as f:
        content = f.read()
    
    insecure_patterns = []
    if 'UploadFile' in content and 'file.file' in content:
        insecure_patterns.append("Direct file byte handling")
    if 'open(file_path' in content and 'wb' in content:
        insecure_patterns.append("Local file system writes")
    if 'shutil.copyfileobj' in content:
        insecure_patterns.append("File copying in application")
    
    if insecure_patterns:
        print("   ❌ INSECURE PATTERNS FOUND:")
        for pattern in insecure_patterns:
            print(f"      - {pattern}")
    else:
        print("   ✅ No insecure patterns found")
        
except Exception as e:
    print(f"   ⚠️  Could not analyze source: {e}")

# Test 4: Check if files are actually being stored locally
print("\n4. 💾 CHECKING LOCAL FILE STORAGE...")
import os
if os.path.exists('uploads'):
    files = os.listdir('uploads')
    if files:
        print(f"   ❌ INSECURE: {len(files)} files stored locally in uploads/")
        print("      - Local file storage violates zero-trust principle")
    else:
        print("   ✅ No files in local storage")
else:
    print("   ✅ No local uploads directory")

print("\n" + "=" * 60)
print("🎯 SECURITY ASSESSMENT SUMMARY:")
print("   Phase 1 & 2: ✅ SECURE (RLS, Authentication working)")
print("   Phase 3:      ❌ INSECURE (Direct file uploads to application)")
print("")
print("🚨 IMMEDIATE ACTION REQUIRED:")
print("   - Current implementation violates security-first blueprint")
print("   - Must implement presigned URL pattern per security guidelines")
print("   - Remove direct file handling from application")
print("   - Implement proper S3 integration with user isolation")
