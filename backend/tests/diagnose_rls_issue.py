"""
DIAGNOSE RLS ISSUE - Find out exactly why room creation is failing
"""
import asyncio
from app.database.database import database
from app.crud.live_audio_rooms import live_audio_rooms_crud
from uuid import uuid4

async def diagnose_rls_issue():
    """Diagnose the exact RLS issue"""
    print("🔍 DIAGNOSING RLS ISSUE")
    print("=" * 50)
    
    await database.connect()
    
    try:
        # Test 1: Check if we can set RLS context
        async with database.pool.acquire() as conn:
            test_user = str(uuid4())
            print(f"1. Setting RLS context to: {test_user}")
            
            # Use the OLD pattern (like live_audio_rooms uses)
            await conn.execute("SELECT set_config('app.current_user_id', $1, true)", test_user)
            ctx_old = await conn.fetchval("SELECT current_setting('app.current_user_id', true)")
            print(f"   OLD pattern context: {ctx_old}")
            
            # Use the NEW pattern (like enhanced_moderation uses)  
            await conn.execute("SELECT set_config('app.current_user_id', $1, false)", test_user)
            ctx_new = await conn.fetchval("SELECT current_setting('app.current_user_id', true)")
            print(f"   NEW pattern context: {ctx_new}")
        
        # Test 2: Try to manually create a room with proper context
        async with database.pool.acquire() as conn:
            test_user_id = uuid4()
            print(f"2. Testing manual room creation for user: {test_user_id}")
            
            # Use NEW pattern for session-level context
            await conn.execute("SELECT set_config('app.current_user_id', $1, false)", str(test_user_id))
            
            # Try to create room directly
            try:
                room = await conn.fetchrow(
                    """
                    INSERT INTO live_audio_rooms
                    (title, description, created_by, max_participants, room_type)
                    VALUES ($1, $2, $3, $4, $5)
                    RETURNING *
                    """,
                    "Diagnostic Room", "Testing RLS", test_user_id, 10, "support"
                )
                print(f"   ✅ Room created: {room['id']}")
                
                # Try to auto-join as host
                try:
                    await conn.execute(
                        """
                        INSERT INTO live_audio_room_participants (room_id, user_id, role)
                        VALUES ($1, $2, 'host')
                        """,
                        room['id'], test_user_id
                    )
                    print("   ✅ Auto-join as host: SUCCESS")
                except Exception as e:
                    print(f"   ❌ Auto-join failed: {e}")
                    
            except Exception as e:
                print(f"   ❌ Room creation failed: {e}")
                
    except Exception as e:
        print(f"❌ Diagnosis failed: {e}")
    finally:
        if database.pool:
            await database.pool.close()

if __name__ == "__main__":
    asyncio.run(diagnose_rls_issue())
