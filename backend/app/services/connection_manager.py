"""
WebSocket Connection Manager for Phase 3, Item 4
Following security-first blueprint and existing patterns
"""
import asyncio
import logging
from typing import Dict, List, Optional
from uuid import UUID, uuid4
from fastapi import WebSocket
import asyncpg

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

class ConnectionManager:
    """
    Manages active WebSocket connections with security isolation
    """
    def __init__(self):
        self.active_connections: Dict[UUID, Connection] = {}
        self.user_connections: Dict[UUID, List[UUID]] = {}
        self._lock = asyncio.Lock()

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

    async def disconnect(self, connection_id: UUID):
        """
        Remove WebSocket connection and cleanup resources
        """
        async with self._lock:
            if connection_id in self.active_connections:
                connection = self.active_connections[connection_id]
                
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

    async def broadcast_to_users(
        self, 
        user_ids: List[UUID], 
        message: dict
    ):
        """
        Send message to multiple specific users
        Security: Ensures only authorized users receive messages
        """
        for user_id in user_ids:
            await self.send_personal_message(user_id, message)

    def get_user_connection_count(self, user_id: UUID) -> int:
        """Get number of active connections for a user"""
        return len(self.user_connections.get(user_id, []))

    def get_total_connections(self) -> int:
        """Get total number of active connections"""
        return len(self.active_connections)

# Global connection manager instance
connection_manager = ConnectionManager()
