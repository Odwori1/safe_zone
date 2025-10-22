#!/usr/bin/env python3
"""
CHECK CURRENT RLS POLICIES IN DATABASE
"""
import asyncpg
import asyncio
from app.core.config import settings

async def check_rls_policies():
    """Check current RLS policies and table ownership"""
    conn = await asyncpg.connect(
        host=settings.DATABASE_HOST,
        port=settings.DATABASE_PORT,
        user=settings.DATABASE_USER,
        password=settings.DATABASE_PASSWORD,
        database=settings.DATABASE_NAME
    )
    
    print("🔍 DATABASE RLS STATUS")
    print("=" * 60)
    
    # Check table RLS status
    tables = await conn.fetch("""
        SELECT 
            tablename,
            tableowner,
            rowsecurity,
            (SELECT count(*) FROM pg_policies WHERE tablename = t.tablename) as policy_count
        FROM pg_tables t 
        WHERE schemaname = 'public'
        AND tablename IN ('conversations', 'conversation_participants', 'messages', 'users')
        ORDER BY tablename;
    """)
    
    print("📊 TABLE RLS STATUS:")
    for table in tables:
        status = "✅ ENABLED" if table['rowsecurity'] else "❌ DISABLED"
        print(f"  {table['tablename']:25} | {status:10} | {table['policy_count']:2} policies | owner: {table['tableowner']}")
    
    print("\n🔐 DETAILED RLS POLICIES:")
    print("-" * 60)
    
    # Get detailed policy information
    policies = await conn.fetch("""
        SELECT 
            tablename,
            policyname,
            permissive,
            roles,
            cmd,
            qual,
            with_check
        FROM pg_policies 
        WHERE schemaname = 'public'
        AND tablename IN ('conversations', 'conversation_participants', 'messages')
        ORDER BY tablename, policyname;
    """)
    
    for policy in policies:
        print(f"📋 {policy['tablename']}.{policy['policyname']}:")
        print(f"   Command: {policy['cmd']}")
        print(f"   Roles: {policy['roles']}")
        if policy['qual']:
            print(f"   Condition: {policy['qual']}")
        if policy['with_check']:
            print(f"   Check: {policy['with_check']}")
        print()
    
    # Check if current user can bypass RLS
    user_info = await conn.fetch("""
        SELECT 
            usename,
            usesuper AS is_superuser,
            usebypassrls AS can_bypass_rls
        FROM pg_user 
        WHERE usename = current_user;
    """)
    
    print("👤 CURRENT DATABASE USER:")
    for user in user_info:
        print(f"  Username: {user['usename']}")
        print(f"  Superuser: {user['is_superuser']}")
        print(f"  Bypass RLS: {user['can_bypass_rls']}")
    
    # Test RLS with non-owner scenario
    print("\n🧪 RLS BYPASS TEST:")
    print("-" * 60)
    
    # Create a test user that doesn't own tables
    test_user = "rls_test_user"
    try:
        await conn.execute(f"CREATE USER {test_user} WITH PASSWORD 'testpass123';")
        await conn.execute(f"GRANT CONNECT ON DATABASE {settings.DATABASE_NAME} TO {test_user};")
        await conn.execute(f"GRANT USAGE ON SCHEMA public TO {test_user};")
        await conn.execute(f"GRANT SELECT ON ALL TABLES IN SCHEMA public TO {test_user};")
        
        print(f"✅ Created test user: {test_user}")
        
        # Test with non-owner connection
        test_conn = await asyncpg.connect(
            host=settings.DATABASE_HOST,
            port=settings.DATABASE_PORT,
            user=test_user,
            password='testpass123',
            database=settings.DATABASE_NAME
        )
        
        # Try to access data without setting user context
        try:
            result = await test_conn.fetch("SELECT * FROM conversations LIMIT 1;")
            print("❌ RLS BYPASSED: Non-owner could access conversations without context")
        except Exception as e:
            print("✅ RLS WORKING: Non-owner correctly blocked from conversations")
            print(f"   Error: {e}")
        
        await test_conn.close()
        
        # Cleanup
        await conn.execute(f"DROP USER {test_user};")
        
    except Exception as e:
        print(f"⚠️  Test user creation failed (may already exist): {e}")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(check_rls_policies())
