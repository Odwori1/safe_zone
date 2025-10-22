#!/usr/bin/env python3
"""
PYTHON-BASED RLS TEST WITH PROPER INITIALIZATION
"""
import asyncio
import uuid
from app.database.database import database, init_db
from app.core.config import settings

async def initialize_database():
    """Initialize database if not already done"""
    if not database.pool:
        await init_db()

async def test_rls_with_app_connection():
    """Test RLS using the application's database connection"""
    
    print("🔍 TESTING RLS WITH APPLICATION DATABASE CONNECTION")
    print("=" * 60)
    
    # Initialize database first
    await initialize_database()
    
    # Get database connection from application pool
    conn = await database.pool.acquire()
    
    try:
        print("1. CURRENT DATABASE CONTEXT:")
        current_user = await conn.fetchval("SELECT current_user;")
        current_user_id = await conn.fetchval("SELECT current_setting('app.current_user_id', true);")
        print(f"   Database User: {current_user}")
        print(f"   App User ID: {current_user_id}")
        
        print("\n2. CREATING TEST DATA...")
        
        # Create test users
        user1_id = uuid.uuid4()
        user2_id = uuid.uuid4() 
        user3_id = uuid.uuid4()
        conversation_id = uuid.uuid4()
        
        # Insert test users
        await conn.execute("""
            INSERT INTO users (id, email, username, hashed_password, full_name, is_active)
            VALUES 
                ($1, 'test_user1_py@example.com', 'testuser1_py', 'fakehash1', 'Test User 1 Python', true),
                ($2, 'test_user2_py@example.com', 'testuser2_py', 'fakehash2', 'Test User 2 Python', true),
                ($3, 'test_user3_py@example.com', 'testuser3_py', 'fakehash3', 'Test User 3 Python', true)
            ON CONFLICT (email) DO NOTHING;
        """, user1_id, user2_id, user3_id)
        
        # Create conversation
        await conn.execute("""
            INSERT INTO conversations (id, title, created_at)
            VALUES ($1, 'Python RLS Test Conversation', NOW())
            ON CONFLICT DO NOTHING;
        """, conversation_id)
        
        # Add participants (user1 and user2)
        await conn.execute("""
            INSERT INTO conversation_participants (conversation_id, user_id, joined_at)
            VALUES 
                ($1, $2, NOW()),
                ($1, $3, NOW())
            ON CONFLICT DO NOTHING;
        """, conversation_id, user1_id, user2_id)
        
        # Add test messages
        await conn.execute("""
            INSERT INTO messages (id, conversation_id, sender_id, content, created_at)
            VALUES 
                ($1, $4, $2, 'Hello from User 1 - Python Test', NOW()),
                ($5, $4, $3, 'Hello from User 2 - Python Test', NOW())
            ON CONFLICT DO NOTHING;
        """, uuid.uuid4(), user1_id, user2_id, conversation_id, uuid.uuid4())
        
        print("3. TESTING RLS AS USER 1 (PARTICIPANT):")
        # Set user context for user1
        await conn.execute("SELECT set_config('app.current_user_id', $1, true);", str(user1_id))
        
        user1_conversations = await conn.fetch("SELECT id, title FROM conversations;")
        user1_messages = await conn.fetch("SELECT id, sender_id, content FROM messages;")
        
        print(f"   User1 sees {len(user1_conversations)} conversations (SHOULD BE 1)")
        print(f"   User1 sees {len(user1_messages)} messages (SHOULD BE 2)")
        
        print("\n4. TESTING RLS AS USER 3 (NOT IN CONVERSATION):")
        # Set user context for user3
        await conn.execute("SELECT set_config('app.current_user_id', $1, true);", str(user3_id))
        
        user3_conversations = await conn.fetch("SELECT id, title FROM conversations;")
        user3_messages = await conn.fetch("SELECT id, sender_id, content FROM messages;")
        
        print(f"   User3 sees {len(user3_conversations)} conversations (SHOULD BE 0)")
        print(f"   User3 sees {len(user3_messages)} messages (SHOULD BE 0)")
        
        print("\n5. TESTING RLS BYPASS (NO USER CONTEXT):")
        # Reset user context (table owner)
        await conn.execute("RESET app.current_user_id;")
        
        all_conversations = await conn.fetch("SELECT COUNT(*) as count FROM conversations;")
        all_messages = await conn.fetch("SELECT COUNT(*) as count FROM messages;")
        
        print(f"   Table owner sees {all_conversations[0]['count']} conversations (ALL)")
        print(f"   Table owner sees {all_messages[0]['count']} messages (ALL)")
        
        # Check if RLS is working
        rls_working = len(user3_conversations) == 0 and len(user3_messages) == 0
        rls_bypassed = len(user1_conversations) > 1  # Should only see 1
        
        print("\n" + "=" * 60)
        print("🎯 RLS SECURITY ASSESSMENT:")
        if rls_working and not rls_bypassed:
            print("✅ RLS IS WORKING CORRECTLY - User isolation enforced")
        elif not rls_working:
            print("🚨 RLS IS NOT WORKING - Users can see all data")
            print("   User3 (non-participant) could see conversations/messages")
        elif rls_bypassed:
            print("🚨 RLS IS PARTIALLY WORKING - But user1 saw too much data")
            print(f"   User1 saw {len(user1_conversations)} conversations (should be 1)")
        
        print("\n6. CLEANUP...")
        await conn.execute("DELETE FROM messages WHERE conversation_id = $1;", conversation_id)
        await conn.execute("DELETE FROM conversation_participants WHERE conversation_id = $1;", conversation_id)
        await conn.execute("DELETE FROM conversations WHERE id = $1;", conversation_id)
        await conn.execute("DELETE FROM users WHERE id IN ($1, $2, $3);", user1_id, user2_id, user3_id)
        
    except Exception as e:
        print(f"❌ Error during RLS test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await database.pool.release(conn)

async def check_rls_policies():
    """Check current RLS policies"""
    print("\n🔐 CHECKING RLS POLICIES:")
    print("-" * 40)
    
    await initialize_database()
    conn = await database.pool.acquire()
    
    try:
        # Get RLS policies
        policies = await conn.fetch("""
            SELECT 
                tablename,
                policyname,
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
            if policy['qual']:
                print(f"   Condition: {policy['qual']}")
            if policy['with_check']:
                print(f"   Check: {policy['with_check']}")
            print()
            
    except Exception as e:
        print(f"Error checking policies: {e}")
    finally:
        await database.pool.release(conn)

if __name__ == "__main__":
    asyncio.run(test_rls_with_app_connection())
    asyncio.run(check_rls_policies())
