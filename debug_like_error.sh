#!/bin/bash

echo "🔍 DEBUGGING LIKE ERROR"
echo "======================"

# Get token
TOKEN=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "developer_test@example.com",
    "password": "DeveloperPass123!"
  }' | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

echo "Token: ${TOKEN:0:20}..."

# Get first post ID
POST_ID=$(curl -s -X GET "http://localhost:8001/api/v1/posts/?limit=1" \
  -H "Authorization: Bearer $TOKEN" | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)

echo "Testing with post: $POST_ID"

echo ""
echo "1. Checking post before like:"
curl -s -X GET "http://localhost:8001/api/v1/posts/$POST_ID" \
  -H "Authorization: Bearer $TOKEN" | grep -E "(like_count|user_has_liked)"

echo ""
echo "2. Testing like endpoint with verbose output:"
curl -v -X POST "http://localhost:8001/api/v1/posts/$POST_ID/like" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  2>&1 | grep -E "(HTTP|< detail|Error|error)"

echo ""
echo "3. Checking if user has already liked this post:"
# Let's check the database directly if possible
echo "   Need to check post_likes table for existing likes"

echo ""
echo "4. Testing with a different post (create a new one):"
NEW_POST_RESPONSE=$(curl -s -X POST "http://localhost:8001/api/v1/posts/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Test post for like debugging",
    "mood": "calm",
    "visibility": "public"
  }')
NEW_POST_ID=$(echo "$NEW_POST_RESPONSE" | grep -o '"id":"[^"]*' | cut -d'"' -f4)
echo "   Created new post: $NEW_POST_ID"

echo ""
echo "5. Testing like on new post:"
curl -X POST "http://localhost:8001/api/v1/posts/$NEW_POST_ID/like" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"

echo ""
echo "6. Checking new post after like attempt:"
curl -s -X GET "http://localhost:8001/api/v1/posts/$NEW_POST_ID" \
  -H "Authorization: Bearer $TOKEN" | grep -E "(like_count|user_has_liked)"
