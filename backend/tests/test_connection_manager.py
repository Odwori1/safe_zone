#!/usr/bin/env python3
"""
Test Connection Manager - Phase 1, Step 1.3 Verification
"""
import asyncio
from uuid import UUID, uuid4
from app.services.connection_manager import ConnectionManager, Connection
from fastapi import WebSocket
from unittest.mock import AsyncMock
import asyncpg

class MockWebSocket:
    def __init__(self):
        self.sent_messages = []
        self.close_called = False
        
    async def send_json(self, message):
        self.sent_messages.append(message)
        
    async def close(self):
        self.close_called = True

async def test_connection_manager_lifecycle():
    """Test connection lifecycle management"""
    print("🔍 TESTING CONNECTION MANAGER LIFECYCLE")
    print("=" * 50)
    
    manager = ConnectionManager()
    mock_websocket = MockWebSocket()
    mock_db_conn = AsyncMock(spec=asyncpg.Connection)
    user_id = uuid4()
    
    # Test connection
    connection_id = await manager.connect(mock_websocket, user_id, mock_db_conn)
    assert isinstance(connection_id, UUID)
    assert manager.get_total_connections() == 1
    assert manager.get_user_connection_count(user_id) == 1
    print("✅ Connection creation test PASSED")
    
    # Test message sending
    test_message = {"type": "test", "data": "hello"}
    await manager.send_personal_message(user_id, test_message)
    assert len(mock_websocket.sent_messages) == 1
    assert mock_websocket.sent_messages[0] == test_message
    print("✅ Message sending test PASSED")
    
    # Test disconnection
    await manager.disconnect(connection_id)
    assert manager.get_total_connections() == 0
    assert manager.get_user_connection_count(user_id) == 0
    print("✅ Connection cleanup test PASSED")

async def test_multiple_connections_same_user():
    """Test multiple connections for same user"""
    print("🔍 TESTING MULTIPLE CONNECTIONS PER USER")
    print("=" * 50)
    
    manager = ConnectionManager()
    user_id = uuid4()
    
    # Create multiple connections for same user
    for i in range(3):
        mock_websocket = MockWebSocket()
        mock_db_conn = AsyncMock(spec=asyncpg.Connection)
        await manager.connect(mock_websocket, user_id, mock_db_conn)
    
    assert manager.get_total_connections() == 3
    assert manager.get_user_connection_count(user_id) == 3
    print("✅ Multiple connections test PASSED")

if __name__ == "__main__":
    asyncio.run(test_connection_manager_lifecycle())
    asyncio.run(test_multiple_connections_same_user())
    print("🎉 Connection manager tests COMPLETE")
