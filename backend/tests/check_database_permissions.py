"""
Check Database User Permissions for RLS
"""
import asyncio
from app.database.database import database

async def check_permissions():
    """Check if database user has proper permissions"""
    print("🔐 DATABASE USER PERMISSIONS CHECK")
    print("=" * 50)
    
    await database.connect()
    
    try:
        async with database.pool.acquire() as conn:
            # Check current user privileges
            print("1. Current user privileges:")
            user_privs = await conn.fetch("""
                SELECT 
                    usename,
                    useconfig
                FROM pg_user 
                WHERE usename = current_user
            """)
            for priv in user_privs:
                print(f"   User: {priv['usename']}")
                print(f"   Config: {priv['useconfig']}")
            
            # Check if we can create custom configurations
            print("2. Testing custom configuration creation:")
            try:
                # Try to set a custom configuration
                await conn.execute("SET custom.app_test = 'works'")
                test_val = await conn.fetchval("SHOW custom.app_test")
                print(f"   Custom config test: {test_val}")
            except Exception as e:
                print(f"   Custom config failed: {e}")
            
            # Check RLS status on tables
            print("3. RLS status on key tables:")
            rls_status = await conn.fetch("""
                SELECT 
                    relname as table_name,
                    relrowsecurity as rls_enabled
                FROM pg_class 
                WHERE relname IN ('live_audio_room_moderations', 'content_reports', 'users')
                AND relkind = 'r'
            """)
            for status in rls_status:
                print(f"   Table {status['table_name']}: RLS {'ENABLED' if status['rls_enabled'] else 'DISABLED'}")
                
    except Exception as e:
        print(f"❌ Permission check failed: {e}")
    finally:
        if database.pool:
            await database.pool.close()

if __name__ == "__main__":
    asyncio.run(check_permissions())
