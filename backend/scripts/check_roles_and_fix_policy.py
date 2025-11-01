import asyncpg
import asyncio

async def check_roles_and_fix():
    try:
        conn = await asyncpg.connect(
            host='127.0.0.1',
            port=5433,
            database='safe_zone',
            user='safe_zone_app_user',
            password='secure_app_password_2024'
        )
        
        print("🔍 Checking available roles...")
        
        # Check what roles exist
        roles = await conn.fetch("SELECT rolname FROM pg_roles WHERE rolname NOT LIKE 'pg_%'")
        print("Available roles:")
        for role in roles:
            print(f"  - {role['rolname']}")
        
        # Check what role is used in existing policies
        existing_policies = await conn.fetch('''
            SELECT policyname, roles, cmd 
            FROM pg_policies 
            WHERE tablename = 'crisis_resources'
        ''')
        
        print("Existing crisis_resources policies:")
        for policy in existing_policies:
            print(f"  - {policy['policyname']}: {policy['cmd']} for roles {policy['roles']}")
        
        # Use the same role as the existing SELECT policy
        if existing_policies:
            target_role = existing_policies[0]['roles'][0] if existing_policies[0]['roles'] else 'public'
            print(f"🎯 Using role: {target_role}")
            
            # Add INSERT policy with the correct role
            await conn.execute(f'''
                CREATE POLICY insert_crisis_resources_policy ON crisis_resources
                FOR INSERT TO {target_role}
                WITH CHECK (true)
            ''')
            print(f"✅ INSERT policy added for role: {target_role}")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

asyncio.run(check_roles_and_fix())
