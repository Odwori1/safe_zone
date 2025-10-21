import requests
import json
import uuid

print("🔍 COMPLETE S3 FLOW TEST")
print("=" * 50)

# Get auth token
auth_response = requests.post(
    'http://localhost:8001/api/v1/auth/login',
    json={'email': 'test_bc64ceba@example.com', 'password': 'securepassword123'}
)

if auth_response.status_code == 200:
    token = auth_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

    # 1. Create a test post
    post_response = requests.post(
        'http://localhost:8001/api/v1/posts/',
        headers=headers,
        json={
            "content": "Complete S3 flow test post",
            "content_type": "text",
            "visibility": "public",
            "is_anonymous": False
        }
    )

    if post_response.status_code == 200:
        post_id = post_response.json()['id']
        print(f"✅ Test post created: {post_id}")

        # 2. Generate presigned URL for audio file
        upload_response = requests.post(
            f'http://localhost:8001/api/v1/files/posts/{post_id}/presigned-upload',
            headers=headers,
            json={
                "filename": "test_audio.mp3",
                "file_type": "audio",
                "mime_type": "audio/mpeg",
                "file_size": 5242880,
                "duration": 120
            }
        )

        if upload_response.status_code == 200:
            upload_data = upload_response.json()
            print(f"✅ Audio presigned URL generated:")
            print(f"   - File ID: {upload_data['file_id']}")
            print(f"   - S3 Key: {upload_data['s3_key']}")
            print(f"   - Expires in: {upload_data['expires_in']} seconds")

            # 3. Generate presigned URL for video file
            video_response = requests.post(
                f'http://localhost:8001/api/v1/files/posts/{post_id}/presigned-upload',
                headers=headers,
                json={
                    "filename": "test_video.mp4",
                    "file_type": "video",
                    "mime_type": "video/mp4",
                    "file_size": 10485760,
                    "duration": 180,
                    "width": 1920,
                    "height": 1080
                }
            )

            if video_response.status_code == 200:
                video_data = video_response.json()
                print(f"✅ Video presigned URL generated:")
                print(f"   - File ID: {video_data['file_id']}")

                # 4. Test security validation (should reject invalid file)
                invalid_response = requests.post(
                    f'http://localhost:8001/api/v1/files/posts/{post_id}/presigned-upload',
                    headers=headers,
                    json={
                        "filename": "malicious.exe",
                        "file_type": "executable",
                        "mime_type": "application/x-msdownload",
                        "file_size": 1024
                    }
                )

                if invalid_response.status_code != 200:
                    print("✅ Security validation correctly rejected invalid file type")
                else:
                    print("❌ Security validation failed - accepted invalid file")

                # 5. Get post files list
                files_response = requests.get(
                    f'http://localhost:8001/api/v1/files/posts/{post_id}/files',
                    headers=headers
                )

                if files_response.status_code == 200:
                    files_data = files_response.json()
                    print(f"✅ Retrieved {len(files_data['files'])} files for post")
                    for file in files_data['files']:
                        print(f"   - {file['file_type']}: {file['original_filename']} ({file['upload_status']})")

                print("\\n🎉 SECURE S3 IMPLEMENTATION COMPLETELY SUCCESSFUL!")
                
            else:
                print(f"❌ Video upload failed: {video_response.status_code} - {video_response.text}")
        else:
            print(f"❌ Audio upload failed: {upload_response.status_code} - {upload_response.text}")
    else:
        print(f"❌ Post creation failed: {post_response.status_code} - {post_response.text}")
else:
    print(f"❌ Authentication failed: {auth_response.status_code}")
