"""
TEST EXACT WORKING PATTERN from live_audio_rooms.py
"""
import asyncio
from app.database.database import database
from uuid import uuid4

async def test_exact_working_pattern():
    """Test the exact pattern used in working code"""
    print("🔍 TESTING EXACT WORKING PATTERN")
    print("=" * 50)
    
    await database.connect()
    
    try:
        # Use the EXACT same pattern as live_audio_rooms.py
        async with database.pool.acquire() as conn:
            # Pattern from live_audio_rooms.py - using UUID object converted to string
            test_user_id = uuid4()
            print(f"1. Testing with UUID object: {test_user_id}")
            
            # EXACT pattern from working code
            await conn.execute("SELECT set_config('app.current_user_id', $1, true)", str(test_user_id))
            
            # Check context
            current_context = await conn.fetchval("SELECT current_setting('app.current_user_id', true)")
            print(f"2. Current context: {current_context}")
            
            if str(test_user_id) == current_context:
                print("✅ UUID PATTERN WORKS!")
                return True
            else:
                print(f"❌ UUID pattern failed: expected {test_user_id}, got {current_context}")
                
                # Try with simple string
                print("3. Testing with simple string:")
                simple_id = "simple-test-id-123"
                await conn.execute("SELECT set_config('app.current_user_id', $1, true)", simple_id)
                simple_context = await conn.fetchval("SELECT current_setting('app.current_user_id', true)")
                print(f"   Simple context: {simple_context}")
                
                if simple_id == simple_context:
                    print("✅ SIMPLE STRING PATTERN WORKS!")
                    return True
                else:
                    print("❌ Both patterns failed")
                    return False
                    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        if database.pool:
            await database.pool.close()

if __name__ == "__main__":
    success = asyncio.run(test_exact_working_pattern())
    exit(0 if success else 1)
