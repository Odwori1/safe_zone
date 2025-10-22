"""
Audio Room Manager for Live Audio Rooms - Phase 3, Item 5
Following EXACT same patterns as connection_manager_enhanced.py
"""

import asyncio
import logging
from typing import Dict, List, Optional, Set
from uuid import UUID, uuid4
from fastapi import WebSocket
import asyncpg

from app.services.redis_service import redis_service
from app.database.database import database

logger = logging.getLogger("safe_zone.audio_room_manager")

class AudioRoomConnection:
    """
    Represents an active WebSocket connection for audio rooms
    FOLLOWING EXACT SAME PATTERN AS Connection class
    """
    def __init__(
        self,
        websocket: WebSocket,
        user_id: UUID,
        db_connection: asyncpg.Connection,
        connection_id: UUID,
        room_id: UUID
    ):
        self.websocket = websocket
        self.user_id = user_id
        self.db_connection = db_connection
        self.connection_id = connection_id
        self.room_id = room_id
        self.authenticated_at = asyncio.get_event_loop().time()
        self.is_speaking: bool = False
        self.audio_enabled: bool = True

class AudioRoomManager:
    """
    Manages active audio room WebSocket connections
    FOLLOWING EXACT SAME PATTERN AS ConnectionManager
    """
    def __init__(self):
        self.active_connections: Dict[UUID, AudioRoomConnection] = {}
        self.room_connections: Dict[UUID, Set[UUID]] = {}  # room_id -> set of connection_ids
        self.user_connections: Dict[UUID, List[UUID]] = {}  # user_id -> list of connection_ids
        self._lock = asyncio.Lock()
        self._redis_initialized = False

    async def initialize_redis(self):
        """Initialize Redis connection - EXACT SAME PATTERN"""
        if not self._redis_initialized:
            await redis_service.connect()
            asyncio.create_task(self._subscribe_to_audio_rooms())
            self._redis_initialized = True

    async def _subscribe_to_audio_rooms(self):
        """Subscribe to audio room channels for cross-instance delivery"""
        try:
            await redis_service.subscribe_to_channel(
                "audio_room:*",
                self._handle_redis_message
            )
        except Exception as e:
            logger.error(f"Failed to subscribe to Redis audio rooms: {e}")

    async def _handle_redis_message(self, message_data: dict):
        """Handle incoming Redis messages for audio rooms"""
        try:
            room_id = message_data.get('room_id')
            if not room_id:
                return

            if isinstance(room_id, str):
                room_id = UUID(room_id)

            # Deliver to all connections in the room
            await self._deliver_to_room_subscribers(room_id, message_data)

        except Exception as e:
            logger.error(f"Error handling Redis audio room message: {e}")

    async def _deliver_to_room_subscribers(self, room_id: UUID, message: dict):
        """Deliver message to all connections in a room"""
        async with self._lock:
            if room_id not in self.room_connections:
                return

            connection_ids = self.room_connections[room_id].copy()

        # Deliver to each connection
        for connection_id in connection_ids:
            await self.send_personal_message(connection_id, message)

    async def connect(
        self,
        websocket: WebSocket,
        user_id: UUID,
        db_connection: asyncpg.Connection,
        room_id: UUID
    ) -> UUID:
        """
        Add new secure audio room WebSocket connection
        EXACT SAME PATTERN AS connection_manager.connect()
        """
        connection_id = uuid4()

        async with self._lock:
            connection = AudioRoomConnection(websocket, user_id, db_connection, connection_id, room_id)
            self.active_connections[connection_id] = connection

            # Track room connections
            if room_id not in self.room_connections:
                self.room_connections[room_id] = set()
            self.room_connections[room_id].add(connection_id)

            # Track user connections
            if user_id not in self.user_connections:
                self.user_connections[user_id] = []
            self.user_connections[user_id].append(connection_id)

        logger.info(f"Audio room connection established: {connection_id} for user {user_id} in room {room_id}")
        return connection_id

    async def disconnect(self, connection_id: UUID):
        """
        Remove audio room WebSocket connection and cleanup
        EXACT SAME PATTERN AS connection_manager.disconnect()
        """
        async with self._lock:
            if connection_id in self.active_connections:
                connection = self.active_connections[connection_id]

                # Remove from room tracking
                if connection.room_id in self.room_connections:
                    self.room_connections[connection.room_id].discard(connection_id)
                    if not self.room_connections[connection.room_id]:
                        del self.room_connections[connection.room_id]

                # Remove from user tracking
                if connection.user_id in self.user_connections:
                    user_conns = self.user_connections[connection.user_id]
                    if connection_id in user_conns:
                        user_conns.remove(connection_id)
                    if not user_conns:
                        del self.user_connections[connection.user_id]

                # Remove from active connections
                del self.active_connections[connection_id]

                logger.info(f"Audio room connection removed: {connection_id}")

    async def send_personal_message(self, connection_id: UUID, message: dict):
        """
        Send message to specific connection
        EXACT SAME PATTERN
        """
        connection = self.active_connections.get(connection_id)
        if connection:
            try:
                await connection.websocket.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send message to {connection_id}: {e}")
                await self.disconnect(connection_id)

    async def broadcast_to_room(
        self,
        room_id: UUID,
        message: dict,
        exclude_connection: Optional[UUID] = None,
        exclude_user: Optional[UUID] = None
    ):
        """
        Send message to all connections in a room
        EXACT SAME PATTERN AS connection_manager.broadcast_to_conversation()
        """
        # Publish to Redis for cross-instance delivery
        redis_message = {
            **message,
            "room_id": str(room_id),
            "timestamp": asyncio.get_event_loop().time()
        }
        
        if exclude_connection:
            redis_message["exclude_connection"] = str(exclude_connection)
        if exclude_user:
            redis_message["exclude_user"] = str(exclude_user)

        await redis_service.publish_message(f"audio_room:{room_id}", redis_message)

    async def handle_webrtc_offer(
        self,
        connection_id: UUID,
        target_user_id: UUID,
        offer: dict
    ):
        """Handle WebRTC offer and forward to target user"""
        connection = self.active_connections.get(connection_id)
        if not connection:
            return

        message = {
            "type": "webrtc_offer",
            "data": {
                "offer": offer,
                "from_user_id": str(connection.user_id),
                "from_connection_id": str(connection_id)
            }
        }

        # Send to target user's connections in the same room
        await self._send_to_user_in_room(target_user_id, connection.room_id, message)

    async def handle_webrtc_answer(
        self,
        connection_id: UUID,
        target_user_id: UUID,
        answer: dict
    ):
        """Handle WebRTC answer and forward to target user"""
        connection = self.active_connections.get(connection_id)
        if not connection:
            return

        message = {
            "type": "webrtc_answer",
            "data": {
                "answer": answer,
                "from_user_id": str(connection.user_id),
                "from_connection_id": str(connection_id)
            }
        }

        await self._send_to_user_in_room(target_user_id, connection.room_id, message)

    async def handle_ice_candidate(
        self,
        connection_id: UUID,
        target_user_id: UUID,
        candidate: dict
    ):
        """Handle ICE candidate and forward to target user"""
        connection = self.active_connections.get(connection_id)
        if not connection:
            return

        message = {
            "type": "ice_candidate",
            "data": {
                "candidate": candidate,
                "from_user_id": str(connection.user_id),
                "from_connection_id": str(connection_id)
            }
        }

        await self._send_to_user_in_room(target_user_id, connection.room_id, message)

    async def handle_user_joined(
        self,
        room_id: UUID,
        user_data: dict
    ):
        """Notify room that a user joined"""
        message = {
            "type": "user_joined",
            "data": user_data
        }
        await self.broadcast_to_room(room_id, message, exclude_user=user_data["user_id"])

    async def handle_user_left(
        self,
        room_id: UUID,
        user_data: dict
    ):
        """Notify room that a user left"""
        message = {
            "type": "user_left",
            "data": user_data
        }
        await self.broadcast_to_room(room_id, message)

    async def handle_user_speaking(
        self,
        connection_id: UUID,
        is_speaking: bool
    ):
        """Handle user speaking status update"""
        connection = self.active_connections.get(connection_id)
        if not connection:
            return

        connection.is_speaking = is_speaking

        message = {
            "type": "user_speaking",
            "data": {
                "user_id": str(connection.user_id),
                "is_speaking": is_speaking
            }
        }
        await self.broadcast_to_room(connection.room_id, message, exclude_connection=connection_id)

    async def _send_to_user_in_room(self, user_id: UUID, room_id: UUID, message: dict):
        """Send message to all connections of a user in a specific room"""
        async with self._lock:
            if user_id not in self.user_connections:
                return

            for connection_id in self.user_connections[user_id]:
                connection = self.active_connections.get(connection_id)
                if connection and connection.room_id == room_id:
                    await self.send_personal_message(connection_id, message)

    def get_room_connection_count(self, room_id: UUID) -> int:
        """Get number of active connections in a room"""
        return len(self.room_connections.get(room_id, []))

    def get_user_connection_count(self, user_id: UUID) -> int:
        """Get number of active connections for a user"""
        return len(self.user_connections.get(user_id, []))

# Global audio room manager instance - EXACT SAME PATTERN
audio_room_manager = AudioRoomManager()
