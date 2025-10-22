#!/usr/bin/env python3
"""
Phase 2 Integration Test - Fixed Version with Database Initialization
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

async def test_phase2_integration():
    """Test complete Phase 2 integration"""
    print("🔍 PHASE 2 INTEGRATION TEST - MESSAGING")
    print("=" * 50)
    
    # Initialize database connection
    await database.connect()
    
    try:
        # Connect to database with user context for direct testing
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
            title="Test Conversation"
        )
        
        assert conversation is not None
        conversation_id = conversation['id']
        print(f"✅ Conversation created: {conversation_id}")
        
        # 2. Test message creation
        print("💬 Testing message creation...")
        message = await messages_crud.create_message(
            conversation_id,
            UUID(test_user_id),
            "Hello, this is a test message!",
            "text"
        )
        
        assert message is not None
        assert message['content'] == "Hello, this is a test message!"
        print(f"✅ Message created: {message['id']}")
        
        # 3. Test retrieving messages
        print("📨 Testing message retrieval...")
        messages = await messages_crud.get_conversation_messages(conversation_id)
        assert len(messages) == 1
        assert messages[0]['content'] == "Hello, this is a test message!"
        print("✅ Message retrieval working")
        
        # 4. Test retrieving user conversations
        print("📂 Testing conversation retrieval...")
        conversations = await messages_crud.get_user_conversations(UUID(test_user_id))
        assert len(conversations) >= 1
        print(f"✅ Found {len(conversations)} conversations")
        
        # 5. Test conversation participants
        print("👥 Testing participant retrieval...")
        participants = await messages_crud.get_conversation_participants(conversation_id)
        assert len(participants) >= 1
        print(f"✅ Found {len(participants)} participants")
        
        print("🎉 PHASE 2 INTEGRATION TEST COMPLETE - MESSAGING READY!")
        
    except Exception as e:
        print(f"❌ Phase 2 integration failed: {e}")
        raise
    finally:
        if 'conn' in locals():
            await conn.close()
        await database.close()

if __name__ == "__main__":
    asyncio.run(test_phase2_integration())
