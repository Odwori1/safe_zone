"""
Enhanced WebSocket Endpoints with Additional Real-time Features
"""
import asyncio
import logging
from typing import Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from app.services.websocket_auth import websocket_auth
from app.services.connection_manager_enhanced import connection_manager
from app.services.realtime_features import realtime_features
from app.crud.messages import messages_crud
from app.database.database import database

logger = logging.getLogger("safe_zone.websocket_enhanced")

router = APIRouter()

@router.websocket("/ws/enhanced")
async def enhanced_websocket_endpoint(websocket: WebSocket, token: Optional[str] = None):
    """
    Enhanced WebSocket endpoint with additional real-time features
    """
    await websocket.accept()
    
    connection_id = None
    db_connection = None
    
    try:
        # 1. Authenticate WebSocket connection
        auth_result = await websocket_auth.authenticate_websocket(websocket, token)
        if not auth_result:
            return

        user_id = auth_result["user_id"]
        
        # 2. Acquire dedicated database connection
        db_connection = await database.pool.acquire()
        await db_connection.execute(
            "SELECT set_config('app.current_user_id', $1, true);",
            str(user_id)
        )
        
        # 3. Register connection and set user online
        connection_id = await connection_manager.connect(websocket, user_id, db_connection)
        await realtime_features.handle_user_online(user_id)
        
        # 4. Send enhanced connection confirmation
        await websocket.send_json({
            "type": "connection.enhanced",
            "connection_id": str(connection_id),
            "user_id": str(user_id),
            "features": ["typing_indicators", "read_receipts", "online_status"]
        })
        
        logger.info(f"Enhanced WebSocket connection {connection_id} for user {user_id}")
        
        # 5. Enhanced message handling loop
        await _handle_enhanced_websocket_messages(websocket, connection_id, user_id, db_connection)
        
    except WebSocketDisconnect:
        logger.info(f"Enhanced WebSocket connection {connection_id} disconnected")
    except Exception as e:
        logger.error(f"Enhanced WebSocket error: {e}")
        try:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        except:
            pass
    finally:
        # 6. Cleanup resources and set user offline
        if connection_id:
            await connection_manager.disconnect(connection_id)
        if db_connection:
            await database.pool.release(db_connection)
        if 'user_id' in locals():
            await realtime_features.handle_user_offline(user_id)

async def _handle_enhanced_websocket_messages(
    websocket: WebSocket, 
    connection_id: UUID, 
    user_id: UUID, 
    db_connection
):
    """
    Handle enhanced WebSocket messages with additional features
    """
    while True:
        try:
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            # Enhanced message routing
            if message_type == "message.send":
                await _handle_send_message(data, user_id, db_connection)
            elif message_type == "typing.start":
                await _handle_typing_start(data, user_id)
            elif message_type == "typing.stop":
                await _handle_typing_stop(data, user_id)
            elif message_type == "message.read":
                await _handle_message_read(data, user_id)
            elif message_type == "online.status":
                await _handle_online_status(data, user_id)
            elif message_type == "conversation.subscribe":
                await _handle_conversation_subscribe(data, connection_id, user_id, db_connection)
            elif message_type == "ping":
                await websocket.send_json({"type": "pong"})
            else:
                await websocket.send_json({
                    "type": "error",
                    "code": "UNKNOWN_MESSAGE_TYPE",
                    "message": f"Unknown message type: {message_type}"
                })
                
        except WebSocketDisconnect:
            raise
        except Exception as e:
            logger.error(f"Error handling enhanced WebSocket message: {e}")

async def _handle_typing_start(data: Dict[str, Any], user_id: UUID):
    """Handle typing start indicator"""
    try:
        conversation_id = UUID(data.get("conversation_id"))
        await realtime_features.handle_typing_start(conversation_id, user_id)
    except Exception as e:
        logger.error(f"Error handling typing start: {e}")

async def _handle_typing_stop(data: Dict[str, Any], user_id: UUID):
    """Handle typing stop indicator"""
    try:
        conversation_id = UUID(data.get("conversation_id"))
        await realtime_features.handle_typing_stop(conversation_id, user_id)
    except Exception as e:
        logger.error(f"Error handling typing stop: {e}")

async def _handle_message_read(data: Dict[str, Any], user_id: UUID):
    """Handle read receipt"""
    try:
        message_id = UUID(data.get("message_id"))
        conversation_id = UUID(data.get("conversation_id"))
        await realtime_features.handle_read_receipt(message_id, user_id, conversation_id)
    except Exception as e:
        logger.error(f"Error handling message read: {e}")

async def _handle_online_status(data: Dict[str, Any], user_id: UUID):
    """Handle online status request"""
    try:
        requested_user_ids = [UUID(uid) for uid in data.get("user_ids", [])]
        online_status = await realtime_features.get_online_users(requested_user_ids)
        
        # Send online status response
        connection = connection_manager.active_connections.get(
            next(iter(connection_manager.user_connections.get(user_id, [])), None)
        )
        if connection:
            await connection.websocket.send_json({
                "type": "online.status.response",
                "online_status": {
                    str(uid): status for uid, status in online_status.items()
                }
            })
    except Exception as e:
        logger.error(f"Error handling online status: {e}")

# Reuse existing message handling functions from websocket.py
from app.api.endpoints.websocket import (
    _handle_send_message,
    _handle_conversation_subscribe,
    _handle_conversation_unsubscribe,
    _handle_auth_refresh
)
