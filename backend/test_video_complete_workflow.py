import requests
import json
import uuid

print("🎬 COMPREHENSIVE VIDEO WORKFLOW TEST")
print("=" * 50)

# 1. Authentication
auth_response = requests.post(
    'http://localhost:8001/api/v1/auth/login',
    json={'email': 'test_bc64ceba@example.com', 'password': 'securepassword123'}
)
token = auth_response.json()['access_token']
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
print("✅ Authentication successful")

# 2. Generate video upload URL
upload_response = requests.post(
    'http://localhost:8001/api/v1/uploads/video/upload-url',
    headers=headers,
    json={'filename': 'test_video_workflow.mp4', 'duration': 120}
)
print(f"✅ Video upload URL: {upload_response.status_code}")

if upload_response.status_code == 200:
    upload_data = upload_response.json()
    print(f"   - File ID: {upload_data['file_id']}")
    print(f"   - Upload URL: {upload_data['upload_url']}")

# 3. Create a video post (simulating that upload happened)
video_post_data = {
    "content": "Test video post from complete workflow",
    "content_type": "video",
    "mood": "calm", 
    "visibility": "public",
    "is_anonymous": False,
    "video_url": "/uploads/test_video_123.mp4",  # Simulated uploaded file
    "file_size": 10485760,  # 10MB
    "mime_type": "video/mp4"
}

post_response = requests.post(
    'http://localhost:8001/api/v1/posts/',
    headers=headers,
    json=video_post_data
)
print(f"✅ Video post creation: {post_response.status_code}")

if post_response.status_code == 200:
    post_data = post_response.json()
    print(f"   - Post ID: {post_data['id']}")
    print(f"   - Content Type: {post_data['content_type']}")
    print(f"   - Video URL: {post_data.get('video_url', 'None')}")

# 4. Retrieve video posts
video_posts_response = requests.get(
    'http://localhost:8001/api/v1/posts/video',
    headers=headers
)
print(f"✅ Video posts retrieval: {video_posts_response.status_code}")

if video_posts_response.status_code == 200:
    video_posts = video_posts_response.json()
    print(f"   - Found {len(video_posts)} video posts")

# 5. Check if video posts appear in main feed
feed_response = requests.get(
    'http://localhost:8001/api/v1/posts/feed/?content_type=video',
    headers=headers
)
print(f"✅ Video posts in feed: {feed_response.status_code}")

if feed_response.status_code == 200:
    feed_data = feed_response.json()
    video_in_feed = any(post.get('content_type') == 'video' for post in feed_data.get('posts', []))
    print(f"   - Video posts in main feed: {'Yes' if video_in_feed else 'No'}")

print("=" * 50)
print("🎬 VIDEO WORKFLOW TEST COMPLETE")
