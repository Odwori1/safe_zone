import asyncio
import sys
sys.path.append('.')
from app.database.database import database

async def check_existing_data():
    print("📊 CHECKING EXISTING DATABASE DATA")
    print("=" * 50)
    
    await database.connect()
    try:
        async with database.pool.acquire() as conn:
            # Check users
            users = await conn.fetch("SELECT id, username, email FROM users LIMIT 3")
            print(f"Users in database: {len(users)}")
            for user in users:
                print(f"  - {user['username']} ({user['email']}) - ID: {user['id']}")
            
            # Check posts
            posts = await conn.fetch("SELECT COUNT(*) as count FROM posts")
            total_posts = posts[0]['count']
            print(f"\nTotal posts in database: {total_posts}")
            
            if total_posts > 0:
                recent_posts = await conn.fetch("""
                    SELECT p.id, p.content, p.user_id, u.username, p.created_at 
                    FROM posts p 
                    LEFT JOIN users u ON p.user_id = u.id 
                    ORDER BY p.created_at DESC 
                    LIMIT 3
                """)
                print("Recent posts:")
                for post in recent_posts:
                    print(f"  - '{post['content'][:50]}...' by {post['username']} at {post['created_at']}")
                    
            # Check RLS policies for posts
            policies = await conn.fetch("""
                SELECT policyname, cmd, qual 
                FROM pg_policies 
                WHERE tablename = 'posts'
            """)
            print(f"\nPosts RLS policies: {len(policies)}")
            for policy in policies:
                print(f"  - {policy['policyname']}: {policy['cmd']}")
                print(f"    Qual: {policy['qual']}")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await database.close()

asyncio.run(check_existing_data())
