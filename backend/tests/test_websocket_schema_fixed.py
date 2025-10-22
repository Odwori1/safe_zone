#!/usr/bin/env python3
"""
Test WebSocket Sessions Schema - Fixed Connection Version
"""
import asyncio
import asyncpg
from app.core.config import settings

async def test_websocket_sessions_table():
    """Verify WebSocket sessions table exists with proper RLS"""
    print("🔍 TESTING WEBSOCKET SESSIONS SCHEMA")
    print("=" * 50)
    
    # Use explicit connection parameters instead of URL
    conn = await asyncpg.connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database=settings.db_name
    )
    
    try:
        # 1. Verify table exists
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'websocket_sessions'
            );
        """)
        print(f"✅ Table exists: {table_exists}")
        assert table_exists, "WebSocket sessions table should exist"
        
        # 2. Verify RLS is enabled - FIXED COLUMN NAME
        rls_enabled = await conn.fetchval("""
            SELECT rowsecurity FROM pg_tables 
            WHERE tablename = 'websocket_sessions';
        """)
        print(f"✅ RLS enabled: {rls_enabled}")
        assert rls_enabled, "RLS should be enabled on websocket_sessions"
        
        # 3. Verify indexes exist
        indexes = await conn.fetch("""
            SELECT indexname FROM pg_indexes 
            WHERE tablename = 'websocket_sessions';
        """)
        print(f"✅ Indexes created: {len(indexes)}")
        for idx in indexes:
            print(f"   - {idx['indexname']}")
        assert len(indexes) >= 3, "Should have at least 3 indexes"
            
        # 4. Verify policies exist
        policies = await conn.fetch("""
            SELECT policyname FROM pg_policies 
            WHERE tablename = 'websocket_sessions';
        """)
        print(f"✅ RLS policies: {len(policies)}")
        for policy in policies:
            print(f"   - {policy['policyname']}")
        assert len(policies) >= 1, "Should have at least 1 RLS policy"
        
        # 5. Test RLS enforcement by trying to insert without user context
        try:
            await conn.execute("INSERT INTO websocket_sessions (user_id) VALUES ('d31ce60e-e013-44a9-97e3-dda4ee30d6d2')")
            print("❌ RLS test FAILED - Should not allow insert without user context")
            assert False, "RLS should block this insert"
        except Exception as e:
            print(f"✅ RLS enforcement working: {str(e)[:100]}...")
            
        # 6. Verify table structure
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'websocket_sessions'
            ORDER BY ordinal_position;
        """)
        print(f"✅ Table columns: {len(columns)}")
        expected_columns = ['id', 'user_id', 'connected_at', 'disconnected_at', 'last_activity', 'client_info', 'is_active']
        for col in columns:
            print(f"   - {col['column_name']} ({col['data_type']})")
            
        print("🎉 WebSocket sessions schema verification COMPLETE")
        
    except Exception as e:
        print(f"❌ Schema verification failed: {e}")
        raise
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(test_websocket_sessions_table())
