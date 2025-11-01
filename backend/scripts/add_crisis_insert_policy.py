import asyncpg
import asyncio

async def add_insert_policy():
    """Add INSERT policy to crisis_resources table"""
    try:
        conn = await asyncpg.connect(
            host='127.0.0.1',
            port=5433,
            database='safe_zone',
            user='safe_zone_app_user',
            password='secure_app_password_2024'
        )
        
        print("🔧 Adding INSERT policy to crisis_resources...")
        
        # Add INSERT policy that allows authenticated users to insert crisis resources
        await conn.execute('''
            CREATE POLICY insert_crisis_resources_policy ON crisis_resources
            FOR INSERT TO authenticated
            WITH CHECK (true)
        ''')
        print("✅ INSERT policy added successfully")
        
        # Verify the policies
        policies = await conn.fetch('''
            SELECT policyname, cmd 
            FROM pg_policies 
            WHERE tablename = 'crisis_resources'
        ''')
        
        print("Updated policies:")
        for policy in policies:
            print(f"  - {policy['policyname']}: {policy['cmd']}")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

asyncio.run(add_insert_policy())
