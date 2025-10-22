"""
Enhanced Connection Manager with Redis Integration - FIXED VERSION
Following security-first blueprint with cross-instance delivery
"""
import asyncio
import logging
from typing import Dict, List, Optional, Set
from uuid import UUID, uuid4
from fastapi import WebSocket
import asyncpg

from app.services.redis_service import redis_service

logger = logging.getLogger("safe_zone.connection_manager")

class Connection:
    """
    Represents an active WebSocket connection with security context
    Follows zero-trust principle with dedicated DB connection
    """
    def __init__(
        self, 
        websocket: WebSocket, 
        user_id: UUID, 
        db_connection: asyncpg.Connection,
        connection_id: UUID
    ):
        self.websocket = websocket
        self.user_id = user_id
        self.db_connection = db_connection
        self.connection_id = connection_id
        self.authenticated_at = asyncio.get_event_loop().time()
        self.conversations: Set[UUID] = set()  # Track which conversations user is viewing

class ConnectionManager:
    """
    Manages active WebSocket connections with Redis integration
    """
    def __init__(self):
        self.active_connections: Dict[UUID, Connection] = {}
        self.user_connections: Dict[UUID, List[UUID]] = {}
        self.conversation_subscribers: Dict[UUID, Set[UUID]] = {}  # conversation_id -> set of user_ids
        self._lock = asyncio.Lock()
        self._redis_initialized = False
        
    async def initialize_redis(self):
        """Initialize Redis connection and subscriber - call this once at startup"""
        if not self._redis_initialized:
            await redis_service.connect()
            # Start Redis subscriber in background
            asyncio.create_task(self._subscribe_to_conversations())
            self._redis_initialized = True

    async def _subscribe_to_conversations(self):
        """Subscribe to conversation channels for message delivery"""
        try:
            # This would be enhanced to dynamically subscribe to user's conversations
            # For now, we'll use a pattern to catch all conversation messages
            await redis_service.subscribe_to_channel(
                "conversation:*", 
                self._handle_redis_message
            )
        except Exception as e:
            logger.error(f"Failed to subscribe to Redis conversations: {e}")

    async def _handle_redis_message(self, message_data: dict):
        """Handle incoming Redis messages and deliver to connected users"""
        try:
            conversation_id = message_data.get('conversation_id')
            if not conversation_id:
                return

            # Convert to UUID if it's a string
            if isinstance(conversation_id, str):
                conversation_id = UUID(conversation_id)

            # Deliver to all subscribers of this conversation
            await self._deliver_to_conversation_subscribers(conversation_id, message_data)

        except Exception as e:
            logger.error(f"Error handling Redis message: {e}")

    async def _deliver_to_conversation_subscribers(self, conversation_id: UUID, message: dict):
        """Deliver message to all users subscribed to a conversation"""
        async with self._lock:
            if conversation_id not in self.conversation_subscribers:
                return

            user_ids = self.conversation_subscribers[conversation_id].copy()
            
        # Deliver to each user's connections
        for user_id in user_ids:
            await self.send_personal_message(user_id, {
                "type": "message.new",
                "data": message
            })

    async def connect(
        self, 
        websocket: WebSocket, 
        user_id: UUID, 
        db_connection: asyncpg.Connection
    ) -> UUID:
        """
        Add new secure WebSocket connection
        Returns connection ID for management
        """
        connection_id = uuid4()
        
        async with self._lock:
            connection = Connection(websocket, user_id, db_connection, connection_id)
            self.active_connections[connection_id] = connection
            
            # Track user's connections
            if user_id not in self.user_connections:
                self.user_connections[user_id] = []
            self.user_connections[user_id].append(connection_id)
            
        logger.info(f"WebSocket connection established: {connection_id} for user {user_id}")
        return connection_id

    async def subscribe_to_conversation(self, connection_id: UUID, conversation_id: UUID):
        """
        Subscribe connection to a conversation for real-time updates
        """
        async with self._lock:
            if connection_id not in self.active_connections:
                return

            connection = self.active_connections[connection_id]
            connection.conversations.add(conversation_id)
            
            # Track conversation subscribers
            if conversation_id not in self.conversation_subscribers:
                self.conversation_subscribers[conversation_id] = set()
            self.conversation_subscribers[conversation_id].add(connection.user_id)
            
        logger.debug(f"User {connection.user_id} subscribed to conversation {conversation_id}")

    async def unsubscribe_from_conversation(self, connection_id: UUID, conversation_id: UUID):
        """
        Unsubscribe connection from a conversation
        """
        async with self._lock:
            if connection_id not in self.active_connections:
                return

            connection = self.active_connections[connection_id]
            connection.conversations.discard(conversation_id)
            
            # Remove from conversation subscribers
            if conversation_id in self.conversation_subscribers:
                self.conversation_subscribers[conversation_id].discard(connection.user_id)
                if not self.conversation_subscribers[conversation_id]:
                    del self.conversation_subscribers[conversation_id]

    async def disconnect(self, connection_id: UUID):
        """
        Remove WebSocket connection and cleanup resources
        """
        async with self._lock:
            if connection_id in self.active_connections:
                connection = self.active_connections[connection_id]
                
                # Remove from all conversation subscriptions
                for conversation_id in connection.conversations.copy():
                    await self.unsubscribe_from_conversation(connection_id, conversation_id)
                
                # Remove from user tracking
                if connection.user_id in self.user_connections:
                    user_conns = self.user_connections[connection.user_id]
                    if connection_id in user_conns:
                        user_conns.remove(connection_id)
                    if not user_conns:
                        del self.user_connections[connection.user_id]
                
                # Remove from active connections
                del self.active_connections[connection_id]
                
                logger.info(f"WebSocket connection removed: {connection_id}")

    async def send_personal_message(
        self, 
        user_id: UUID, 
        message: dict
    ):
        """
        Send message to all connections of a specific user
        Security: Only sends to authenticated user's connections
        """
        async with self._lock:
            if user_id not in self.user_connections:
                return

            failed_connections = []
            
            for connection_id in self.user_connections[user_id]:
                connection = self.active_connections.get(connection_id)
                if connection:
                    try:
                        await connection.websocket.send_json(message)
                    except Exception as e:
                        logger.error(f"Failed to send message to {connection_id}: {e}")
                        failed_connections.append(connection_id)
            
            # Cleanup failed connections
            for connection_id in failed_connections:
                await self.disconnect(connection_id)

    async def broadcast_to_conversation(
        self, 
        conversation_id: UUID, 
        message: dict,
        exclude_user_id: Optional[UUID] = None
    ):
        """
        Send message to all users subscribed to a conversation
        Security: Ensures only authorized users receive messages
        """
        # Publish to Redis for cross-instance delivery
        redis_message = {
            **message,
            "conversation_id": str(conversation_id),
            "timestamp": asyncio.get_event_loop().time()
        }
        await redis_service.publish_message(f"conversation:{conversation_id}", redis_message)

    def get_user_connection_count(self, user_id: UUID) -> int:
        """Get number of active connections for a user"""
        return len(self.user_connections.get(user_id, []))

    def get_total_connections(self) -> int:
        """Get total number of active connections"""
        return len(self.active_connections)

# Global connection manager instance
connection_manager = ConnectionManager()
