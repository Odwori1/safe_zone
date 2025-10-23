"""
Simple diagnostic for leave_room issue
"""
import asyncio
from app.database.database import get_database

async def test_leave_room():
    db = get_database()
    await db.connect()
    
    test_user_email = "final_test1_13e795af@example.com"
    
    try:
        async with db.pool.acquire() as conn:
            # Get test user
            user = await conn.fetchrow("SELECT id FROM users WHERE email = $1", test_user_email)
            if not user:
                print("❌ Test user not found")
                return
                
            user_id = user['id']
            print(f"✅ Testing with user: {user_id}")
            
            # Get a room this user is in
            room = await conn.fetchrow("""
                SELECT room_id FROM live_audio_room_participants 
                WHERE user_id = $1 AND left_at IS NULL 
                LIMIT 1
            """, user_id)
            
            if not room:
                print("❌ User not in any room")
                return
                
            room_id = room['room_id']
            print(f"✅ Testing with room: {room_id}")
            
            # Set RLS context
            await conn.execute("SELECT set_config('app.current_user_id', $1, true)", str(user_id))
            
            # Check current state
            before = await conn.fetchrow("""
                SELECT * FROM live_audio_room_participants
                WHERE room_id = $1 AND user_id = $2
            """, room_id, user_id)
            print(f"📋 Before - left_at: {before['left_at']}, is_active: {before['is_active']}")
            
            # Test the UPDATE
            result = await conn.execute("""
                UPDATE live_audio_room_participants
                SET left_at = NOW(), is_active = false
                WHERE room_id = $1 AND user_id = $2 AND left_at IS NULL
            """, room_id, user_id)
            
            print(f"📊 UPDATE result: {repr(result)}")
            
            # Check after state
            after = await conn.fetchrow("""
                SELECT * FROM live_audio_room_participants
                WHERE room_id = $1 AND user_id = $2
            """, room_id, user_id)
            print(f"📋 After - left_at: {after['left_at']}, is_active: {after['is_active']}")
            
    finally:
        if hasattr(db, 'pool'):
            pass  # Connection cleanup handled by context

if __name__ == "__main__":
    asyncio.run(test_leave_room())
