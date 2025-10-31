#!/bin/bash

echo "🔍 TESTING LIKE PERSISTENCE"
echo "============================"

# Get token
TOKEN=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "developer_test@example.com",
    "password": "DeveloperPass123!"
  }' | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

echo "1. Getting current posts:"
POSTS_RESPONSE=$(curl -s -X GET "http://localhost:8001/api/v1/posts/?limit=1" \
  -H "Authorization: Bearer $TOKEN")
echo "Posts response sample:"
echo "$POSTS_RESPONSE" | head -c 300
echo "..."

echo ""
echo "2. Check if posts have like info:"
if echo "$POSTS_RESPONSE" | grep -q "user_has_liked"; then
    echo "✅ Posts include user_has_liked field"
else
    echo "❌ Posts missing user_has_liked field"
fi

if echo "$POSTS_RESPONSE" | grep -q "like_count"; then
    echo "✅ Posts include like_count field"
else
    echo "❌ Posts missing like_count field"
fi

echo ""
echo "3. Check database for likes:"
# This would require direct database access to verify likes are stored
echo "   Need to check if likes are actually stored in post_likes table"

echo ""
echo "4. Test like/unlike cycle:"
# Get first post ID
POST_ID=$(echo "$POSTS_RESPONSE" | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)
if [ -n "$POST_ID" ]; then
    echo "   Testing with post: $POST_ID"
    
    echo "   Liking post..."
    LIKE_RESPONSE=$(curl -s -X POST "http://localhost:8001/api/v1/posts/$POST_ID/like" \
      -H "Authorization: Bearer $TOKEN")
    echo "   Like response: $LIKE_RESPONSE"
    
    echo "   Checking post after like..."
    POST_AFTER_LIKE=$(curl -s -X GET "http://localhost:8001/api/v1/posts/$POST_ID" \
      -H "Authorization: Bearer $TOKEN")
    echo "   Post after like:"
    echo "$POST_AFTER_LIKE" | grep -E "(like_count|user_has_liked)" || echo "   No like info in response"
    
else
    echo "   ❌ No posts found to test with"
fi
