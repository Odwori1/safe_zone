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

    async def _record_to_dict(self, record: asyncpg.Record) -> dict:
        """Convert asyncpg Record to dictionary for Pydantic serialization"""
        if not record:
            return None
        return {key: record[key] for key in record.keys()}

    async def create_room(
        self,
        room_data: Dict[str, Any],
        user_id: UUID
    ) -> Optional[dict]:
        """
        Create room with UNIFIED RLS context (session-level)
        """
        async with database.pool.acquire() as conn:
            # UNIFIED: Use session-level context like enhanced_moderation
            await conn.execute("SELECT set_config('app.current_user_id', $1, false)", str(user_id))

            # Create room - FIXED: Explicit field selection
            room = await conn.fetchrow(
                """
                INSERT INTO live_audio_rooms
                (title, description, created_by, max_participants, room_type, visibility)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING
                    id,
                    title,
                    description,
                    created_by,
                    visibility,
                    max_participants,
                    room_type,
                    is_active,
                    current_participants,
                    created_at,
                    updated_at
                """,
                room_data["title"],
                room_data.get("description"),
                user_id,
                room_data.get("max_participants", 50),
                room_data.get("room_type", "support"),
                room_data.get("visibility", "public")
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

            return await self._record_to_dict(room) if room else None

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

    async def get_room(self, room_id: UUID, user_id: UUID) -> Optional[dict]:
        """Get room with UNIFIED RLS context"""
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_config('app.current_user_id', $1, false)", str(user_id))

            # FIXED: Removed JOIN and trailing comma
            room = await conn.fetchrow(
                """
                SELECT
                    id,
                    title,
                    description,
                    created_by,
                    visibility,
                    max_participants,
                    room_type,
                    is_active,
                    current_participants,
                    created_at,
                    updated_at
                FROM live_audio_rooms
                WHERE id = $1 AND is_active = true
                """,
                room_id
            )
            return await self._record_to_dict(room) if room else None

    async def join_room(
        self,
        room_id: UUID,
        user_id: UUID,
        role: str = "participant"
    ) -> Optional[dict]:
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
                return await self._record_to_dict(existing)

            # Join room
            participant = await conn.fetchrow(
                """
                INSERT INTO live_audio_room_participants (room_id, user_id, role)
                VALUES ($1, $2, $3)
                RETURNING *
                """,
                room_id, user_id, role
            )

            return await self._record_to_dict(participant) if participant else None

    async def get_room_participants(
        self,
        room_id: UUID,
        user_id: UUID
    ) -> List[dict]:
        """Get room participants with UNIFIED RLS context"""
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_config('app.current_user_id', $1, false)", str(user_id))

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
            return [await self._record_to_dict(p) for p in participants] if participants else []

    async def get_active_rooms(
        self,
        room_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[dict]:
        """Get active rooms (no user context needed for public rooms)"""
        async with database.pool.acquire() as conn:
            if room_type:
                # FIXED: Removed JOIN and host_username
                rooms = await conn.fetch(
                    """
                    SELECT
                        id,
                        title,
                        description,
                        created_by,
                        visibility,
                        max_participants,
                        room_type,
                        is_active,
                        current_participants,
                        created_at,
                        updated_at
                    FROM live_audio_rooms
                    WHERE is_active = true AND room_type = $1
                    ORDER BY current_participants DESC, created_at DESC
                    LIMIT $2 OFFSET $3
                    """,
                    room_type, limit, offset
                )
            else:
                # FIXED: Removed JOIN and trailing comma
                rooms = await conn.fetch(
                    """
                    SELECT
                        id,
                        title,
                        description,
                        created_by,
                        visibility,
                        max_participants,
                        room_type,
                        is_active,
                        current_participants,
                        created_at,
                        updated_at
                    FROM live_audio_rooms
                    WHERE is_active = true
                    ORDER BY current_participants DESC, created_at DESC
                    LIMIT $1 OFFSET $2
                    """,
                    limit, offset
                )
            return [await self._record_to_dict(room) for room in rooms] if rooms else []

    async def create_moderation_action(
        self,
        room_id: UUID,
        action_data: Dict[str, Any],
        user_id: UUID
    ) -> Optional[dict]:
        """Create moderation action with UNIFIED RLS context"""
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_config('app.current_user_id', $1, false)", str(user_id))

            try:
                action = await conn.fetchrow(
                    """
                    INSERT INTO live_audio_room_moderations (
                        room_id, moderator_id, target_user_id,
                        action_type, reason, duration_minutes
                    ) VALUES ($1, $2, $3, $4, $5, $6)
                    RETURNING *
                    """,
                    room_id,
                    user_id,
                    action_data.get('target_user_id'),
                    action_data.get('action_type'),
                    action_data.get('reason'),
                    action_data.get('duration_minutes')
                )
                return await self._record_to_dict(action) if action else None
            except Exception as e:
                print(f"Error creating moderation action: {e}")
                return None

# Global instance with unified pattern
live_audio_rooms_crud = LiveAudioRoomsCRUD()
