"""
TEST CORRECT SET SYNTAX for RLS Context
"""
import asyncio
from app.database.database import database

async def test_correct_set_syntax():
    """Test correct syntax for SET commands"""
    print("🔍 TESTING CORRECT SET SYNTAX")
    print("=" * 50)
    
    await database.connect()
    
    try:
        async with database.pool.acquire() as conn:
            # Method 1: String formatting (be careful with SQL injection)
            print("1. Testing string formatting:")
            test_user = "format-user-123"
            await conn.execute(f"SET app.current_user_id = '{test_user}'")
            ctx_format = await conn.fetchval("SELECT current_setting('app.current_user_id', true)")
            print(f"   Format context: {ctx_format}")
            
            # Method 2: Use set_config with is_local=false (session-level)
            print("2. Testing set_config with is_local=false:")
            test_user2 = "config-user-456"
            result = await conn.execute("SELECT set_config('app.current_user_id', $1, false)", test_user2)
            print(f"   set_config result: {result}")
            ctx_config = await conn.fetchval("SELECT current_setting('app.current_user_id', true)")
            print(f"   Config context: {ctx_config}")
            
            # Method 3: Test persistence
            print("3. Testing persistence:")
            await conn.execute("SELECT 1")
            await conn.execute("SELECT 2") 
            ctx_persist = await conn.fetchval("SELECT current_setting('app.current_user_id', true)")
            print(f"   Persistent context: {ctx_persist}")
            
            # Method 4: Test with UUID
            print("4. Testing with UUID:")
            import uuid
            test_uuid = str(uuid.uuid4())
            await conn.execute(f"SET app.current_user_id = '{test_uuid}'")
            ctx_uuid = await conn.fetchval("SELECT current_setting('app.current_user_id', true)")
            print(f"   UUID context: {ctx_uuid}")
            print(f"   Match: {test_uuid == ctx_uuid}")
            
            if test_uuid == ctx_uuid:
                print("✅ UUID SET SYNTAX WORKS!")
                return True
            else:
                print("❌ UUID syntax failed")
                return False
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        if database.pool:
            await database.pool.close()

if __name__ == "__main__":
    success = asyncio.run(test_correct_set_syntax())
    exit(0 if success else 1)
