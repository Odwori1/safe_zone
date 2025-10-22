"""
Secure Live Audio Rooms Endpoints for Phase 3, Item 5
Following EXACT same patterns as websocket.py and files.py
"""

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from typing import List, Optional
from uuid import UUID
import json
import logging

from app.schemas.live_audio_rooms import (
    LiveAudioRoomCreate, LiveAudioRoom, LiveAudioRoomUpdate,
    RoomParticipantJoin, WebRTCOffer, WebRTCAnswer, ICECandidate,
    RoomModerationAction, UserPresenceUpdate
)
from app.crud.live_audio_rooms import live_audio_rooms_crud
from app.services.audio_room_manager import audio_room_manager
from app.services.websocket_auth import websocket_auth
from app.core.security import get_current_user
from app.schemas.user import User
from app.database.database import database

router = APIRouter()
logger = logging.getLogger(__name__)

# REST API Endpoints - FOLLOWING EXACT SAME PATTERNS AS FILES.PY

@router.post("/rooms", response_model=LiveAudioRoom)
async def create_room(
    room_data: LiveAudioRoomCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new live audio room
    SECURITY: RLS ensures user can only create their own rooms
    """
    try:
        room = await live_audio_rooms_crud.create_room(room_data.dict(), current_user.id)
        if not room:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create room"
            )
        return room
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating room: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create room"
        )

@router.get("/rooms", response_model=List[LiveAudioRoom])
async def get_active_rooms(
    room_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """
    Get all active audio rooms user can access
    SECURITY: RLS ensures user can only see rooms they have permission for
    """
    try:
        rooms = await live_audio_rooms_crud.get_active_rooms(room_type, limit, offset)
        return rooms
    except Exception as e:
        logger.error(f"Error fetching rooms: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch rooms"
        )

@router.get("/rooms/{room_id}", response_model=LiveAudioRoom)
async def get_room(
    room_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Get specific room details
    SECURITY: RLS ensures user can only access rooms they have permission for
    """
    try:
        room = await live_audio_rooms_crud.get_room(room_id, current_user.id)
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room not found or access denied"
            )
        return room
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching room: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch room"
        )

