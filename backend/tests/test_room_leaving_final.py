#!/usr/bin/env python3
"""
FINAL Room Leaving Test with Fixed CRUD
"""
import asyncio
from app.database.database import init_db
from app.crud.live_audio_rooms import live_audio_rooms_crud

async def test_room_leaving_final():
    """Test fixed room leaving functionality"""
    
    print("🔧 FINAL ROOM LEAVING TEST")
    print("=" * 50)
    
    await init_db()
    
    from app.database.database import database
    async with database.pool.acquire() as conn:
        user = await conn.fetchrow("SELECT id, email FROM users LIMIT 1")
        user_id = user['id']
        
        print(f"✅ Using user: {user['email']}")
        
        # Create a room first
        room = await live_audio_rooms_crud.create_room(
            {'title': 'Final Leaving Test Room'}, 
            user_id
        )
        
        print(f"✅ Created room: {room['title']}")
        
        # Verify user is in the room
        participants_before = await live_audio_rooms_crud.get_room_participants(room['id'], user_id)
        print(f"✅ User is participant: {len(participants_before) > 0}")
        print(f"   Participants before: {len(participants_before)}")
        
        # Test leaving
        success = await live_audio_rooms_crud.leave_room(room['id'], user_id)
        print(f"✅ Leave room result: {success}")
        
        # Verify user left
        participants_after = await live_audio_rooms_crud.get_room_participants(room['id'], user_id)
        print(f"✅ User left room: {len(participants_after) == 0}")
        print(f"   Participants after: {len(participants_after)}")
        
        if len(participants_after) == 0:
            print("\n🎉 ROOM LEAVING FIXED SUCCESSFULLY!")
        else:
            print("\n❌ Room leaving still not working properly")

if __name__ == "__main__":
    asyncio.run(test_room_leaving_final())
