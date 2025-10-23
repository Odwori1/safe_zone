"""
Test workaround approaches for the leave room issue
"""
import asyncio
from app.database.database import database

async def test_workaround():
    await database.connect()
    
    test_user_email = "final_test1_13e795af@example.com"
    
    try:
        async with database.pool.acquire() as conn:
            # Get test user
            user = await conn.fetchrow("SELECT id FROM users WHERE email = $1", test_user_email)
            user_id = user['id']
            print(f"User: {user_id}")
            
            # Get a participant record
            participant = await conn.fetchrow("SELECT * FROM live_audio_room_participants WHERE user_id = $1 AND left_at IS NULL LIMIT 1", user_id)
            if not participant:
                print("No active participant found")
                return
                
            print(f"Testing with participant: {participant['id']}")
            print(f"Current left_at: {participant['left_at']}")
            
            # Workaround 1: Try using a CTE (Common Table Expression)
            print("\n1. Testing CTE approach:")
            cte_result = await conn.execute("""
                WITH updated AS (
                    UPDATE live_audio_room_participants 
                    SET left_at = NOW() 
                    WHERE id = $1 
                    RETURNING *
                ) 
                SELECT COUNT(*) FROM updated
            """, participant['id'])
            print(f"   CTE result: {cte_result}")
            
            # Workaround 2: Try using a function call
            print("2. Testing function approach:")
            try:
                # Check if we can call a function that does the update
                func_result = await conn.fetchval("""
                    SELECT update_room_participant_count()
                """)
                print(f"   Function result: {func_result}")
            except Exception as e:
                print(f"   Function approach failed: {e}")
            
            # Check current state
            current = await conn.fetchrow("SELECT * FROM live_audio_room_participants WHERE id = $1", participant['id'])
            print(f"Current state - left_at: {current['left_at']}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await database.close()

asyncio.run(test_workaround())
