"""
UNIFIED Live Audio Rooms CRUD - Using same RLS pattern as enhanced_moderation
"""
import asyncpg
from typing import Optional, List, Dict, Any
from uuid import UUID
from app.database.database import database

class LiveAudioRoomsCRUD:
    """
    UNIFIED CRUD operations using session-level RLS context
    """

    async def create_room(
        self,
        room_data: Dict[str, Any],
        user_id: UUID
    ) -> Optional[asyncpg.Record]:
        """
        Create room with UNIFIED RLS context (session-level)
        """
        async with database.pool.acquire() as conn:
            # UNIFIED: Use session-level context like enhanced_moderation
            await conn.execute("SELECT set_config('app.current_user_id', $1, false)", str(user_id))

            # Create room
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
                # Auto-join creator as host
                await conn.execute(
                    """
                    INSERT INTO live_audio_room_participants (room_id, user_id, role)
                    VALUES ($1, $2, 'host')
                    """,
                    room['id'], user_id
                )

            return room

    async def leave_room(self, room_id: UUID, user_id: UUID) -> bool:
        """Leave room with UNIFIED RLS context"""
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_config('app.current_user_id', $1, false)", str(user_id))

            try:
                result = await conn.execute(
                    """
                    UPDATE live_audio_room_participants
                    SET left_at = NOW(), is_active = false
                    WHERE room_id = $1 AND user_id = $2 AND left_at IS NULL
                    """,
                    room_id, user_id
                )
                return "UPDATE 1" in result
            except Exception as e:
                print(f"Leave room error: {e}")
                return False

    # Add other methods with unified pattern...
    async def get_room(self, room_id: UUID, user_id: UUID) -> Optional[asyncpg.Record]:
        """Get room with UNIFIED RLS context"""
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_config('app.current_user_id', $1, false)", str(user_id))

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
        """Join room with UNIFIED RLS context"""
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_config('app.current_user_id', $1, false)", str(user_id))

            # Check if room exists and has space
            room = await conn.fetchrow(
                "SELECT * FROM live_audio_rooms WHERE id = $1 AND is_active = true",
                room_id
            )

            if not room:
                return None

            # Check room capacity
            if room['current_participants'] >= room['max_participants']:
                return None

            # Check if already joined
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

            # Join room
            participant = await conn.fetchrow(
                """
                INSERT INTO live_audio_room_participants (room_id, user_id, role)
                VALUES ($1, $2, $3)
                RETURNING *
                """,
                room_id, user_id, role
            )

            return participant

# Global instance with unified pattern
live_audio_rooms_crud = LiveAudioRoomsCRUD()
