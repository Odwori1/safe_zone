"""
Diagnostic script for leave_room issue
"""
import asyncio
import asyncpg
from uuid import UUID
import os
import sys

# Add the app directory to path so we can import database
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

async def diagnose_leave_room():
    """Test the leave_room UPDATE query directly"""
    
    # Import here after path is set
    from app.database.database import database
    
    # Initialize database connection
    await database.connect()
    
    # Test user and room data (use existing test data)
    test_user_email = "final_test1_13e795af@example.com"
    
    try:
        async with database.pool.acquire() as conn:
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
            
            # Test the exact UPDATE query
            print("🔧 Testing UPDATE query directly...")
            result = await conn.execute("""
                UPDATE live_audio_room_participants
                SET left_at = NOW(), is_active = false
                WHERE room_id = $1 AND user_id = $2 AND left_at IS NULL
            """, room_id, user_id)
            
            print(f"📊 UPDATE result: {repr(result)}")
            print(f"📊 Result type: {type(result)}")
            
            # Check different ways to verify update
            print(f"🔍 'UPDATE 1' in result: {'UPDATE 1' in result}")
            print(f"🔍 'UPDATE 0' in result: {'UPDATE 0' in result}")
            print(f"🔍 'UPDATE' in result: {'UPDATE' in result}")
            
            # Verify if user actually left
            participant = await conn.fetchrow("""
                SELECT * FROM live_audio_room_participants
                WHERE room_id = $1 AND user_id = $2 AND left_at IS NULL
            """, room_id, user_id)
            
            print(f"📋 User still in room: {participant is not None}")
    
    finally:
        await database.disconnect()

if __name__ == "__main__":
    asyncio.run(diagnose_leave_room())
