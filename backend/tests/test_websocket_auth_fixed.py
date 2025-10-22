#!/usr/bin/env python3
"""
Test WebSocket Authentication Service - Fixed Version
"""
import asyncio
from app.services.websocket_auth import websocket_auth
from app.core.security import create_access_token
from fastapi import WebSocket
from uuid import UUID

class MockWebSocket:
    """Mock WebSocket for testing"""
    def __init__(self):
        self.close_called = False
        self.close_code = None
        self.close_reason = None
        
    async def close(self, code=None, reason=None):
        self.close_called = True
        self.close_code = code
        self.close_reason = reason

async def test_websocket_auth_success():
    """Test successful WebSocket authentication"""
    print("🔍 TESTING WEBSOCKET AUTHENTICATION - SUCCESS")
    print("=" * 50)
    
    # Create valid JWT token
    token = create_access_token({"sub": "d31ce60e-e013-44a9-97e3-dda4ee30d6d2", "email": "test@example.com"})
    
    mock_websocket = MockWebSocket()
    
    # Test authentication
    result = await websocket_auth.authenticate_websocket(mock_websocket, token)
    
    assert result is not None
    assert isinstance(result["user_id"], UUID)
    assert str(result["user_id"]) == "d31ce60e-e013-44a9-97e3-dda4ee30d6d2"  # FIXED: Compare string representation
    assert not mock_websocket.close_called
    print("✅ Successful authentication test PASSED")

async def test_websocket_auth_no_token():
    """Test authentication failure with no token"""
    print("🔍 TESTING WEBSOCKET AUTHENTICATION - NO TOKEN")
    print("=" * 50)
    
    mock_websocket = MockWebSocket()
    
    result = await websocket_auth.authenticate_websocket(mock_websocket, None)
    
    assert result is None
    assert mock_websocket.close_called
    assert "No authentication" in mock_websocket.close_reason
    print("✅ No token rejection test PASSED")

async def test_websocket_auth_invalid_token():
    """Test authentication failure with invalid token"""
    print("🔍 TESTING WEBSOCKET AUTHENTICATION - INVALID TOKEN")
    print("=" * 50)
    
    mock_websocket = MockWebSocket()
    
    result = await websocket_auth.authenticate_websocket(mock_websocket, "invalid_token")
    
    assert result is None
    assert mock_websocket.close_called
    print("✅ Invalid token rejection test PASSED")

if __name__ == "__main__":
    asyncio.run(test_websocket_auth_success())
    asyncio.run(test_websocket_auth_no_token())
    asyncio.run(test_websocket_auth_invalid_token())
    print("🎉 WebSocket authentication tests COMPLETE")
