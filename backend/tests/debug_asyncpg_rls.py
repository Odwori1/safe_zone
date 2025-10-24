"""
DEBUG AsyncPG RLS Context Issue
Find why set_config works in psql but not in asyncpg
"""
import asyncio
from app.database.database import database

async def debug_asyncpg_rls():
    """Debug the asyncpg-specific RLS issue"""
    print("🔍 DEBUG ASYNCPG RLS CONTEXT ISSUE")
    print("=" * 50)
    
    await database.connect()
    
    try:
        async with database.pool.acquire() as conn:
            # Test 1: Check if it's a transaction issue
            print("1. Testing in explicit transaction:")
            async with conn.transaction():
                await conn.execute("SELECT set_config('app.current_user_id', 'test-in-tx', true)")
                ctx_in_tx = await conn.fetchval("SELECT current_setting('app.current_user_id', true)")
                print(f"   Context in transaction: {ctx_in_tx}")
            
            # Check after transaction
            ctx_after_tx = await conn.fetchval("SELECT current_setting('app.current_user_id', true)")
            print(f"   Context after transaction: {ctx_after_tx}")
            
            # Test 2: Try different set_config syntax
            print("2. Testing different set_config syntax:")
            result = await conn.fetchval("SELECT set_config('app.current_user_id', 'test-syntax', true)")
            print(f"   set_config result: {result}")
            ctx_syntax = await conn.fetchval("SELECT current_setting('app.current_user_id', true)")
            print(f"   Context after syntax test: {ctx_syntax}")
            
            # Test 3: Try SET LOCAL (transaction-scoped)
            print("3. Testing SET LOCAL:")
            async with conn.transaction():
                await conn.execute("SET LOCAL app.current_user_id = 'local-value'")
                ctx_local = await conn.fetchval("SELECT current_setting('app.current_user_id', true)")
                print(f"   Context with SET LOCAL: {ctx_local}")
            
            # Test 4: Check if it's the third parameter (is_local)
            print("4. Testing is_local parameter:")
            await conn.execute("SELECT set_config('app.current_user_id', 'test-local-false', false)")
            ctx_local_false = await conn.fetchval("SELECT current_setting('app.current_user_id', true)")
            print(f"   Context with is_local=false: {ctx_local_false}")
            
            await conn.execute("SELECT set_config('app.current_user_id', 'test-local-true', true)")
            ctx_local_true = await conn.fetchval("SELECT current_setting('app.current_user_id', true)")
            print(f"   Context with is_local=true: {ctx_local_true}")
            
    except Exception as e:
        print(f"❌ Debug failed: {e}")
    finally:
        if database.pool:
            await database.pool.close()

if __name__ == "__main__":
    asyncio.run(debug_asyncpg_rls())
