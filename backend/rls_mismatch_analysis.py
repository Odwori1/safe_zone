import asyncio
import asyncpg
from app.core.config import settings

async def analyze_rls_mismatch():
    print("🔍 COMPREHENSIVE RLS ARCHITECTURE ANALYSIS")
    print("=" * 60)
    
    conn = await asyncpg.connect(settings.database_url)
    try:
        # 1. Check what RLS policies actually use
        print("\n1. RLS POLICY CONTEXT ANALYSIS:")
        print("-" * 40)
        
        tables_with_policies = await conn.fetch('''
            SELECT DISTINCT tablename 
            FROM pg_policies 
            WHERE schemaname = 'public'
            ORDER BY tablename
        ''')
        
        policy_contexts = set()
        for table in tables_with_policies:
            table_name = table['tablename']
            policies = await conn.fetch('''
                SELECT qual FROM pg_policies WHERE tablename = $1
            ''', table_name)
            
            for policy in policies:
                qual = policy['qual']
                if qual:
                    if 'request.jwt.claim.sub' in qual:
                        policy_contexts.add('request.jwt.claim.sub')
                    elif 'app.current_user_id' in qual:
                        policy_contexts.add('app.current_user_id')
                    elif 'current_setting' in qual:
                        # Extract the setting name
                        import re
                        match = re.search(r"current_setting\('([^']+)'", qual)
                        if match:
                            policy_contexts.add(match.group(1))
        
        print(f"RLS policies use contexts: {list(policy_contexts)}")
        
        # 2. Check database function
        print("\n2. DATABASE FUNCTION ANALYSIS:")
        print("-" * 40)
        
        set_current_user_exists = await conn.fetchval('''
            SELECT EXISTS(SELECT 1 FROM pg_proc WHERE proname = 'set_current_user_id')
        ''')
        print(f"set_current_user_id function exists: {set_current_user_exists}")
        
        if set_current_user_exists:
            func_def = await conn.fetchval('''
                SELECT pg_get_functiondef(oid) FROM pg_proc WHERE proname = 'set_current_user_id'
            ''')
            print(f"Function sets context to: {func_def}")
        
        # 3. Test both approaches
        print("\n3. CONTEXT SETTING TEST:")
        print("-" * 40)
        
        test_user_id = '12345678-1234-1234-1234-123456789abc'
        
        # Test set_config approach
        try:
            await conn.execute("SELECT set_config('app.current_user_id', $1, false)", test_user_id)
            app_context = await conn.fetchval("SELECT current_setting('app.current_user_id', true)")
            print(f"set_config('app.current_user_id') works: {app_context == test_user_id}")
        except Exception as e:
            print(f"set_config('app.current_user_id') failed: {e}")
        
        # Test set_current_user_id approach
        if set_current_user_exists:
            try:
                await conn.execute("SELECT set_current_user_id($1)", test_user_id)
                print("set_current_user_id() executed (but we can't verify the context it sets)")
            except Exception as e:
                print(f"set_current_user_id() failed: {e}")
        
        # Test request.jwt.claim.sub approach
        try:
            await conn.execute("SELECT set_config('request.jwt.claim.sub', $1, false)", test_user_id)
            jwt_context = await conn.fetchval("SELECT current_setting('request.jwt.claim.sub', true)")
            print(f"set_config('request.jwt.claim.sub') works: {jwt_context == test_user_id}")
        except Exception as e:
            print(f"set_config('request.jwt.claim.sub') failed: {e}")
            
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(analyze_rls_mismatch())
