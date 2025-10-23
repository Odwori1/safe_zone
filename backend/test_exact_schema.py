"""
Check the exact schema of the problematic tables and compare with working tables
"""
import asyncio
from app.database.database import database

async def test_exact_schema():
    await database.connect()
    
    try:
        async with database.pool.acquire() as conn:
            print("=== COMPARING TABLE SCHEMAS ===\n")
            
            # Check live_audio_rooms schema
            print("live_audio_rooms COLUMNS:")
            rooms_cols = await conn.fetch("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'live_audio_rooms'
                ORDER BY ordinal_position
            """)
            for col in rooms_cols:
                print(f"  {col['column_name']} - {col['data_type']} - nullable: {col['is_nullable']}")
            
            print("\nlive_audio_room_participants COLUMNS:")
            participants_cols = await conn.fetch("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'live_audio_room_participants'
                ORDER BY ordinal_position
            """)
            for col in participants_cols:
                print(f"  {col['column_name']} - {col['data_type']} - nullable: {col['is_nullable']}")
            
            # Check if there are any missing columns from the original schema
            print("\n=== CHECKING FOR MISSING COLUMNS ===\n")
            
            # From create_live_audio_rooms.sql, we expect these columns for live_audio_rooms:
            expected_rooms_columns = ['visibility', 'is_public', 'is_active', 'max_participants', 'current_participants', 'room_type']
            existing_rooms_columns = [col['column_name'] for col in rooms_cols]
            
            print("Missing columns in live_audio_rooms:")
            for expected in expected_rooms_columns:
                if expected not in existing_rooms_columns:
                    print(f"  ❌ {expected}")
                else:
                    print(f"  ✅ {expected}")
                    
            # Check RLS policies
            print("\n=== CHECKING RLS POLICIES ===\n")
            rls_policies = await conn.fetch("""
                SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check
                FROM pg_policies 
                WHERE tablename IN ('live_audio_rooms', 'live_audio_room_participants')
            """)
            
            print("RLS POLICIES:")
            for policy in rls_policies:
                print(f"  {policy['tablename']}.{policy['policyname']}")
                print(f"    Command: {policy['cmd']}")
                print(f"    Qual: {policy['qual']}")
                print(f"    With Check: {policy['with_check']}")
                print()
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await database.close()

asyncio.run(test_exact_schema())
