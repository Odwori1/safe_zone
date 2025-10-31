#!/bin/bash

echo "🎯 TESTING LIKE PERSISTENCE AFTER REFRESH"
echo "========================================="

# Get token
TOKEN=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "developer_test@example.com",
    "password": "DeveloperPass123!"
  }' | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

echo "1. Create a new test post:"
NEW_POST=$(curl -s -X POST "http://localhost:8001/api/v1/posts/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Like persistence test post",
    "mood": "happy", 
    "visibility": "public"
  }')
POST_ID=$(echo "$NEW_POST" | grep -o '"id":"[^"]*' | cut -d'"' -f4)
echo "   Created post: $POST_ID"

echo ""
echo "2. Check post BEFORE like:"
BEFORE_LIKE=$(curl -s -X GET "http://localhost:8001/api/v1/posts/$POST_ID" \
  -H "Authorization: Bearer $TOKEN")
echo "   like_count: $(echo "$BEFORE_LIKE" | grep -o '"like_count":[0-9]*' | cut -d: -f2)"
echo "   user_has_liked: $(echo "$BEFORE_LIKE" | grep -o '"user_has_liked":\(true\|false\)' | cut -d: -f2)"

echo ""
echo "3. Like the post:"
LIKE_RESPONSE=$(curl -s -X POST "http://localhost:8001/api/v1/posts/$POST_ID/like" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")
echo "   Like response: $LIKE_RESPONSE"

echo ""
echo "4. Check post IMMEDIATELY after like:"
AFTER_LIKE=$(curl -s -X GET "http://localhost:8001/api/v1/posts/$POST_ID" \
  -H "Authorization: Bearer $TOKEN")
echo "   like_count: $(echo "$AFTER_LIKE" | grep -o '"like_count":[0-9]*' | cut -d: -f2)"
echo "   user_has_liked: $(echo "$AFTER_LIKE" | grep -o '"user_has_liked":\(true\|false\)' | cut -d: -f2)"

echo ""
echo "5. Check database directly for the like:"
python3 << PYTHON_EOF
import asyncpg
import asyncio
import os

async def check_like():
    try:
        conn = await asyncpg.connect(
            host='localhost',
            port=5433,
            database='safe_zone',
            user='safe_zone_app_user', 
            password='secure_app_password_2024'
        )
        
        # Get the post ID from the shell variable
        post_id = "$POST_ID"
        user_id = "8808956b-11fb-4253-91ef-98b9902ffbc8"
        
        if post_id and post_id != "":
            # Check if like exists in database
            like_exists = await conn.fetchval(
                "SELECT 1 FROM post_likes WHERE post_id = \$1 AND user_id = \$2",
                post_id, user_id
            )
            print(f"   Database: Like exists = {like_exists is not None}")
            
            # Count total likes for this post
            like_count = await conn.fetchval(
                "SELECT COUNT(*) FROM post_likes WHERE post_id = \$1",
                post_id
            )
            print(f"   Database: Total likes = {like_count}")
        else:
            print("   No POST_ID available for database check")
        
        await conn.close()
    except Exception as e:
        print(f"   Database error: {e}")

asyncio.run(check_like())
PYTHON_EOF

echo ""
echo "6. Simulate page refresh - get posts feed and find our test post:"
FEED_RESPONSE=$(curl -s -X GET "http://localhost:8001/api/v1/posts/?limit=20" \
  -H "Authorization: Bearer $TOKEN")

# Use a Python script to properly parse JSON and find our test post
python3 << PYTHON_EOF
import json
import sys

feed_response = """$FEED_RESPONSE"""
post_id = "$POST_ID"

try:
    posts = json.loads(feed_response)
    if isinstance(posts, list):
        for post in posts:
            if post.get('id') == post_id:
                like_count = post.get('like_count', 0)
                user_has_liked = post.get('user_has_liked', False)
                print(f"   like_count: {like_count}")
                print(f"   user_has_liked: {user_has_liked}")
                break
        else:
            print("   Test post not found in feed")
    else:
        print("   Invalid feed response format")
except Exception as e:
    print(f"   Error parsing feed: {e}")
PYTHON_EOF
