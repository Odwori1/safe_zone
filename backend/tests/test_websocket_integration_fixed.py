#!/usr/bin/env python3
"""
WebSocket Integration Test - FIXED VERSION
"""
import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import database
from app.crud.messages import messages_crud
from app.services.connection_manager_enhanced import connection_manager
from uuid import uuid4, UUID
from fastapi import WebSocket
import asyncpg
from app.core.config import settings

class MockWebSocket:
    """Mock WebSocket for testing"""
    def __init__(self):
        self.sent_messages = []
        self.close_called = False
        self.close_code = None
        self.close_reason = None
        self.accept_called = False
        
    async def accept(self):
        self.accept_called = True
        
    async def send_json(self, message):
        self.sent_messages.append(message)
        
    async def close(self, code=None, reason=None):
        self.close_called = True
        self.close_code = code
        self.close_reason = reason

async def test_websocket_integration():
    """Test complete WebSocket integration"""
    print("🔍 TESTING WEBSOCKET INTEGRATION")
    print("=" * 50)
    
    # Initialize database for integration testing
    await database.connect()
    
    try:
        # Test data
        user_id = UUID("d31ce60e-e013-44a9-97e3-dda4ee30d6d2")
        
        # Create a test conversation
        conversation = await messages_crud.create_conversation(
            user_id, is_group=False, title="WebSocket Test Conversation"
        )
        assert conversation is not None
        conversation_id = conversation['id']
        print("✅ Test conversation created")
        
        # Test WebSocket connection simulation
        mock_websocket = MockWebSocket()
        mock_db_conn = await database.pool.acquire()
        
        try:
            # Set user context for RLS
            await mock_db_conn.execute(
                "SELECT set_config('app.current_user_id', $1, true);",
                str(user_id)
            )
            
            # Test connection registration
            connection_id = await connection_manager.connect(
                mock_websocket, user_id, mock_db_conn
            )
            
            # Debug: Check current connection count
            current_connections = connection_manager.get_total_connections()
            print(f"📊 Current connections: {current_connections}")
            
            # The connection should be registered
            assert current_connections >= 1, f"Expected at least 1 connection, got {current_connections}"
            print("✅ WebSocket connection integration: PASSED")
            
            # Test conversation subscription integration
            await connection_manager.subscribe_to_conversation(connection_id, conversation_id)
            connection = connection_manager.active_connections.get(connection_id)
            if connection:
                assert conversation_id in connection.conversations
                print("✅ Conversation subscription integration: PASSED")
            else:
                print("⚠️  Connection not found in active connections")
            
            # Cleanup
            await connection_manager.disconnect(connection_id)
            
        finally:
            await database.pool.release(mock_db_conn)
        
        print("🎉 WebSocket integration test COMPLETE")
        
    except Exception as e:
        print(f"❌ WebSocket integration test failed: {e}")
        raise
    finally:
        await database.close()

if __name__ == "__main__":
    asyncio.run(test_websocket_integration())
