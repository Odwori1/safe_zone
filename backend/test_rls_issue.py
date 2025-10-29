import asyncio
import asyncpg
from app.core.config import settings
from app.crud.post_audio import post_crud
from uuid import uuid4

async def test_post_creation():
    print("Testing post creation with RLS...")
    
    # Test direct database connection first
    conn = await asyncpg.connect(settings.database_url)
    try:
        # Create a test user
        user_id = uuid4()
        test_email = f"test_{user_id}@example.com"
        
        # Try to create user without RLS context
        try:
            await conn.execute('''
                INSERT INTO users (id, email, username, hashed_password, is_active)
                VALUES ($1, $2, $3, $4, $5)
            ''', user_id, test_email, f"user_{user_id}", "hashed_pass", True)
            print("✅ User created without RLS (expected for users table)")
        except Exception as e:
            print(f"❌ User creation failed: {e}")
            
        # Try to create post without RLS context
        try:
            await conn.execute('''
                INSERT INTO posts (user_id, content, content_type, visibility)
                VALUES ($1, $2, $3, $4)
            ''', user_id, "Test post", "text", "public")
            print("❌ Post created without RLS context - this should have failed!")
        except Exception as e:
            print(f"✅ Post creation correctly blocked by RLS: {e}")
            
        # Now try with RLS context
        try:
            await conn.execute("SELECT set_current_user_id($1)", str(user_id))
            await conn.execute('''
                INSERT INTO posts (user_id, content, content_type, visibility)
                VALUES ($1, $2, $3, $4)
            ''', user_id, "Test post with RLS", "text", "public")
            print("✅ Post created successfully with RLS context")
        except Exception as e:
            print(f"❌ Post creation failed even with RLS: {e}")
            
    finally:
        await conn.close()

asyncio.run(test_post_creation())
