import asyncio
import sys
sys.path.append('.')
from app.database.database import database

async def test_current_settings():
    print("🔍 TESTING CURRENT SETTINGS DURING OPERATIONS")
    print("=" * 50)
    
    await database.connect()
    try:
        async with database.pool.acquire() as conn:
            # Check what current_setting values exist
            settings = await conn.fetch("""
                SELECT name, setting 
                FROM pg_settings 
                WHERE name LIKE '%app%' OR name LIKE '%request%' OR name LIKE '%jwt%'
            """)
            print("Current relevant settings:")
            for setting in settings:
                print(f"  {setting['name']}: {setting['setting']}")
            
            # Test what happens when we try different contexts
            print("\nTesting different context settings:")
            
            # Test 1: app.current_user_id
            await conn.execute("SELECT set_config('app.current_user_id', 'test-user-123', false)")
            app_context = await conn.fetchval("SELECT current_setting('app.current_user_id', true)")
            print(f"  app.current_user_id: {app_context}")
            
            # Test 2: request.jwt.claim.sub  
            await conn.execute("SELECT set_config('request.jwt.claim.sub', 'test-jwt-sub', false)")
            jwt_context = await conn.fetchval("SELECT current_setting('request.jwt.claim.sub', true)")
            print(f"  request.jwt.claim.sub: {jwt_context}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await database.close()

asyncio.run(test_current_settings())
