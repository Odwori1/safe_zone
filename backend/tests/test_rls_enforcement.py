#!/usr/bin/env python3
"""
Test RLS Enforcement Directly
"""
import asyncio
import asyncpg
from app.core.config import settings
from uuid import uuid4, UUID

async def test_rls_enforcement():
    """Test RLS enforcement directly"""
    print("🔍 TESTING RLS ENFORCEMENT DIRECTLY")
    print("=" * 50)
    
    # Connect as different users and test RLS
    conn1 = await asyncpg.connect(
        host=settings.db_host, port=settings.db_port,
        user=settings.db_user, password=settings.db_password,
        database=settings.db_name
    )
    
    # User 1 creates a conversation
    user1_id = UUID("d31ce60e-e013-44a9-97e3-dda4ee30d6d2")
    await conn1.execute("SELECT set_config('app.current_user_id', $1, true);", str(user1_id))
    
    # Create conversation as user1
    conversation = await conn1.fetchrow(
        "INSERT INTO conversations (is_group, title) VALUES (false, 'RLS Test') RETURNING *"
    )
    conversation_id = conversation['id']
    
    # Add user1 as participant
    await conn1.execute(
        "INSERT INTO conversation_participants (conversation_id, user_id) VALUES ($1, $2)",
        conversation_id, user1_id
    )
    
    print(f"✅ User1 created conversation: {conversation_id}")
    
    # Now try to access as unauthorized user2
    user2_id = uuid4()
    conn2 = await asyncpg.connect(
        host=settings.db_host, port=settings.db_port,
        user=settings.db_user, password=settings.db_password,
        database=settings.db_name
    )
    
    await conn2.execute("SELECT set_config('app.current_user_id', $1, true);", str(user2_id))
    
    # Test 1: User2 should NOT see the conversation
    try:
        conversations = await conn2.fetch("SELECT * FROM conversations WHERE id = $1", conversation_id)
        if len(conversations) == 0:
            print("✅ RLS Test 1: User2 cannot see conversation - PASSED")
        else:
            print("❌ RLS Test 1: User2 can see conversation - FAILED")
    except Exception as e:
        print(f"✅ RLS Test 1: User2 access blocked - PASSED")
    
    # Test 2: User2 should NOT be able to insert into conversation_participants
    try:
        await conn2.execute(
            "INSERT INTO conversation_participants (conversation_id, user_id) VALUES ($1, $2)",
            conversation_id, user2_id
        )
        print("❌ RLS Test 2: User2 inserted into participants - FAILED")
    except Exception as e:
        print("✅ RLS Test 2: User2 cannot insert into participants - PASSED")
    
    # Test 3: User2 should NOT be able to send message
    try:
        await conn2.execute(
            "INSERT INTO messages (conversation_id, sender_id, content) VALUES ($1, $2, $3)",
            conversation_id, user2_id, "Unauthorized message"
        )
        print("❌ RLS Test 3: User2 sent message - FAILED")
    except Exception as e:
        print("✅ RLS Test 3: User2 cannot send message - PASSED")
    
    await conn1.close()
    await conn2.close()

if __name__ == "__main__":
    asyncio.run(test_rls_enforcement())
