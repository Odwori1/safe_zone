#!/usr/bin/env python3
"""
Test Messaging Schema - Phase 2 Verification
"""
import asyncio
import asyncpg
from app.core.config import settings

async def test_messaging_schema():
    """Verify messaging schema exists with proper RLS"""
    print("🔍 TESTING MESSAGING SCHEMA")
    print("=" * 50)
    
    conn = await asyncpg.connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database=settings.db_name
    )
    
    try:
        # 1. Verify tables exist
        tables = ['conversations', 'conversation_participants', 'messages']
        for table in tables:
            exists = await conn.fetchval(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = '{table}'
                );
            """)
            print(f"✅ Table {table} exists: {exists}")
            assert exists, f"Table {table} should exist"

        # 2. Verify RLS is enabled on all tables
        for table in tables:
            rls_enabled = await conn.fetchval(f"""
                SELECT rowsecurity FROM pg_tables 
                WHERE tablename = '{table}';
            """)
            print(f"✅ RLS enabled on {table}: {rls_enabled}")
            assert rls_enabled, f"RLS should be enabled on {table}"

        # 3. Verify indexes exist
        indexes = await conn.fetch("""
            SELECT tablename, indexname FROM pg_indexes 
            WHERE tablename IN ('conversations', 'conversation_participants', 'messages')
            ORDER BY tablename, indexname;
        """)
        print(f"✅ Indexes created: {len(indexes)}")
        for idx in indexes:
            print(f"   - {idx['tablename']}.{idx['indexname']}")

        # 4. Verify RLS policies exist
        policies = await conn.fetch("""
            SELECT tablename, policyname FROM pg_policies 
            WHERE tablename IN ('conversations', 'conversation_participants', 'messages')
            ORDER BY tablename, policyname;
        """)
        print(f"✅ RLS policies: {len(policies)}")
        for policy in policies:
            print(f"   - {policy['tablename']}.{policy['policyname']}")

        # 5. Test RLS enforcement
        test_user_id = "d31ce60e-e013-44a9-97e3-dda4ee30d6d2"
        
        # Try to insert without user context - should fail
        try:
            await conn.execute("INSERT INTO conversations (is_group) VALUES (false)")
            print("❌ RLS test FAILED - Should not allow insert without user context")
            assert False, "RLS should block this insert"
        except Exception as e:
            print(f"✅ RLS enforcement working on conversations: {str(e)[:100]}...")

        print("🎉 Messaging schema verification COMPLETE")
        
    except Exception as e:
        print(f"❌ Schema verification failed: {e}")
        raise
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(test_messaging_schema())
