import asyncpg
import asyncio

async def add_policy_as_postgres():
    """Add INSERT policy using postgres superuser"""
    try:
        # Connect as postgres (superuser)
        conn = await asyncpg.connect(
            host='127.0.0.1',
            port=5433,
            database='safe_zone',
            user='postgres',  # Use postgres superuser
            password='password'  # Use the postgres password
        )
        
        print("🔧 Adding INSERT policy as postgres...")
        
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
        
    except Exception as e:
        print(f"❌ Error: {e}")
        # If postgres password is different, try without password or check what it is
        print("💡 If postgres password failed, check your postgres user password")

asyncio.run(add_policy_as_postgres())
