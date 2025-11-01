import asyncpg
import asyncio

async def check_crisis_rls():
    try:
        conn = await asyncpg.connect(
            host='127.0.0.1',
            port=5433,
            database='safe_zone',
            user='safe_zone_app_user',
            password='secure_app_password_2024'
        )
        
        print("🔍 Checking crisis_resources RLS policies...")
        
        # Check if RLS is enabled
        rls_enabled = await conn.fetchval("SELECT rowsecurity FROM pg_tables WHERE tablename = 'crisis_resources'")
        print(f"RLS enabled: {rls_enabled}")
        
        # Check policies
        policies = await conn.fetch('''
            SELECT policyname, permissive, roles, cmd, qual, with_check 
            FROM pg_policies 
            WHERE tablename = 'crisis_resources'
        ''')
        
        print("Current policies:")
        for policy in policies:
            print(f"  - {policy['policyname']}: {policy['cmd']}")
            print(f"    Qual: {policy['qual']}")
            print(f"    With Check: {policy['with_check']}")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(check_crisis_rls())
