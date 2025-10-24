"""
TEST UNIFIED RLS PATTERN - Verify the fix works with real users
"""
import asyncio
from app.database.database import database
from app.crud.live_audio_rooms import live_audio_rooms_crud

async def test_unified_rls_pattern():
    """Test unified RLS pattern with real user"""
    print("🔧 TESTING UNIFIED RLS PATTERN")
    print("=" * 50)
    
    await database.connect()
    
    try:
        # Get a real user from the database
        async with database.pool.acquire() as conn:
            user = await conn.fetchrow("SELECT id, email FROM users LIMIT 1")
            if not user:
                print("❌ No users found in database")
                return False
                
            user_id = user['id']
            print(f"✅ Using real user: {user['email']} ({user_id})")
        
        # Test 1: Create room with unified RLS pattern
        print("1. Testing room creation with unified RLS pattern...")
        try:
            room = await live_audio_rooms_crud.create_room(
                {'title': 'Unified RLS Test Room', 'description': 'Testing unified pattern'},
                user_id
            )
            if room:
                print(f"   ✅ Room created: {room['id']}")
            else:
                print("   ❌ Room creation failed")
                return False
        except Exception as e:
            print(f"   ❌ Room creation error: {e}")
            return False
        
        # Test 2: Test room leaving
        print("2. Testing room leaving...")
        try:
            success = await live_audio_rooms_crud.leave_room(room['id'], user_id)
            if success:
                print("   ✅ Room leaving: SUCCESS")
            else:
                print("   ❌ Room leaving: FAILED")
                return False
        except Exception as e:
            print(f"   ❌ Room leaving error: {e}")
            return False
        
        print("🎉 UNIFIED RLS PATTERN TEST: ALL TESTS PASSED!")
        print("✅ Live audio rooms CRUD now uses session-level RLS context")
        print("✅ Room creation and leaving work correctly")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        if database.pool:
            await database.pool.close()

if __name__ == "__main__":
    success = asyncio.run(test_unified_rls_pattern())
    exit(0 if success else 1)
