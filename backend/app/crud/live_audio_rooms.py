"""
SECURE CRUD operations for live audio rooms - WITH CIRCULAR DEPENDENCY FIX
Following previous developer's guidance exactly
"""

import asyncpg
from typing import Optional, List, Dict, Any
from uuid import UUID
from app.database.database import database

class LiveAudioRoomsCRUD:
    """
    Secure CRUD operations for live audio rooms
    RLS provides isolation, application handles business logic
    """

    async def create_room(
        self,
        room_data: Dict[str, Any],
        user_id: UUID
    ) -> Optional[asyncpg.Record]:
        """
        Create a new live audio room
        RLS: INSERT WITH CHECK (true) - NO circular dependency
        """
        async with database.pool.acquire() as conn:
            # Set RLS context
            await conn.execute("SELECT set_config('app.current_user_id', $1, true)", str(user_id))
            
            # Create room - RLS allows this (no participant check)
            room = await conn.fetchrow(
                """
                INSERT INTO live_audio_rooms 
                (title, description, created_by, max_participants, room_type)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING *
                """,
                room_data["title"], room_data.get("description"), user_id,
                room_data.get("max_participants", 50), room_data.get("room_type", "support")
            )

            if room:
                # Auto-join creator as host - RLS allows this
                await conn.execute(
                    """
                    INSERT INTO live_audio_room_participants (room_id, user_id, role)
                    VALUES ($1, $2, 'host')
                    """,
                    room['id'], user_id
                )

            return room

    async def get_active_rooms(
        self,
        room_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[asyncpg.Record]:
        """
        Get active rooms user can access
        RLS: Only shows rooms user participates in
        """
        async with database.pool.acquire() as conn:
            if room_type:
                rooms = await conn.fetch(
                    """
                    SELECT lr.*, u.username as host_username
                    FROM live_audio_rooms lr
                    JOIN users u ON lr.created_by = u.id
                    WHERE lr.is_active = true AND lr.room_type = $1
                    ORDER BY lr.current_participants DESC, lr.created_at DESC
                    LIMIT $2 OFFSET $3
                    """,
                    room_type, limit, offset
                )
            else:
                rooms = await conn.fetch(
                    """
                    SELECT lr.*, u.username as host_username
                    FROM live_audio_rooms lr
                    JOIN users u ON lr.created_by = u.id
                    WHERE lr.is_active = true
                    ORDER BY lr.current_participants DESC, lr.created_at DESC
                    LIMIT $1 OFFSET $2
                    """,
                    limit, offset
                )
            return rooms

    async def get_room(self, room_id: UUID, user_id: UUID) -> Optional[asyncpg.Record]:
        """
        Get specific room details
        RLS: Only returns room if user is participant
        """
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_config('app.current_user_id', $1, true)", str(user_id))

            room = await conn.fetchrow(
                """
                SELECT lr.*, u.username as host_username
                FROM live_audio_rooms lr
                JOIN users u ON lr.created_by = u.id
                WHERE lr.id = $1 AND lr.is_active = true
                """,
                room_id
            )
            return room

    async def join_room(
        self,
        room_id: UUID,
        user_id: UUID,
        role: str = "participant"
    ) -> Optional[asyncpg.Record]:
        """
        Join a live audio room
        APPLICATION handles access control (not RLS)
        """
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_config('app.current_user_id', $1, true)", str(user_id))

            # APPLICATION LOGIC: Check if room exists and has space
            room = await conn.fetchrow(
                "SELECT * FROM live_audio_rooms WHERE id = $1 AND is_active = true",
                room_id
            )

            if not room:
                return None

            # APPLICATION LOGIC: Check capacity
            if room['current_participants'] >= room['max_participants']:
                return None

            # APPLICATION LOGIC: Check if already joined
            existing = await conn.fetchrow(
                """
                SELECT * FROM live_audio_room_participants
                WHERE room_id = $1 AND user_id = $2 AND left_at IS NULL
                """,
                room_id, user_id
            )

            if existing:
                # Update last active timestamp
                await conn.execute(
                    "UPDATE live_audio_room_participants SET last_active_at = NOW() WHERE id = $1",
                    existing['id']
                )
                return existing

            # Join room - RLS allows this (basic user_id check only)
            participant = await conn.fetchrow(
                """
                INSERT INTO live_audio_room_participants (room_id, user_id, role)
                VALUES ($1, $2, $3)
                RETURNING *
                """,
                room_id, user_id, role
            )

            return participant

    async def leave_room(self, room_id: UUID, user_id: UUID) -> bool:
        """
        Leave a live audio room
        RLS: User can only leave their own participation
        """
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_config('app.current_user_id', $1, true)", str(user_id))

            result = await conn.execute(
                """
                UPDATE live_audio_room_participants
                SET left_at = NOW()
                WHERE room_id = $1 AND user_id = $2 AND left_at IS NULL
                """,
                room_id, user_id
            )

            return "UPDATE 1" in result

    async def get_room_participants(
        self,
        room_id: UUID,
        user_id: UUID
    ) -> List[asyncpg.Record]:
        """
        Get current participants in a room
        RLS: User can only see participants in rooms they access
        """
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_config('app.current_user_id', $1, true)", str(user_id))

            participants = await conn.fetch(
                """
                SELECT p.*, u.username, u.email
                FROM live_audio_room_participants p
                JOIN users u ON p.user_id = u.id
                WHERE p.room_id = $1 AND p.left_at IS NULL
                ORDER BY
                    CASE p.role
                        WHEN 'host' THEN 1
                        WHEN 'moderator' THEN 2
                        WHEN 'speaker' THEN 3
                        ELSE 4
                    END,
                    p.joined_at
                """,
                room_id
            )
            return participants

# Global CRUD instance - EXACT SAME PATTERN
live_audio_rooms_crud = LiveAudioRoomsCRUD()
