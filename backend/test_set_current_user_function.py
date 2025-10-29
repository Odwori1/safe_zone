import asyncio
import sys
import uuid
sys.path.append('.')
from app.database.database import database

async def test_set_current_user_function():
    print("🔍 TESTING set_current_user_id FUNCTION")
    print("=" * 50)
    
    await database.connect()
    try:
        test_user_id = str(uuid.uuid4())
        
        async with database.pool.acquire() as conn:
            # Test 1: Try to call set_current_user_id directly
            print("1. Testing set_current_user_id function...")
            try:
                result = await conn.execute("SELECT set_current_user_id($1)", test_user_id)
                print(f"   ✅ set_current_user_id called: {result}")
                
                # Check if app.current_user_id was set
                app_context = await conn.fetchval("SELECT current_setting('app.current_user_id', true)")
                print(f"   app.current_user_id after function: {app_context}")
                
            except Exception as e:
                print(f"   ❌ set_current_user_id failed: {e}")
                
            # Test 2: Compare with direct set_config
            print("\n2. Testing direct set_config...")
            await conn.execute("SELECT set_config('app.current_user_id', $1, false)", test_user_id)
            app_context = await conn.fetchval("SELECT current_setting('app.current_user_id', true)")
            print(f"   app.current_user_id after direct set: {app_context}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await database.close()

asyncio.run(test_set_current_user_function())
