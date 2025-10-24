"""
VERIFY COMPLETE RLS FIX
Test that set_config with is_local=false provides session-level context
"""
import asyncio
from app.database.database import database
from uuid import uuid4

async def verify_complete_rls_fix():
    """Verify the complete RLS fix works"""
    print("🔍 VERIFYING COMPLETE RLS FIX")
    print("=" * 50)
    
    await database.connect()
    
    try:
        async with database.pool.acquire() as conn:
            # Test 1: Use set_config with is_local=false
            test_user = "complete-test-user"
            print(f"1. Setting session context with set_config(false): {test_user}")
            
            result = await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)", 
                test_user
            )
            print(f"   set_config result: {result}")
            
            # Test 2: Verify context is set
            current_ctx = await conn.fetchval("SELECT current_setting('app.current_user_id', true)")
            print(f"2. Current context: {current_ctx}")
            
            if current_ctx != test_user:
                print("❌ Context not set properly")
                return False
            
            # Test 3: Verify persistence across multiple operations
            print("3. Testing persistence across operations:")
            for i in range(5):
                await conn.execute("SELECT $1", i)
                ctx_after = await conn.fetchval("SELECT current_setting('app.current_user_id', true)")
                if ctx_after != test_user:
                    print(f"❌ Context lost at operation {i+1}")
                    return False
                print(f"   Operation {i+1}: context maintained")
            
            # Test 4: Test with UUID (like our actual use case)
            print("4. Testing with UUID:")
            test_uuid = str(uuid4())
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)", 
                test_uuid
            )
            ctx_uuid = await conn.fetchval("SELECT current_setting('app.current_user_id', true)")
            print(f"   UUID context: {ctx_uuid}")
            
            if ctx_uuid == test_uuid:
                print("✅ UUID CONTEXT WORKS!")
            else:
                print("❌ UUID context failed")
                return False
            
            print("🎉 COMPLETE RLS FIX VERIFIED!")
            print("✅ set_config with is_local=false provides session-level context")
            print("✅ Context persists across multiple operations")
            print("✅ UUID formatting works correctly")
            return True
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False
    finally:
        if database.pool:
            await database.pool.close()

if __name__ == "__main__":
    success = asyncio.run(verify_complete_rls_fix())
    exit(0 if success else 1)
