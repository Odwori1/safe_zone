#!/usr/bin/env python3
"""
Diagnose RLS Policy Issue
"""
import asyncio
import asyncpg
from app.core.config import settings

async def diagnose_rls():
    print("🔍 Diagnosing RLS Policy Issue...")
    
    try:
        # Connect to database
        conn = await asyncpg.connect(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database=settings.db_name
        )
        
        print("✅ Database connected")
        
        # 1. Check current RLS policies
        print("\n1. Checking RLS Policies...")
        policies = await conn.fetch("""
            SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check 
            FROM pg_policies 
            WHERE tablename = 'posts'
        """)
        
        for policy in policies:
            print(f"   Policy: {policy['policyname']}")
            print(f"   Command: {policy['cmd']}")
            print(f"   Qual: {policy['qual']}")
            print(f"   With Check: {policy['with_check']}")
            print("   ---")
        
        # 2. Check if we can set JWT claim
        print("\n2. Testing JWT Claim Setting...")
        try:
            # Try to set a test user ID
            test_user_id = "d31ce60e-e013-44a9-97e3-dda4ee30d6d2"  # From your test user
            await conn.execute("SELECT set_config('request.jwt.claim.sub', $1, true)", test_user_id)
            print("✅ Can set JWT claim")
            
            # Verify it was set
            current_sub = await conn.fetchval("SELECT current_setting('request.jwt.claim.sub', true)")
            print(f"   Current JWT sub: {current_sub}")
            
        except Exception as e:
            print(f"❌ Cannot set JWT claim: {e}")
        
        # 3. Test direct post creation with RLS
        print("\n3. Testing Direct Post Creation with RLS...")
        try:
            # First set the user context
            await conn.execute("SELECT set_config('request.jwt.claim.sub', $1, true)", test_user_id)
            
            # Try to create a post
            result = await conn.execute("""
                INSERT INTO posts (user_id, content, visibility, is_anonymous)
                VALUES ($1, $2, $3, $4)
            """, test_user_id, "Test post via direct SQL", "public", False)
            
            print("✅ Direct post creation with RLS WORKING")
            print(f"   Result: {result}")
            
        except Exception as e:
            print(f"❌ Direct post creation failed: {e}")
        
        # 4. Check if user exists
        print("\n4. Verifying Test User...")
        user = await conn.fetchrow("SELECT id, email FROM users WHERE id = $1", test_user_id)
        if user:
            print(f"✅ Test user exists: {user['email']}")
        else:
            print("❌ Test user not found")
            # List available users
            users = await conn.fetch("SELECT id, email FROM users LIMIT 5")
            print("Available users:")
            for u in users:
                print(f"   {u['id']} - {u['email']}")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Diagnosis failed: {e}")

if __name__ == "__main__":
    asyncio.run(diagnose_rls())
