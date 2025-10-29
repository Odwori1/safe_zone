import asyncio
import asyncpg
from app.core.config import settings

async def check_set_current_user_id():
    try:
        conn = await asyncpg.connect(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database=settings.db_name
        )
        
        print("🔍 Checking if set_current_user_id function exists...")
        
        # Check if function exists
        function_exists = await conn.fetchval("""
            SELECT EXISTS(
                SELECT 1 FROM pg_proc 
                WHERE proname = 'set_current_user_id'
            );
        """)
        
        if function_exists:
            print("✅ set_current_user_id function EXISTS in database")
            
            # Check what it does
            func_def = await conn.fetchval("""
                SELECT pg_get_functiondef(oid) 
                FROM pg_proc 
                WHERE proname = 'set_current_user_id'
            """)
            print(f"Function definition: {func_def}")
        else:
            print("❌ set_current_user_id function does NOT exist")
            
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(check_set_current_user_id())
