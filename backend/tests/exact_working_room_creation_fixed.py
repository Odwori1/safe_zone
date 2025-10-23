#!/usr/bin/env python3
"""
EXACT WORKING ROOM CREATION - UPDATED FOR NEW TABLES
"""
import asyncio
import uuid
from app.database.database import database, init_db

async def exact_working_room_creation():
    """EXACT CODE THAT WORKS - Updated for new tables"""
    
    print("🎯 EXACT WORKING ROOM CREATION - UPDATED")
    print("=" * 60)
    
    # 1. INITIALIZE DATABASE (CRITICAL STEP)
    await init_db()
    
    # 2. ACQUIRE CONNECTION
    conn = await database.pool.acquire()
    
    try:
        # 3. CREATE A REAL USER FIRST (or use existing)
        # Get existing user or create test user
        existing_user = await conn.fetchrow("SELECT id FROM users LIMIT 1;")
        if existing_user:
            user_id = existing_user['id']
            print(f"✅ Using existing user: {user_id}")
        else:
            # Create test user if none exist
            user_id = uuid.uuid4()
            await conn.execute("""
                INSERT INTO users (id, email, username, hashed_password, full_name, is_active)
                VALUES ($1, $2, $3, $4, $5, true)
            """, user_id, f"test_{uuid.uuid4().hex[:8]}@example.com", f"user_{uuid.uuid4().hex[:8]}", 
                "fake_hash", "Test User")
            print(f"✅ Created test user: {user_id}")
        
        # 4. SET RLS CONTEXT (EXACTLY LIKE THIS)
        await conn.execute("SELECT set_config('app.current_user_id', $1, true);", str(user_id))
        
        # 5. VERIFY CONTEXT IS SET
        current_context = await conn.fetchval("SELECT current_setting('app.current_user_id', true);")
        print(f"✅ RLS Context set to: {current_context}")
        
        # 6. CREATE ROOM (THIS SHOULD WORK NOW)
        print("Creating live audio room...")
        room = await conn.fetchrow("""
            INSERT INTO live_audio_rooms (
                title, description, created_by, 
                visibility, max_participants, room_type
            ) VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id, title, created_by, visibility
        """, "Security Test Room", "Test description", 
            user_id, "public", 50, "support")
        
        if room:
            print(f"✅ ROOM CREATION SUCCESS!")
            print(f"   Room ID: {room['id']}")
            print(f"   Title: {room['title']}")
            print(f"   Created by: {room['created_by']}")
            
            # 7. AUTO-JOIN CREATOR AS PARTICIPANT
            await conn.execute("""
                INSERT INTO live_audio_room_participants (
                    room_id, user_id, role
                ) VALUES ($1, $2, 'host')
            """, room['id'], user_id)
            print("✅ Creator auto-joined as host")
            
            # 8. VERIFY ROOM IS VISIBLE
            visible_rooms = await conn.fetch("SELECT id, title FROM live_audio_rooms;")
            print(f"✅ User can see {len(visible_rooms)} rooms")
            
            # 9. VERIFY PARTICIPANT IS VISIBLE
            participants = await conn.fetch("""
                SELECT p.user_id, p.role 
                FROM live_audio_room_participants p
                WHERE p.room_id = $1
            """, room['id'])
            print(f"✅ Room has {len(participants)} participants")
            
            print("\n🎉 LIVE AUDIO ROOMS WORKING PERFECTLY!")
            
        else:
            print("❌ Room creation failed")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # 10. CLEANUP
        await database.pool.release(conn)

if __name__ == "__main__":
    asyncio.run(exact_working_room_creation())
