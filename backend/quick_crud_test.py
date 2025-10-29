import asyncio
import sys
import uuid
sys.path.append('.')
from app.database.database import database
from app.crud.post_audio import post_crud

async def quick_test():
    print("🔍 QUICK CRUD TEST")
    print("=" * 30)
    
    await database.connect()
    try:
        # Get a real user ID
        async with database.pool.acquire() as conn:
            user = await conn.fetchrow("SELECT id FROM users LIMIT 1")
            real_user_id = user['id']
            print(f"Using user ID: {real_user_id}")

        # Test create with proper parameters
        post_data = type('PostIn', (), {
            'content': 'Quick test post',
            'content_type': 'text',
            'mood': 'neutral',
            'visibility': 'public',
            'is_anonymous': False,
            'audio_url': None,
            'audio_duration': None,
            'file_size': None,
            'mime_type': None
        })()
        
        result = await post_crud.create(real_user_id, post_data, real_user_id)
        print(f"✅ Create: SUCCESS - Post ID: {result['id']}")
        
        # Test get
        retrieved = await post_crud.get(result['id'], real_user_id)
        print(f"✅ Get: SUCCESS - Content: '{retrieved['content']}'")
        
        # Clean up
        await post_crud.delete(result['id'], real_user_id, real_user_id)
        print("✅ Cleanup: SUCCESS")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await database.close()

asyncio.run(quick_test())
