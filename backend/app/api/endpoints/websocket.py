"""
WebSocket Endpoints for Real-time Messaging - Phase 3, Item 4
Following security-first blueprint with RLS protection
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from app.services.websocket_auth import websocket_auth
from app.services.connection_manager_enhanced import connection_manager
from app.crud.messages import messages_crud
from app.services.redis_service import redis_service
from app.database.database import database

logger = logging.getLogger("safe_zone.websocket")

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: Optional[str] = None):
    """
    Main WebSocket endpoint for real-time messaging
    Security: JWT authentication required, RLS enforced via dedicated connection
    """
    await websocket.accept()
    
    connection_id = None
    db_connection = None
    
    try:
        # 1. Authenticate WebSocket connection
        auth_result = await websocket_auth.authenticate_websocket(websocket, token)
        if not auth_result:
            return  # Connection already rejected by auth service

        user_id = auth_result["user_id"]
        
        # 2. Acquire dedicated database connection for this WebSocket
        db_connection = await database.pool.acquire()
        
        # 3. Set user context for RLS enforcement on this connection
        await db_connection.execute(
            "SELECT set_config('app.current_user_id', $1, true);",
            str(user_id)
        )
        
        # 4. Register connection with manager
        connection_id = await connection_manager.connect(websocket, user_id, db_connection)
        
        # 5. Send connection confirmation
        await websocket.send_json({
            "type": "connection.established",
            "connection_id": str(connection_id),
            "user_id": str(user_id)
        })
        
        logger.info(f"WebSocket connection {connection_id} established for user {user_id}")
        
        # 6. Main message handling loop
        await _handle_websocket_messages(websocket, connection_id, user_id, db_connection)
        
    except WebSocketDisconnect:
        logger.info(f"WebSocket connection {connection_id} disconnected normally")
    except Exception as e:
        logger.error(f"WebSocket error for connection {connection_id}: {e}")
        try:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        except:
            pass
    finally:
        # 7. Cleanup resources
        if connection_id:
            await connection_manager.disconnect(connection_id)
        if db_connection:
            await database.pool.release(db_connection)

async def _handle_websocket_messages(
    websocket: WebSocket, 
    connection_id: UUID, 
    user_id: UUID, 
    db_connection
):
    """
    Handle incoming WebSocket messages with security context
    """
    while True:
        try:
            # Receive message from client
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            logger.debug(f"Received WebSocket message type: {message_type} from user {user_id}")
            
            # Route message to appropriate handler
            if message_type == "message.send":
                await _handle_send_message(data, user_id, db_connection)
            elif message_type == "conversation.subscribe":
                await _handle_conversation_subscribe(data, connection_id, user_id, db_connection)
            elif message_type == "conversation.unsubscribe":
                await _handle_conversation_unsubscribe(data, connection_id)
            elif message_type == "auth.refresh":
                await _handle_auth_refresh(data, connection_id, user_id, db_connection)
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
            logger.error(f"Error handling WebSocket message: {e}")
            await websocket.send_json({
                "type": "error",
                "code": "MESSAGE_HANDLING_ERROR",
                "message": "Failed to process message"
            })

async def _handle_send_message(data: Dict[str, Any], user_id: UUID, db_connection):
    """
    Handle sending a new message with RLS enforcement
    """
    try:
        conversation_id = UUID(data.get("conversation_id"))
        content = data.get("content", "").strip()
        content_type = data.get("content_type", "text")
        
        if not content:
            return
        
        # Create message (RLS ensures user can only send to conversations they participate in)
        message = await messages_crud.create_message(
            conversation_id, user_id, content, content_type
        )
        
        if message:
            # Prepare message for delivery
            message_data = {
                "id": str(message["id"]),
                "conversation_id": str(conversation_id),
                "sender_id": str(user_id),
                "content": content,
                "content_type": content_type,
                "created_at": message["created_at"].isoformat(),
                "username": message.get("username")  # From joined query
            }
            
            # Broadcast to conversation subscribers via Redis
            await connection_manager.broadcast_to_conversation(
                conversation_id,
                {
                    "type": "message.new",
                    "data": message_data
                },
                exclude_user_id=user_id  # Don't send back to sender
            )
            
            logger.info(f"Message {message['id']} sent to conversation {conversation_id}")
        
    except Exception as e:
        logger.error(f"Error sending message: {e}")

async def _handle_conversation_subscribe(
    data: Dict[str, Any], 
    connection_id: UUID, 
    user_id: UUID, 
    db_connection
):
    """
    Handle subscription to conversation for real-time updates
    RLS ensures user can only subscribe to conversations they participate in
    """
    try:
        conversation_id = UUID(data.get("conversation_id"))
        
        # Verify user is participant (RLS will enforce this in subsequent queries)
        participants = await messages_crud.get_conversation_participants(conversation_id)
        is_participant = any(p["user_id"] == user_id for p in participants)
        
        if is_participant:
            await connection_manager.subscribe_to_conversation(connection_id, conversation_id)
            
            # Send subscription confirmation
            connection = connection_manager.active_connections.get(connection_id)
            if connection:
                await connection.websocket.send_json({
                    "type": "conversation.subscribed",
                    "conversation_id": str(conversation_id)
                })
        else:
            # User is not a participant in this conversation
            connection = connection_manager.active_connections.get(connection_id)
            if connection:
                await connection.websocket.send_json({
                    "type": "error",
                    "code": "NOT_PARTICIPANT",
                    "message": "Not a participant in this conversation"
                })
                
    except Exception as e:
        logger.error(f"Error subscribing to conversation: {e}")

async def _handle_conversation_unsubscribe(data: Dict[str, Any], connection_id: UUID):
    """Handle unsubscription from conversation"""
    try:
        conversation_id = UUID(data.get("conversation_id"))
        await connection_manager.unsubscribe_from_conversation(connection_id, conversation_id)
    except Exception as e:
        logger.error(f"Error unsubscribing from conversation: {e}")

async def _handle_auth_refresh(
    data: Dict[str, Any], 
    connection_id: UUID, 
    user_id: UUID, 
    db_connection
):
    """
    Handle token refresh for long-lived WebSocket connections
    Security: Re-authenticate and update user context
    """
    try:
        new_token = data.get("token")
        
        # Re-authenticate with new token
        from app.services.websocket_auth import websocket_auth
        
        # Create a mock websocket for silent authentication
        class SilentWebSocket:
            async def close(self, *args, **kwargs):
                pass  # Don't actually close during refresh
        
        auth_result = await websocket_auth.authenticate_websocket(
            SilentWebSocket(),
            new_token
        )
        
        if auth_result:
            new_user_id = auth_result["user_id"]
            
            # Update user context in database connection
            await db_connection.execute(
                "SELECT set_config('app.current_user_id', $1, true);",
                str(new_user_id)
            )
            
            # Send refresh confirmation
            connection = connection_manager.active_connections.get(connection_id)
            if connection:
                await connection.websocket.send_json({
                    "type": "auth.refreshed",
                    "user_id": str(new_user_id)
                })
                
            logger.info(f"WebSocket connection {connection_id} re-authenticated for user {new_user_id}")
        else:
            # Authentication failed
            connection = connection_manager.active_connections.get(connection_id)
            if connection:
                await connection.websocket.send_json({
                    "type": "error", 
                    "code": "AUTH_FAILED",
                    "message": "Token refresh failed"
                })
                
    except Exception as e:
        logger.error(f"Error during auth refresh: {e}")
