"""
TEST SESSION-LEVEL RLS CONTEXT
Use SET instead of set_config for session-level persistence
"""
import asyncio
from app.database.database import database

async def test_session_level_rls():
    """Test session-level RLS context setting"""
    print("🔍 TESTING SESSION-LEVEL RLS CONTEXT")
    print("=" * 50)
    
    await database.connect()
    
    try:
        async with database.pool.acquire() as conn:
            # Method 1: Use SET for session-level context
            print("1. Testing SET (session-level):")
            await conn.execute("SET app.current_user_id = 'session-test-123'")
            ctx_session = await conn.fetchval("SELECT current_setting('app.current_user_id', true)")
            print(f"   Session context: {ctx_session}")
            
            # Test if it persists across operations
            await conn.execute("SELECT 1")  # Another operation
            ctx_after_op = await conn.fetchval("SELECT current_setting('app.current_user_id', true)")
            print(f"   Context after operation: {ctx_after_op}")
            
            # Method 2: Use set_config with is_local=false
            print("2. Testing set_config with is_local=false:")
            await conn.execute("SELECT set_config('app.current_user_id', 'config-false-test', false)")
            ctx_config_false = await conn.fetchval("SELECT current_setting('app.current_user_id', true)")
            print(f"   Config false context: {ctx_config_false}")
            
            # Test persistence
            await conn.execute("SELECT 1")
            ctx_config_after = await conn.fetchval("SELECT current_setting('app.current_user_id', true)")
            print(f"   Config context after operation: {ctx_config_after}")
            
            # Method 3: Test in our CRUD pattern
            print("3. Testing in CRUD-like pattern:")
            test_user_id = "crud-test-user-456"
            await conn.execute("SET app.current_user_id = $1", test_user_id)
            
            # Simulate CRUD operations
            current_ctx = await conn.fetchval("SELECT current_setting('app.current_user_id', true)")
            print(f"   Context during CRUD: {current_ctx}")
            
            if current_ctx == test_user_id:
                print("✅ SESSION-LEVEL RLS CONTEXT WORKS!")
                return True
            else:
                print("❌ Session-level context failed")
                return False
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        if database.pool:
            await database.pool.close()

if __name__ == "__main__":
    success = asyncio.run(test_session_level_rls())
    exit(0 if success else 1)
