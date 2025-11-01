import asyncio
import asyncpg
import os
from dotenv import load_dotenv
from uuid import UUID

load_dotenv()

async def debug_saved_posts():
    db_host = os.getenv("DB_HOST", "127.0.0.1")
    db_port = int(os.getenv("DB_PORT", "5433"))
    db_name = os.getenv("DB_NAME", "safe_zone")
    db_user = os.getenv("DB_USER", "safe_zone_app_user")
    db_password = os.getenv("DB_PASSWORD", "secure_app_password_2024")
    
    user_id = UUID("8808956b-11fb-4253-91ef-98b9902ffbc8")
    
    conn = await asyncpg.connect(
        host=db_host, port=db_port, database=db_name, 
        user=db_user, password=db_password
    )
    
    print("🔍 DEBUGGING SAVED POSTS ISSUE")
    print("=" * 50)
    
    # 1. Check if saved_posts table has data
    print("\n1. Checking saved_posts table...")
    saved_posts = await conn.fetch("""
        SELECT * FROM saved_posts WHERE user_id = $1
    """, user_id)
    
    print(f"   Found {len(saved_posts)} saved posts in database")
    for sp in saved_posts:
        print(f"   - Post ID: {sp['post_id']}, Saved at: {sp['saved_at']}")
    
    # 2. Check if the posts exist and are accessible
    if saved_posts:
        post_id = saved_posts[0]['post_id']
        print(f"\n2. Checking post {post_id}...")
        
        post = await conn.fetchrow("""
            SELECT * FROM posts WHERE id = $1
        """, post_id)
        
        if post:
            print(f"   ✅ Post exists: {post['content'][:50]}...")
            print(f"   📊 Post status: {post['status']}, moderation: {post['moderation_status']}")
        else:
            print("   ❌ Post not found!")
    
    # 3. Test the actual query from get_saved_posts
    print(f"\n3. Testing get_saved_posts query...")
    await conn.execute("SELECT set_current_user_id($1);", str(user_id))
    
    test_posts = await conn.fetch("""
        SELECT 
            p.*,
            u.username as username,
            u.profile_picture as user_avatar,
            (SELECT COUNT(*) FROM post_likes WHERE post_id = p.id) as like_count,
            EXISTS(
                SELECT 1 FROM post_likes 
                WHERE post_id = p.id AND user_id = $1
            ) as user_has_liked,
            (SELECT COUNT(*) FROM post_shares WHERE post_id = p.id) as share_count,
            EXISTS(
                SELECT 1 FROM post_shares 
                WHERE post_id = p.id AND user_id = $1
            ) as user_has_shared,
            sp.saved_at as saved_at
        FROM saved_posts sp
        JOIN posts p ON sp.post_id = p.id
        LEFT JOIN users u ON p.user_id = u.id
        WHERE sp.user_id = $1
        AND p.status = 'active'
        AND p.moderation_status = 'approved'
        ORDER BY sp.saved_at DESC
        LIMIT 10
    """, user_id)
    
    print(f"   Query returned {len(test_posts)} posts")
    for post in test_posts:
        print(f"   - Post: {post['content'][:30]}..., Status: {post['status']}, Moderation: {post['moderation_status']}")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(debug_saved_posts())
