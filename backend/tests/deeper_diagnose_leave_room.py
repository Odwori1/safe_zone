#!/usr/bin/env python3
"""
Deeper Diagnosis of Room Leaving Issue
"""
import asyncio
from app.database.database import init_db

async def deeper_diagnose_leave_room():
    """Deeper diagnosis of the room leaving issue"""
    
    print("🔍 DEEPER DIAGNOSIS OF ROOM LEAVING ISSUE")
    print("=" * 50)
    
    await init_db()
    
    from app.database.database import database
    async with database.pool.acquire() as conn:
        user = await conn.fetchrow("SELECT id, email FROM users LIMIT 1")
        user_id = user['id']
        
        print(f"✅ Using user: {user['email']}")
        
        # Create a room first
        await conn.execute("SELECT set_config('app.current_user_id', $1, true)", str(user_id))
        room = await conn.fetchrow("""
            INSERT INTO live_audio_rooms (title, created_by) 
            VALUES ($1, $2) RETURNING id, title
        """, 'Deep Diagnostic Room', user_id)
        
        print(f"✅ Created room: {room['title']} (ID: {room['id']})")
        
        # Join as participant
        participant = await conn.fetchrow("""
            INSERT INTO live_audio_room_participants (room_id, user_id, role)
            VALUES ($1, $2, 'host') RETURNING id
        """, room['id'], user_id)
        print(f"✅ Joined as participant: {participant['id']}")
        
        # Check EXACT state before UPDATE
        print("\n🔍 EXACT STATE BEFORE UPDATE:")
        exact_state = await conn.fetchrow("""
            SELECT id, room_id, user_id, role, left_at, is_active,
                   room_id = $1 as room_match,
                   user_id = $2 as user_match, 
                   left_at IS NULL as left_at_null
            FROM live_audio_room_participants 
            WHERE id = $3
        """, room['id'], user_id, participant['id'])
        
        for key, value in exact_state.items():
            print(f"   {key}: {value}")
        
        # Test the exact WHERE clause conditions
        print("\n🔍 TESTING WHERE CLAUSE CONDITIONS:")
        conditions = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total_records,
                COUNT(CASE WHEN room_id = $1 THEN 1 END) as room_matches,
                COUNT(CASE WHEN user_id = $2 THEN 1 END) as user_matches,
                COUNT(CASE WHEN left_at IS NULL THEN 1 END) as left_at_null,
                COUNT(CASE WHEN room_id = $1 AND user_id = $2 AND left_at IS NULL THEN 1 END) as all_conditions_match
            FROM live_audio_room_participants 
            WHERE id = $3
        """, room['id'], user_id, participant['id'])
        
        for key, value in conditions.items():
            print(f"   {key}: {value}")
        
        # Try the UPDATE with RETURNING to see what happens
        print("\n🔧 TESTING UPDATE WITH RETURNING:")
        update_result = await conn.fetch("""
            UPDATE live_audio_room_participants 
            SET left_at = NOW()
            WHERE room_id = $1 AND user_id = $2 AND left_at IS NULL
            RETURNING id, left_at
        """, room['id'], user_id)
        
        print(f"   UPDATE returned {len(update_result)} rows")
        if update_result:
            for row in update_result:
                print(f"   Updated: ID={row['id']}, left_at={row['left_at']}")
        else:
            print("   ❌ No rows updated!")
            
        # Check if there's a trigger interfering
        print("\n🔍 CHECKING FOR TRIGGERS:")
        triggers = await conn.fetch("""
            SELECT trigger_name, event_manipulation, action_statement
            FROM information_schema.triggers 
            WHERE event_object_table = 'live_audio_room_participants'
        """)
        
        if triggers:
            for trigger in triggers:
                print(f"   Trigger: {trigger['trigger_name']} on {trigger['event_manipulation']}")
                print(f"   Action: {trigger['action_statement'][:100]}...")
        else:
            print("   No triggers found")

if __name__ == "__main__":
    asyncio.run(deeper_diagnose_leave_room())
