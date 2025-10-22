#!/usr/bin/env python3
"""
Phase 2 Integration Test - Messaging Schema & CRUD
"""
import asyncio
from app.crud.messages import messages_crud
from app.core.security import create_access_token
from uuid import uuid4, UUID
import asyncpg
from app.core.config import settings

async def test_phase2_integration():
    """Test complete Phase 2 integration"""
    print("🔍 PHASE 2 INTEGRATION TEST - MESSAGING")
    print("=" * 50)
    
    # Connect to database with user context
    conn = await asyncpg.connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database=settings.db_name
    )
    
    try:
        # Set user context for RLS
        test_user_id = "d31ce60e-e013-44a9-97e3-dda4ee30d6d2"
        await conn.execute("SELECT set_config('app.current_user_id', $1, true);", test_user_id)
        
        # 1. Test conversation creation
        conversation = await messages_crud.create_conversation(
            UUID(test_user_id),
            is_group=False,
            title="Test Conversation"
        )
        
        assert conversation is not None
        conversation_id = conversation['id']
        print("✅ Conversation creation working")
        
        # 2. Test message creation
        message = await messages_crud.create_message(
            conversation_id,
            UUID(test_user_id),
            "Hello, this is a test message!",
            "text"
        )
        
        assert message is not None
        assert message['content'] == "Hello, this is a test message!"
        print("✅ Message creation working")
        
        # 3. Test retrieving messages
        messages = await messages_crud.get_conversation_messages(conversation_id)
        assert len(messages) == 1
        assert messages[0]['content'] == "Hello, this is a test message!"
        print("✅ Message retrieval working")
        
        # 4. Test retrieving user conversations
        conversations = await messages_crud.get_user_conversations(UUID(test_user_id))
        assert len(conversations) >= 1
        print("✅ Conversation retrieval working")
        
        print("🎉 PHASE 2 INTEGRATION TEST COMPLETE - MESSAGING READY!")
        
    except Exception as e:
        print(f"❌ Phase 2 integration failed: {e}")
        raise
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(test_phase2_integration())
