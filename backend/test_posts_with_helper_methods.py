import asyncio
import sys
import uuid
sys.path.append('.')
from app.database.database import database

async def test_posts_with_helpers():
    print("🔍 TESTING POSTS WITH DATABASE HELPER METHODS")
    print("=" * 50)
    
    await database.connect()
    try:
        # Get a real user ID
        async with database.pool.acquire() as conn:
            user = await conn.fetchrow("SELECT id FROM users LIMIT 1")
            real_user_id = user['id']
            print(f"Using user ID: {real_user_id}")

        # Test 1: Using database helper methods (should work)
        print("\n1. Testing with database.fetchrow (uses set_current_user_id)...")
        try:
            result = await database.fetchrow(
                """
                INSERT INTO posts (user_id, content, content_type, mood, visibility, is_anonymous,
                                 audio_url, audio_duration, file_size, mime_type)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                RETURNING *
                """,
                real_user_id, 'Test with helper', 'text', 'neutral', 'public', False,
                None, None, None, None,
                user_id=str(real_user_id)  # This triggers set_current_user_id
            )
            print(f"   ✅ SUCCESS: Insert worked with helper - Post ID: {result['id']}")
            # Clean up
            await database.execute("DELETE FROM posts WHERE id = $1", result['id'], user_id=str(real_user_id))
        except Exception as e:
            print(f"   ❌ FAILED with helper: {e}")

        # Test 2: Direct connection without RLS (should fail)
        print("\n2. Testing direct connection (current posts CRUD pattern)...")
        try:
            async with database.pool.acquire() as conn:
                result = await conn.fetchrow(
                    """
                    INSERT INTO posts (user_id, content, content_type, mood, visibility, is_anonymous,
                                     audio_url, audio_duration, file_size, mime_type)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    RETURNING *
                    """,
                    real_user_id, 'Test direct', 'text', 'neutral', 'public', False,
                    None, None, None, None
                )
                print(f"   ❌ UNEXPECTED: Direct insert worked")
                await conn.execute("DELETE FROM posts WHERE id = $1", result['id'])
        except Exception as e:
            print(f"   ✅ EXPECTED: Direct insert failed: {e}")

    except Exception as e:
        print(f"General error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await database.close()

asyncio.run(test_posts_with_helpers())