@router.post("/rooms/{room_id}/join")
async def join_room(
    room_id: UUID,
    join_data: RoomParticipantJoin,
    current_user: User = Depends(get_current_user)
):
    """
    Join a live audio room
    SECURITY: RLS ensures user can only join rooms they have access to
    """
    try:
        participant = await live_audio_rooms_crud.join_room(
            room_id, current_user.id, join_data.role
        )
        
        if not participant:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot join room (not found, full, or no access)"
            )
            
        return {
            "message": "Joined room successfully", 
            "participant": {
                "id": participant["id"],
                "role": participant["role"],
                "joined_at": participant["joined_at"].isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error joining room: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to join room"
        )

@router.post("/rooms/{room_id}/leave")
async def leave_room(
    room_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Leave a live audio room
    SECURITY: RLS ensures user can only leave their own participation
    """
    try:
        success = await live_audio_rooms_crud.leave_room(room_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Not in room or already left"
            )
        return {"message": "Left room successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error leaving room: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to leave room"
        )

@router.get("/rooms/{room_id}/participants")
async def get_room_participants(
    room_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Get current participants in a room
    SECURITY: RLS ensures user can only access rooms they participate in
    """
    try:
        participants = await live_audio_rooms_crud.get_room_participants(room_id, current_user.id)
        return {
            "room_id": str(room_id),
            "participants": [
                {
                    "id": str(p["id"]),
                    "user_id": str(p["user_id"]),
                    "username": p["username"],
                    "role": p["role"],
                    "joined_at": p["joined_at"].isoformat(),
                    "last_active_at": p["last_active_at"].isoformat()
                }
                for p in participants
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching participants: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch participants"
        )

# WebSocket Endpoint for Live Audio Rooms - FOLLOWING EXACT SAME PATTERN AS WEBSOCKET.PY

@router.websocket("/audio/{room_id}/ws")
async def audio_room_websocket(websocket: WebSocket, room_id: str, token: str = None):
    """
    WebSocket endpoint for live audio room communication
    SECURITY: JWT authentication required, RLS enforced via dedicated connection
    """
    await websocket.accept()

    connection_id = None
    db_connection = None

    try:
        # 1. AUTHENTICATE WEBSOCKET CONNECTION - EXACT SAME PATTERN
        auth_result = await websocket_auth.authenticate_websocket(websocket, token)
        if not auth_result:
            return  # Connection already rejected by auth service

        user_id = auth_result["user_id"]
        room_uuid = UUID(room_id)

        # 2. ACQUIRE DEDICATED DATABASE CONNECTION - EXACT SAME PATTERN
        db_connection = await database.pool.acquire()

        # 3. SET USER CONTEXT FOR RLS ENFORCEMENT - EXACT SAME PATTERN
        await db_connection.execute(
            "SELECT set_config('app.current_user_id', $1, true);",
            str(user_id)
        )

        # 4. VERIFY USER CAN ACCESS ROOM (RLS ENFORCED)
        room = await live_audio_rooms_crud.get_room(room_uuid, user_id)
        if not room:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Room access denied")
            return

        # 5. JOIN ROOM IN DATABASE (RLS ENFORCED)
        participant = await live_audio_rooms_crud.join_room(room_uuid, user_id)
        if not participant:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Cannot join room")
            return

        # 6. REGISTER CONNECTION WITH AUDIO ROOM MANAGER
        connection_id = await audio_room_manager.connect(
            websocket, user_id, db_connection, room_uuid
        )

        # 7. NOTIFY ROOM THAT USER JOINED
        await audio_room_manager.handle_user_joined(room_uuid, {
            "user_id": str(user_id),
            "username": auth_result.get("email", "Unknown").split('@')[0],
            "connection_id": str(connection_id),
            "role": participant["role"]
        })

        # 8. SEND CONNECTION CONFIRMATION
        await websocket.send_json({
            "type": "connection.established",
            "connection_id": str(connection_id),
            "user_id": str(user_id),
            "room_id": room_id,
            "role": participant["role"]
        })

        logger.info(f"Audio room WebSocket connection {connection_id} established for user {user_id} in room {room_id}")

        # 9. MAIN MESSAGE HANDLING LOOP - EXACT SAME PATTERN
        await _handle_audio_room_messages(websocket, connection_id, user_id, room_uuid, db_connection)

    except WebSocketDisconnect:
        logger.info(f"Audio room WebSocket connection {connection_id} disconnected normally")
    except Exception as e:
        logger.error(f"Audio room WebSocket error for connection {connection_id}: {e}")
        try:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        except:
            pass
    finally:
        # 10. CLEANUP RESOURCES - EXACT SAME PATTERN
        if connection_id:
            # Notify room that user left
            if 'room_uuid' in locals() and 'user_id' in locals():
                try:
                    await live_audio_rooms_crud.leave_room(room_uuid, user_id)
                    await audio_room_manager.handle_user_left(room_uuid, {
                        "user_id": str(user_id),
                        "connection_id": str(connection_id)
                    })
                except Exception as e:
                    logger.error(f"Cleanup error: {e}")
            
            await audio_room_manager.disconnect(connection_id)
        
        if db_connection:
            await database.pool.release(db_connection)

async def _handle_audio_room_messages(
    websocket: WebSocket,
    connection_id: UUID,
    user_id: UUID,
    room_id: UUID,
    db_connection
):
    """
    Handle incoming audio room WebSocket messages with security context
    EXACT SAME PATTERN AS _handle_websocket_messages
    """
    while True:
        try:
            # Receive message from client
            data = await websocket.receive_json()
            message_type = data.get("type")

            logger.debug(f"Received audio room message type: {message_type} from user {user_id}")

            # Route message to appropriate handler
            if message_type == "webrtc.offer":
                await _handle_webrtc_offer(data, connection_id, user_id, room_id)
            elif message_type == "webrtc.answer":
                await _handle_webrtc_answer(data, connection_id, user_id, room_id)
            elif message_type == "ice.candidate":
                await _handle_ice_candidate(data, connection_id, user_id, room_id)
            elif message_type == "user.presence":
                await _handle_user_presence(data, connection_id, user_id, room_id)
            elif message_type == "room.moderation":
                await _handle_room_moderation(data, connection_id, user_id, room_id, db_connection)
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
            logger.error(f"Error handling audio room message: {e}")
            await websocket.send_json({
                "type": "error",
                "code": "MESSAGE_HANDLING_ERROR",
                "message": "Failed to process message"
            })

async def _handle_webrtc_offer(data: dict, connection_id: UUID, user_id: UUID, room_id: UUID):
    """Handle WebRTC offer"""
    try:
        offer_data = WebRTCOffer(**data)
        await audio_room_manager.handle_webrtc_offer(
            connection_id, offer_data.target_user_id, offer_data.offer
        )
    except Exception as e:
        logger.error(f"Error handling WebRTC offer: {e}")

async def _handle_webrtc_answer(data: dict, connection_id: UUID, user_id: UUID, room_id: UUID):
    """Handle WebRTC answer"""
    try:
        answer_data = WebRTCAnswer(**data)
        await audio_room_manager.handle_webrtc_answer(
            connection_id, answer_data.target_user_id, answer_data.answer
        )
    except Exception as e:
        logger.error(f"Error handling WebRTC answer: {e}")

async def _handle_ice_candidate(data: dict, connection_id: UUID, user_id: UUID, room_id: UUID):
    """Handle ICE candidate"""
    try:
        candidate_data = ICECandidate(**data)
        await audio_room_manager.handle_ice_candidate(
            connection_id, candidate_data.target_user_id, candidate_data.candidate
        )
    except Exception as e:
        logger.error(f"Error handling ICE candidate: {e}")

async def _handle_user_presence(data: dict, connection_id: UUID, user_id: UUID, room_id: UUID):
    """Handle user presence updates"""
    try:
        presence_data = UserPresenceUpdate(**data)
        
        if presence_data.is_speaking is not None:
            await audio_room_manager.handle_user_speaking(
                connection_id, presence_data.is_speaking
            )
            
        # TODO: Handle audio/video enabled status
        # This would update connection state and broadcast to room
        
    except Exception as e:
        logger.error(f"Error handling user presence: {e}")

async def _handle_room_moderation(data: dict, connection_id: UUID, user_id: UUID, room_id: UUID, db_connection):
    """Handle room moderation actions"""
    try:
        moderation_data = RoomModerationAction(**data)
        
        # Verify user has moderation privileges (RLS will enforce in CRUD)
        action = await live_audio_rooms_crud.create_moderation_action(
            room_id, moderation_data.dict(), user_id
        )
        
        if action:
            # Broadcast moderation action to room
            await audio_room_manager.broadcast_to_room(room_id, {
                "type": "room.moderation",
                "data": {
                    "action_type": moderation_data.action_type,
                    "target_user_id": str(moderation_data.target_user_id),
                    "moderator_id": str(user_id),
                    "reason": moderation_data.reason
                }
            })
            
    except Exception as e:
        logger.error(f"Error handling room moderation: {e}")
