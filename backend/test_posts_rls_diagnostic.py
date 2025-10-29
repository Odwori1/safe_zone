import asyncio
import sys
import uuid
sys.path.append('.')
from app.database.database import database
from app.crud.post_audio import post_crud

async def diagnose_posts_rls():
    print("🔍 POSTS RLS DIAGNOSTIC TEST")
    print("=" * 50)
    
    await database.connect()
    try:
        test_user_id = uuid.uuid4()
        print(f"Test User ID: {test_user_id}")
        
        # Test 1: Check if we can access posts table directly
        print("\n1. Testing direct database access...")
        async with database.pool.acquire() as conn:
            try:
                # Set RLS context manually
                await conn.execute("SELECT set_config('app.current_user_id', $1, false)", str(test_user_id))
                posts = await conn.fetch("SELECT * FROM posts LIMIT 1")
                print("   ✅ Direct access with RLS context: SUCCESS")
            except Exception as e:
                print(f"   ❌ Direct access error: {e}")
        
        # Test 2: Test posts creation via CRUD (should fail due to missing RLS)
        print("\n2. Testing posts creation via CRUD...")
        try:
            post_data = type('PostIn', (), {
                'content': 'Test post content',
                'content_type': 'text',
                'mood': 'neutral', 
                'visibility': 'public',
                'is_anonymous': False,
                'audio_url': None,
                'audio_duration': None,
                'file_size': None,
                'mime_type': None
            })()
            
            result = await post_crud.create(test_user_id, post_data)
            print("   ✅ Posts creation via CRUD: SUCCESS")
        except Exception as e:
            print(f"   ❌ Posts creation error: {e}")
            
        # Test 3: Test with manual RLS context in CRUD pattern
        print("\n3. Testing manual RLS context pattern...")
        async with database.pool.acquire() as conn:
            try:
                await conn.execute("SELECT set_config('app.current_user_id', $1, false)", str(test_user_id))
                result = await conn.fetchrow(
                    """
                    INSERT INTO posts (user_id, content, content_type, mood, visibility, is_anonymous,
                                     audio_url, audio_duration, file_size, mime_type)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    RETURNING *
                    """,
                    test_user_id, 'Manual test content', 'text', 'neutral', 'public', False,
                    None, None, None, None
                )
                print("   ✅ Manual RLS context: SUCCESS")
            except Exception as e:
                print(f"   ❌ Manual RLS context error: {e}")
                
    except Exception as e:
        print(f"General error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await database.close()
    print("\n" + "=" * 50)

asyncio.run(diagnose_posts_rls())
