#!/bin/bash

echo "🔍 COMPARING POSTS - SUCCESS VS FAILURE"
echo "========================================"

# Get token
TOKEN=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "developer_test@example.com",
    "password": "DeveloperPass123!"
  }' | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

# Post that FAILED to like
FAILED_POST="14120232-38b6-4b0a-bb2d-573ee35abfbf"
echo "1. POST THAT FAILED ($FAILED_POST):"
curl -s -X GET "http://localhost:8001/api/v1/posts/$FAILED_POST" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

echo ""
# Post that SUCCEEDED to like  
SUCCESS_POST="984c6b7c-eeae-4c00-b26b-752e9a828d32"
echo "2. POST THAT SUCCEEDED ($SUCCESS_POST):"
curl -s -X GET "http://localhost:8001/api/v1/posts/$SUCCESS_POST" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

echo ""
echo "3. CHECKING IF USER ALREADY LIKED FAILED POST:"
# Check if user already liked the failed post (this might be the issue)
curl -s -X GET "http://localhost:8001/api/v1/posts/$FAILED_POST" \
  -H "Authorization: Bearer $TOKEN" | grep -E "(user_has_liked|like_count)"

echo ""
echo "4. CHECKING DATABASE FOR SPECIFIC POST LIKES:"
# Let's check if there are existing likes for the failed post
python3 << 'PYTHON_EOF'
import asyncpg
import asyncio

async def check_specific_likes():
    try:
        conn = await asyncpg.connect(
            host='localhost',
            port=5433,
            database='safe_zone', 
            user='safe_zone_app_user',
            password='secure_app_password_2024'
        )
        
        failed_post = "14120232-38b6-4b0a-bb2d-573ee35abfbf"
        user_id = "8808956b-11fb-4253-91ef-98b9902ffbc8"  # From your test user
        
        # Check if user already liked the failed post
        existing_like = await conn.fetchval(
            "SELECT 1 FROM post_likes WHERE post_id = $1 AND user_id = $2",
            failed_post, user_id
        )
        
        if existing_like:
            print(f"❌ User HAS ALREADY LIKED post {failed_post}")
        else:
            print(f"✅ User has NOT liked post {failed_post}")
            
        # Count likes for failed post
        like_count = await conn.fetchval(
            "SELECT COUNT(*) FROM post_likes WHERE post_id = $1",
            failed_post
        )
        print(f"📊 Total likes for failed post: {like_count}")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

asyncio.run(check_specific_likes())
PYTHON_EOF
