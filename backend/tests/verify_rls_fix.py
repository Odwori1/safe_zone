#!/usr/bin/env python3
"""
VERIFY RLS FIX - Test with proper user context
"""
import asyncio
import uuid
from app.database.database import database, init_db

async def test_rls_with_proper_context():
    """Test RLS with proper user context setup"""
    
    print("🔍 TESTING RLS WITH PROPER USER CONTEXT")
    print("=" * 60)
    
    await initialize_database()
    conn = await database.pool.acquire()
    
    try:
        # Create test users and conversation
        user1_id = uuid.uuid4()
        user2_id = uuid.uuid4()
        user3_id = uuid.uuid4()
        conv_id = uuid.uuid4()
        
        # Setup
        await conn.execute("""
            INSERT INTO users (id, email, username, hashed_password, full_name, is_active)
            VALUES 
                ($1, 'verify_user1@example.com', 'verify1', 'hash1', 'Verify User 1', true),
                ($2, 'verify_user2@example.com', 'verify2', 'hash2', 'Verify User 2', true),
                ($3, 'verify_user3@example.com', 'verify3', 'hash3', 'Verify User 3', true)
            ON CONFLICT (email) DO NOTHING;
        """, user1_id, user2_id, user3_id)
        
        await conn.execute("""
            INSERT INTO conversations (id, title, created_at)
            VALUES ($1, 'Verify RLS Conversation', NOW())
            ON CONFLICT DO NOTHING;
        """, conv_id)
        
        await conn.execute("""
            INSERT INTO conversation_participants (conversation_id, user_id, joined_at)
            VALUES 
                ($1, $2, NOW()),
                ($1, $3, NOW())
            ON CONFLICT DO NOTHING;
        """, conv_id, user1_id, user2_id)
        
        # Test 1: User1 should see only their conversation
        print("1. Testing User1 (participant):")
        await conn.execute("SELECT set_config('app.current_user_id', $1, true);", str(user1_id))
        user1_convos = await conn.fetch("SELECT id, title FROM conversations;")
        print(f"   User1 sees {len(user1_convos)} conversations")
        
        # Test 2: User3 should see NO conversations
        print("2. Testing User3 (non-participant):")
        await conn.execute("SELECT set_config('app.current_user_id', $1, true);", str(user3_id))
        user3_convos = await conn.fetch("SELECT id, title FROM conversations;")
        print(f"   User3 sees {len(user3_convos)} conversations")
        
        # Test 3: Reset context (table owner sees all)
        print("3. Testing table owner (no context):")
        await conn.execute("RESET app.current_user_id;")
        owner_convos = await conn.fetch("SELECT COUNT(*) as count FROM conversations;")
        print(f"   Owner sees {owner_convos[0]['count']} conversations")
        
        # Assessment
        print("\n4. SECURITY ASSESSMENT:")
        if len(user1_convos) == 1 and len(user3_convos) == 0:
            print("   ✅ RLS WORKING CORRECTLY")
            print("   User isolation is properly enforced")
        else:
            print("   🚨 RLS STILL BROKEN")
            print(f"   User1 should see 1, sees {len(user1_convos)}")
            print(f"   User3 should see 0, sees {len(user3_convos)}")
            print("   This confirms the table ownership issue")
        
        # Cleanup
        await conn.execute("DELETE FROM conversation_participants WHERE conversation_id = $1;", conv_id)
        await conn.execute("DELETE FROM conversations WHERE id = $1;", conv_id)
        await conn.execute("DELETE FROM users WHERE id IN ($1, $2, $3);", user1_id, user2_id, user3_id)
        
    except Exception as e:
        print(f"Error during verification: {e}")
    finally:
        await database.pool.release(conn)

async def initialize_database():
    """Initialize database if not already done"""
    if not database.pool:
        await init_db()

if __name__ == "__main__":
    asyncio.run(test_rls_with_proper_context())
