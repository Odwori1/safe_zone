#!/usr/bin/env python3
"""
Test Messages CRUD Operations - Fixed Version
"""
import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.crud.messages import messages_crud
from app.database.database import database
from uuid import uuid4, UUID
import asyncpg
from app.core.config import settings

async def test_messages_crud_operations():
    """Test all messages CRUD operations"""
    print("🔍 TESTING MESSAGES CRUD OPERATIONS - FIXED")
    print("=" * 50)
    
    # Initialize database connection
    await database.connect()
    
    try:
        # Connect to database with user context
        conn = await asyncpg.connect(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database=settings.db_name
        )
        
        # Set user context for RLS
        test_user_id = "d31ce60e-e013-44a9-97e3-dda4ee30d6d2"
        await conn.execute("SELECT set_config('app.current_user_id', $1, true);", test_user_id)
        
        # 1. Test conversation creation
        print("📝 Testing conversation creation...")
        conversation = await messages_crud.create_conversation(
            UUID(test_user_id),
            is_group=False,
            title="Test Direct Message"
        )
        assert conversation is not None
        conversation_id = conversation['id']
        print("✅ Conversation creation: PASSED")
        
        # 2. Test group conversation creation
        print("👥 Testing group conversation creation...")
        group_conversation = await messages_crud.create_conversation(
            UUID(test_user_id),
            is_group=True,
            title="Test Group Chat"
        )
        assert group_conversation is not None
        assert group_conversation['is_group'] == True
        print("✅ Group conversation creation: PASSED")
        
        # 3. Test message creation
        print("💬 Testing message creation...")
        message = await messages_crud.create_message(
            conversation_id,
            UUID(test_user_id),
            "Test message content",
            "text"
        )
        assert message is not None
        assert message['content'] == "Test message content"
        assert message['sender_id'] == UUID(test_user_id)
        print("✅ Message creation: PASSED")
        
        # 4. Test message retrieval
        print("📨 Testing message retrieval...")
        messages = await messages_crud.get_conversation_messages(conversation_id)
        assert len(messages) == 1
        assert messages[0]['content'] == "Test message content"
        print("✅ Message retrieval: PASSED")
        
        # 5. Test conversation retrieval
        print("📂 Testing conversation retrieval...")
        conversations = await messages_crud.get_user_conversations(UUID(test_user_id))
        assert len(conversations) >= 2  # Should have both conversations
        print("✅ Conversation retrieval: PASSED")
        
        # 6. Test participant retrieval
        print("👥 Testing participant retrieval...")
        participants = await messages_crud.get_conversation_participants(conversation_id)
        assert len(participants) >= 1
        print("✅ Participant retrieval: PASSED")
        
        # 7. Test soft delete
        print("🗑️ Testing message soft delete...")
        delete_success = await messages_crud.soft_delete_message(
            message['id'],
            UUID(test_user_id)
        )
        assert delete_success == True
        print("✅ Message soft delete: PASSED")
        
        # 8. Test moderation status update
        print("🛡️ Testing moderation status update...")
        moderation_success = await messages_crud.update_message_moderation_status(
            message['id'],
            "approved",
            True
        )
        assert moderation_success == True
        print("✅ Moderation status update: PASSED")
        
        print("🎉 ALL MESSAGES CRUD TESTS PASSED!")
        
    except Exception as e:
        print(f"❌ CRUD test failed: {e}")
        raise
    finally:
        if 'conn' in locals():
            await conn.close()
        await database.close()

if __name__ == "__main__":
    asyncio.run(test_messages_crud_operations())
