#!/usr/bin/env python3
"""
Phase 1 Integration Test - WebSocket Security Foundation
"""
import asyncio
from app.services.websocket_auth import websocket_auth
from app.services.connection_manager import connection_manager
from app.core.security import create_access_token
from fastapi import WebSocket
from unittest.mock import AsyncMock
import asyncpg

class MockWebSocket:
    def __init__(self):
        self.sent_messages = []
        self.close_called = False
        self.close_code = None
        self.close_reason = None
        
    async def send_json(self, message):
        self.sent_messages.append(message)
        
    async def close(self, code=None, reason=None):
        self.close_called = True
        self.close_code = code
        self.close_reason = reason
        
    async def accept(self):
        pass

async def test_phase1_integration():
    """Test complete Phase 1 integration"""
    print("🔍 PHASE 1 INTEGRATION TEST")
    print("=" * 50)
    
    # Test data
    user_id = "d31ce60e-e013-44a9-97e3-dda4ee30d6d2"
    token = create_access_token({"sub": user_id, "email": "test@example.com"})
    
    # 1. Test authentication
    mock_websocket = MockWebSocket()
    auth_result = await websocket_auth.authenticate_websocket(mock_websocket, token)
    
    assert auth_result is not None
    assert str(auth_result["user_id"]) == user_id
    print("✅ Authentication service integrated")
    
    # 2. Test connection management
    mock_db_conn = AsyncMock(spec=asyncpg.Connection)
    connection_id = await connection_manager.connect(
        mock_websocket, auth_result["user_id"], mock_db_conn
    )
    
    assert connection_manager.get_total_connections() == 1
    assert connection_manager.get_user_connection_count(auth_result["user_id"]) == 1
    print("✅ Connection manager integrated")
    
    # 3. Test message delivery
    test_message = {"type": "integration_test", "status": "success"}
    await connection_manager.send_personal_message(auth_result["user_id"], test_message)
    
    assert len(mock_websocket.sent_messages) == 1
    assert mock_websocket.sent_messages[0] == test_message
    print("✅ Message delivery integrated")
    
    # 4. Test cleanup
    await connection_manager.disconnect(connection_id)
    assert connection_manager.get_total_connections() == 0
    print("✅ Resource cleanup integrated")
    
    print("🎉 PHASE 1 INTEGRATION TEST COMPLETE - ALL SYSTEMS GO!")

if __name__ == "__main__":
    asyncio.run(test_phase1_integration())
