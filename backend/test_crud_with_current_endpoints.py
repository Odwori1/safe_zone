import asyncio
import sys
import uuid
sys.path.append('.')
from app.database.database import database
from app.crud.post_audio import post_crud

async def test_missing_parameter_issue():
    print("🔍 TESTING MISSING PARAMETER ISSUE")
    print("=" * 50)
    
    await database.connect()
    try:
        # Get a real user ID
        async with database.pool.acquire() as conn:
            user = await conn.fetchrow("SELECT id FROM users LIMIT 1")
            real_user_id = user['id']
            print(f"Using user ID: {real_user_id}")

        # Test 1: Try calling methods with current endpoint parameters (missing requesting_user_id)
        print("\n1. Testing with current endpoint parameters (missing requesting_user_id)...")
        try:
            post_data = type('PostIn', (), {
                'content': 'Test missing parameter',
                'content_type': 'text',
                'mood': 'neutral',
                'visibility': 'public',
                'is_anonymous': False,
                'audio_url': None,
                'audio_duration': None,
                'file_size': None,
                'mime_type': None
            })()
            
            # This is what current endpoints do - missing requesting_user_id
            result = await post_crud.create(real_user_id, post_data)  # Missing 3rd parameter!
            print(f"   ❌ UNEXPECTED: Worked without requesting_user_id")
        except TypeError as e:
            print(f"   ✅ EXPECTED: Failed with missing parameter: {e}")
        except Exception as e:
            print(f"   ❌ UNEXPECTED ERROR: {e}")

        # Test 2: Try get_feed with current parameters
        print("\n2. Testing get_feed with current parameters...")
        try:
            result = await post_crud.get_feed(real_user_id, 10, 0)  # Missing requesting_user_id
            print(f"   ❌ UNEXPECTED: get_feed worked without requesting_user_id")
        except TypeError as e:
            print(f"   ✅ EXPECTED: get_feed failed with missing parameter: {e}")
        except Exception as e:
            print(f"   ❌ UNEXPECTED ERROR: {e}")

        # Test 3: Try get with current parameters  
        print("\n3. Testing get with current parameters...")
        try:
            # Create a test post first to get an ID
            async with database.pool.acquire() as conn:
                await conn.execute("SELECT set_config('app.current_user_id', $1, false)", str(real_user_id))
                test_post = await conn.fetchrow(
                    "INSERT INTO posts (user_id, content) VALUES ($1, $2) RETURNING id",
                    real_user_id, "Test post for get"
                )
                post_id = test_post['id']
            
            result = await post_crud.get(post_id)  # Missing requesting_user_id
            print(f"   ❌ UNEXPECTED: get worked without requesting_user_id")
            
            # Clean up
            async with database.pool.acquire() as conn:
                await conn.execute("SELECT set_config('app.current_user_id', $1, false)", str(real_user_id))
                await conn.execute("DELETE FROM posts WHERE id = $1", post_id)
        except TypeError as e:
            print(f"   ✅ EXPECTED: get failed with missing parameter: {e}")
        except Exception as e:
            print(f"   ❌ UNEXPECTED ERROR: {e}")
            
    except Exception as e:
        print(f"General error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await database.close()

asyncio.run(test_missing_parameter_issue())
