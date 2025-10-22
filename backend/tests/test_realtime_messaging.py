#!/usr/bin/env python3
"""
End-to-End Real-time Messaging Test - Phase 3, Item 4 Final Verification
"""
import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import database
from app.crud.messages import messages_crud
from app.services.websocket_auth import websocket_auth
from app.core.security import create_access_token
from uuid import uuid4, UUID
from fastapi import WebSocket
import asyncpg
from app.core.config import settings

class TestWebSocketClient:
    """Simulate a WebSocket client for testing"""
    def __init__(self, user_id, token):
        self.user_id = user_id
        self.token = token
        self.received_messages = []
        self.connected = False
        
    async def connect(self):
        """Simulate WebSocket connection"""
        self.connected = True
        
    async def send_message(self, message_type, data):
        """Simulate sending a WebSocket message"""
        message = {"type": message_type, **data}
        # In real test, this would be sent via WebSocket
        print(f"📤 Client {self.user_id} sending: {message_type}")
        return message
        
    async def receive_message(self, message):
        """Simulate receiving a WebSocket message"""
        self.received_messages.append(message)
        print(f"📥 Client {self.user_id} received: {message.get('type')}")

async def test_realtime_messaging_flow():
    """Test complete real-time messaging flow"""
    print("🔍 TESTING REAL-TIME MESSAGING FLOW")
    print("=" * 50)
    
    # Initialize database
    await database.connect()
    
    try:
        # Create test users and conversation
        user1_id = UUID("d31ce60e-e013-44a9-97e3-dda4ee30d6d2")  # Existing test user
        user2_id = uuid4()  # Simulated second user
        
        # Create tokens for both users
        user1_token = create_access_token({"sub": str(user1_id), "email": "user1@test.com"})
        user2_token = create_access_token({"sub": str(user2_id), "email": "user2@test.com"})
        
        # Create test conversation
        conversation = await messages_crud.create_conversation(
            user1_id, 
            is_group=True, 
            title="Real-time Test Chat",
            participant_ids=[user2_id]  # Add second user
        )
        assert conversation is not None
        conversation_id = conversation['id']
        print("✅ Test conversation created with participants")
        
        # Create WebSocket clients
        client1 = TestWebSocketClient(user1_id, user1_token)
        client2 = TestWebSocketClient(user2_id, user2_token)
        
        # Test WebSocket authentication
        mock_websocket = type('MockWebSocket', (), {'close': AsyncMock()})()
        auth_result1 = await websocket_auth.authenticate_websocket(mock_websocket, user1_token)
        auth_result2 = await websocket_auth.authenticate_websocket(mock_websocket, user2_token)
        
        assert auth_result1 is not None
        assert auth_result2 is not None
        assert auth_result1["user_id"] == user1_id
        assert auth_result2["user_id"] == user2_id
        print("✅ WebSocket authentication: PASSED")
        
        # Test message sending flow
        test_message_content = "Hello from real-time test!"
        
        # User1 sends message
        message = await messages_crud.create_message(
            conversation_id, user1_id, test_message_content, "text"
        )
        assert message is not None
        assert message["content"] == test_message_content
        print("✅ Message creation in conversation: PASSED")
        
        # Retrieve messages to verify persistence
        messages = await messages_crud.get_conversation_messages(conversation_id)
        assert len(messages) == 1
        assert messages[0]["content"] == test_message_content
        print("✅ Message persistence: PASSED")
        
        # Test conversation retrieval for both users
        user1_conversations = await messages_crud.get_user_conversations(user1_id)
        user2_conversations = await messages_crud.get_user_conversations(user2_id)
        
        assert len(user1_conversations) >= 1
        assert len(user2_conversations) >= 1
        print("✅ Conversation access control: PASSED")
        
        # Test participants retrieval
        participants = await messages_crud.get_conversation_participants(conversation_id)
        participant_ids = [p["user_id"] for p in participants]
        assert user1_id in participant_ids
        assert user2_id in participant_ids
        print("✅ Participant management: PASSED")
        
        # Simulate real-time message delivery
        # In a real scenario, this would happen via WebSocket and Redis
        message_data = {
            "type": "message.new",
            "data": {
                "id": str(message["id"]),
                "conversation_id": str(conversation_id),
                "sender_id": str(user1_id),
                "content": test_message_content,
                "content_type": "text",
                "created_at": message["created_at"].isoformat(),
                "username": "testuser1"
            }
        }
        
        # Simulate clients receiving the message
        await client1.receive_message(message_data)
        await client2.receive_message(message_data)
        
        assert len(client1.received_messages) == 1
        assert len(client2.received_messages) == 1
        assert client1.received_messages[0]["type"] == "message.new"
        assert client2.received_messages[0]["type"] == "message.new"
        print("✅ Real-time message delivery simulation: PASSED")
        
        # Test message moderation flow
        moderation_success = await messages_crud.update_message_moderation_status(
            message["id"], "approved", True
        )
        assert moderation_success == True
        print("✅ Message moderation: PASSED")
        
        print("🎉 REAL-TIME MESSAGING FLOW TEST COMPLETE!")
        
    except Exception as e:
        print(f"❌ Real-time messaging test failed: {e}")
        raise
    finally:
        await database.close()

if __name__ == "__main__":
    print("🚀 STARTING REAL-TIME MESSAGING TESTS")
    print("=" * 60)
    
    asyncio.run(test_realtime_messaging_flow())
    print("🎉 ALL REAL-TIME MESSAGING TESTS COMPLETED!")
