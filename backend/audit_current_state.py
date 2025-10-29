import asyncio
import asyncpg
from app.core.config import settings

async def audit_current_state():
    try:
        conn = await asyncpg.connect(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database=settings.db_name
        )
        
        print("🔍 AUDITING CURRENT DATABASE STATE")
        print("=" * 50)
        
        # 1. Check current function definition
        print("1. CURRENT set_current_user_id FUNCTION:")
        func_def = await conn.fetchval("""
            SELECT pg_get_functiondef(oid) 
            FROM pg_proc 
            WHERE proname = 'set_current_user_id'
        """)
        print(func_def)
        print()
        
        # 2. Check posts RLS policies
        print("2. POSTS RLS POLICIES:")
        policies = await conn.fetch("""
            SELECT policyname, cmd, qual, with_check 
            FROM pg_policies 
            WHERE tablename = 'posts'
        """)
        for p in policies:
            print(f"   {p['policyname']}: {p['cmd']}")
            if p['qual']: print(f"      Qual: {p['qual']}")
            if p['with_check']: print(f"      With Check: {p['with_check']}")
        print()
        
        # 3. Check comments RLS policies
        print("3. COMMENTS RLS POLICIES:")
        policies = await conn.fetch("""
            SELECT policyname, cmd, qual, with_check 
            FROM pg_policies 
            WHERE tablename = 'comments'
        """)
        for p in policies:
            print(f"   {p['policyname']}: {p['cmd']}")
            if p['qual']: print(f"      Qual: {p['qual']}")
            if p['with_check']: print(f"      With Check: {p['with_check']}")
        print()
        
        # 4. Test both approaches
        print("4. TESTING BOTH APPROACHES:")
        
        # Test current function approach
        await conn.execute("SELECT set_current_user_id('d31ce60e-e013-44a9-97e3-dda4ee30d6d2');")
        app_current = await conn.fetchval("SELECT current_setting('app.current_user_id', true);")
        jwt_claim = await conn.fetchval("SELECT current_setting('request.jwt.claim.sub', true);")
        print(f"   After set_current_user_id():")
        print(f"      app.current_user_id = {app_current}")
        print(f"      request.jwt.claim.sub = {jwt_claim}")
        
        # Test direct JWT approach
        await conn.execute("SELECT set_config('request.jwt.claim.sub', 'test123', true);")
        app_current = await conn.fetchval("SELECT current_setting('app.current_user_id', true);")
        jwt_claim = await conn.fetchval("SELECT current_setting('request.jwt.claim.sub', true);")
        print(f"   After direct set_config():")
        print(f"      app.current_user_id = {app_current}")
        print(f"      request.jwt.claim.sub = {jwt_claim}")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error during audit: {e}")

asyncio.run(audit_current_state())
