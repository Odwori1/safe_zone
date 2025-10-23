#!/usr/bin/env python3
"""
Diagnose Room Leaving Issue
"""
import asyncio
from app.database.database import init_db
from app.crud.live_audio_rooms import live_audio_rooms_crud

async def diagnose_leave_room():
    """Diagnose exactly what's happening with room leaving"""
    
    print("🔍 DIAGNOSING ROOM LEAVING ISSUE")
    print("=" * 50)
    
    await init_db()
    
    from app.database.database import database
    async with database.pool.acquire() as conn:
        user = await conn.fetchrow("SELECT id, email FROM users LIMIT 1")
        user_id = user['id']
        
        print(f"✅ Using user: {user['email']}")
        
        # Create a room first
        room = await live_audio_rooms_crud.create_room(
            {'title': 'Diagnostic Test Room'}, 
            user_id
        )
        
        print(f"✅ Created room: {room['title']} (ID: {room['id']})")
        
        # Check the exact participant record before leaving
        await conn.execute("SELECT set_config('app.current_user_id', $1, true)", str(user_id))
        participant_before = await conn.fetchrow("""
            SELECT id, room_id, user_id, role, left_at, is_active 
            FROM live_audio_room_participants 
            WHERE room_id = $1 AND user_id = $2 AND left_at IS NULL
        """, room['id'], user_id)
        
        print(f"✅ Participant record before leaving:")
        print(f"   ID: {participant_before['id']}")
        print(f"   Role: {participant_before['role']}")
        print(f"   left_at: {participant_before['left_at']}")
        print(f"   is_active: {participant_before['is_active']}")
        
        # Test leaving with detailed debugging
        print("\n🔧 Testing leave_room method...")
        success = await live_audio_rooms_crud.leave_room(room['id'], user_id)
        print(f"   leave_room returned: {success}")
        
        # Check the exact participant record after leaving
        participant_after = await conn.fetchrow("""
            SELECT id, room_id, user_id, role, left_at, is_active 
            FROM live_audio_room_participants 
            WHERE room_id = $1 AND user_id = $2
        """, room['id'], user_id)
        
        print(f"✅ Participant record after leaving:")
        print(f"   ID: {participant_after['id']}")
        print(f"   Role: {participant_after['role']}")
        print(f"   left_at: {participant_after['left_at']}")
        print(f"   is_active: {participant_after['is_active']}")
        
        # Check if the UPDATE actually happened
        if participant_after['left_at'] is not None:
            print("🎉 UPDATE SUCCESSFUL - Participant marked as left!")
        else:
            print("❌ UPDATE FAILED - Participant still active!")
            
        # Let's also check the exact SQL that's being executed
        print("\n🔍 Testing direct SQL execution...")
        result = await conn.execute("""
            UPDATE live_audio_room_participants 
            SET left_at = NOW(), is_active = false
            WHERE room_id = $1 AND user_id = $2 AND left_at IS NULL
            RETURNING id
        """, room['id'], user_id)
        
        print(f"   Direct SQL result: {result}")

if __name__ == "__main__":
    asyncio.run(diagnose_leave_room())
