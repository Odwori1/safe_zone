#!/usr/bin/env python3
"""
Test Room Leaving Fix
"""
import asyncio
from app.database.database import init_db
from app.crud.live_audio_rooms import live_audio_rooms_crud

async def test_room_leaving():
    """Test room leaving functionality"""
    
    print("🔧 TESTING ROOM LEAVING FIX")
    print("=" * 50)
    
    await init_db()
    
    from app.database.database import database
    async with database.pool.acquire() as conn:
        user = await conn.fetchrow("SELECT id, email FROM users LIMIT 1")
        user_id = user['id']
        
        # Create a room first
        room = await live_audio_rooms_crud.create_room(
            {'title': 'Leaving Test Room'}, 
            user_id
        )
        
        print(f"✅ Created room: {room['title']}")
        
        # Verify user is in the room
        participants = await live_audio_rooms_crud.get_room_participants(room['id'], user_id)
        print(f"✅ User is participant: {len(participants) > 0}")
        
        # Test leaving
        success = await live_audio_rooms_crud.leave_room(room['id'], user_id)
        print(f"✅ Leave room result: {success}")
        
        # Verify user left
        participants_after = await live_audio_rooms_crud.get_room_participants(room['id'], user_id)
        print(f"✅ User left room: {len(participants_after) == 0}")

if __name__ == "__main__":
    asyncio.run(test_room_leaving())
