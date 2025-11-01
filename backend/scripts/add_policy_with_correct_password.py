import asyncpg
import asyncio

async def add_policy_with_correct_password():
    """Add INSERT policy using postgres superuser with correct password"""
    try:
        # Connect as postgres (superuser) with correct password
        conn = await asyncpg.connect(
            host='127.0.0.1',
            port=5433,
            database='safe_zone',
            user='postgres',
            password='0791486006@safezone'  # Use the correct password
        )
        
        print("🔧 Adding INSERT policy as postgres with correct password...")
        
        # First, drop any existing INSERT policy to avoid conflicts
        try:
            await conn.execute("DROP POLICY IF EXISTS insert_crisis_resources_policy ON crisis_resources")
            print("✅ Dropped any existing INSERT policy")
        except Exception as e:
            print(f"ℹ️ No existing policy to drop: {e}")
        
        # Add INSERT policy that allows public to insert crisis resources
        await conn.execute('''
            CREATE POLICY insert_crisis_resources_policy ON crisis_resources
            FOR INSERT TO PUBLIC
            WITH CHECK (true)
        ''')
        print("✅ INSERT policy added for PUBLIC role")
        
        # Verify the policies
        policies = await conn.fetch('''
            SELECT policyname, cmd, roles
            FROM pg_policies 
            WHERE tablename = 'crisis_resources'
        ''')
        
        print("Updated policies:")
        for policy in policies:
            print(f"  - {policy['policyname']}: {policy['cmd']} for roles {policy['roles']}")
        
        await conn.close()
        print("🎉 RLS INSERT policy successfully added!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(add_policy_with_correct_password())
