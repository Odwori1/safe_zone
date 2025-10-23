"""
Check for missing RLS policies that are causing the UPDATE to fail
"""
import asyncio
from app.database.database import database

async def test_missing_policies():
    await database.connect()
    
    try:
        async with database.pool.acquire() as conn:
            print("=== INVESTIGATING MISSING RLS POLICIES ===\n")
            
            # Check what policies exist vs what should exist
            print("EXISTING POLICIES FOR live_audio_room_participants:")
            existing_policies = await conn.fetch("""
                SELECT policyname, cmd, qual, with_check
                FROM pg_policies 
                WHERE tablename = 'live_audio_room_participants'
            """)
            
            for policy in existing_policies:
                print(f"  {policy['policyname']} - {policy['cmd']}")
                if policy['qual']:
                    print(f"    Qual: {policy['qual']}")
                if policy['with_check']:
                    print(f"    With Check: {policy['with_check']}")
            
            # According to fix_live_audio_rls_final.sql, we should have these policies:
            expected_policies = [
                ('live_audio_room_participants_select_policy', 'SELECT'),
                ('live_audio_room_participants_insert_policy', 'INSERT'), 
                ('live_audio_room_participants_update_policy', 'UPDATE')
            ]
            
            print(f"\nMISSING POLICIES:")
            existing_policy_names = [p['policyname'] for p in existing_policies]
            for expected_name, expected_cmd in expected_policies:
                if expected_name not in existing_policy_names:
                    print(f"  ❌ {expected_name} ({expected_cmd})")
                else:
                    print(f"  ✅ {expected_name} ({expected_cmd})")
            
            # Test if we can identify why UPDATE is blocked
            print(f"\n=== TESTING POLICY ENFORCEMENT ===\n")
            
            test_user_email = "final_test1_13e795af@example.com"
            user = await conn.fetchrow("SELECT id FROM users WHERE email = $1", test_user_email)
            user_id = user['id']
            
            # Get a participant record
            participant = await conn.fetchrow("SELECT * FROM live_audio_room_participants WHERE user_id = $1 LIMIT 1", user_id)
            
            # Test with RLS context
            await conn.execute("SELECT set_config('app.current_user_id', $1, true)", str(user_id))
            
            print(f"Testing UPDATE with user context {user_id} on participant {participant['id']}:")
            
            # The issue might be that without an UPDATE policy, RLS blocks all updates
            result = await conn.execute("UPDATE live_audio_room_participants SET left_at = NOW() WHERE id = $1", participant['id'])
            print(f"UPDATE result: {result}")
            
            # Let's check if SELECT works (it should, since we have SELECT policy)
            select_result = await conn.fetchrow("SELECT * FROM live_audio_room_participants WHERE id = $1", participant['id'])
            print(f"SELECT works: {select_result is not None}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await database.close()

asyncio.run(test_missing_policies())
