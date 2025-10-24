"""
DEEP RLS CONTEXT INVESTIGATION
Find out why RLS context isn't working
"""
import asyncio
from app.database.database import database

async def deep_investigate_rls():
    """Deep investigation of RLS context issue"""
    print("🔍 DEEP RLS CONTEXT INVESTIGATION")
    print("=" * 50)
    
    await database.connect()
    
    try:
        async with database.pool.acquire() as conn:
            # Test 1: Check if custom configs are allowed
            print("1. Checking custom configuration permissions:")
            custom_configs = await conn.fetchval("SHOW custom_variable_classes")
            print(f"   Custom variable classes: {custom_configs}")
            
            # Test 2: Try setting a different custom variable
            print("2. Testing with different custom variable:")
            await conn.execute("SELECT set_config('app.test_setting', 'test_value', true)")
            test_setting = await conn.fetchval("SELECT current_setting('app.test_setting', true)")
            print(f"   Test setting: {test_setting}")
            
            # Test 3: Check current user and database
            print("3. Checking database user and session:")
            current_user = await conn.fetchval("SELECT current_user")
            current_database = await conn.fetchval("SELECT current_database()")
            print(f"   Current user: {current_user}")
            print(f"   Current database: {current_database}")
            
            # Test 4: Check if app settings are in allowed list
            print("4. Checking app settings configuration:")
            try:
                app_context = await conn.fetchval("SELECT current_setting('app.current_user_id')")
                print(f"   App context (no true): {app_context}")
            except Exception as e:
                print(f"   App context error: {e}")
            
            # Test 5: Try with local (transaction-level) setting
            print("5. Testing local (transaction) setting:")
            await conn.execute("SET LOCAL app.current_user_id = 'local_test'")
            local_setting = await conn.fetchval("SELECT current_setting('app.current_user_id', true)")
            print(f"   Local setting: {local_setting}")
            
            # Test 6: Check all current settings
            print("6. All current settings with 'app' prefix:")
            app_settings = await conn.fetch("SELECT name, setting FROM pg_settings WHERE name LIKE 'app.%'")
            for setting in app_settings:
                print(f"   {setting['name']} = {setting['setting']}")
                
    except Exception as e:
        print(f"❌ Investigation failed: {e}")
    finally:
        if database.pool:
            await database.pool.close()

if __name__ == "__main__":
    asyncio.run(deep_investigate_rls())
