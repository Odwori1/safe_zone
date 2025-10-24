"""
DEBUG RLS Context Setting Issue
"""
import asyncio
from app.database.database import database

async def debug_rls_context():
    """Debug why RLS context isn't being set properly"""
    print("🔍 DEBUGGING RLS CONTEXT SETTING")
    print("=" * 50)
    
    await database.connect()
    
    try:
        async with database.pool.acquire() as conn:
            # Test 1: Check current context
            print("1. Initial context:")
            initial = await conn.fetchval("SELECT current_setting('app.current_user_id', true)")
            print(f"   Initial: {initial}")
            
            # Test 2: Try setting context
            test_id = "12345678-1234-1234-1234-123456789abc"
            print(f"2. Setting context to: {test_id}")
            result = await conn.execute("SELECT set_config('app.current_user_id', $1, true)", test_id)
            print(f"   Set result: {result}")
            
            # Test 3: Check if context was set
            print("3. Checking context after set:")
            after_set = await conn.fetchval("SELECT current_setting('app.current_user_id', true)")
            print(f"   After set: {after_set}")
            
            # Test 4: Try with different syntax
            print("4. Trying alternative syntax:")
            await conn.execute("SET app.current_user_id TO %s", test_id)
            alt_check = await conn.fetchval("SELECT current_setting('app.current_user_id', true)")
            print(f"   Alternative: {alt_check}")
            
            # Test 5: Check if it's a transaction issue
            print("5. Testing in same command:")
            combined = await conn.fetchval("SELECT set_config('app.current_user_id', $1, true) as set_result, current_setting('app.current_user_id', true) as current", test_id)
            print(f"   Combined result: {combined}")
            
    except Exception as e:
        print(f"❌ Debug failed: {e}")
    finally:
        if database.pool:
            await database.pool.close()

if __name__ == "__main__":
    asyncio.run(debug_rls_context())
