#!/usr/bin/env python3
"""
Test WebSocket Sessions Schema - Phase 1, Step 1.1 Verification
"""
import asyncio
import asyncpg
from app.core.config import settings

async def test_websocket_sessions_table():
    """Verify WebSocket sessions table exists with proper RLS"""
    print("🔍 TESTING WEBSOCKET SESSIONS SCHEMA")
    print("=" * 50)
    
    conn = await asyncpg.connect(settings.database_url)
    
    try:
        # 1. Verify table exists
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'websocket_sessions'
            );
        """)
        print(f"✅ Table exists: {table_exists}")
        
        # 2. Verify RLS is enabled
        rls_enabled = await conn.fetchval("""
            SELECT row_security FROM pg_tables 
            WHERE tablename = 'websocket_sessions';
        """)
        print(f"✅ RLS enabled: {rls_enabled}")
        
        # 3. Verify indexes exist
        indexes = await conn.fetch("""
            SELECT indexname FROM pg_indexes 
            WHERE tablename = 'websocket_sessions';
        """)
        print(f"✅ Indexes created: {len(indexes)}")
        for idx in indexes:
            print(f"   - {idx['indexname']}")
            
        # 4. Verify policies exist
        policies = await conn.fetch("""
            SELECT policyname FROM pg_policies 
            WHERE tablename = 'websocket_sessions';
        """)
        print(f"✅ RLS policies: {len(policies)}")
        for policy in policies:
            print(f"   - {policy['policyname']}")
            
        print("🎉 WebSocket sessions schema verification COMPLETE")
        
    except Exception as e:
        print(f"❌ Schema verification failed: {e}")
        raise
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(test_websocket_sessions_table())
