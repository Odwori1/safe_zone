"""
FIXED Live Audio Rooms CRUD - With working room leaving
"""
import asyncpg
from typing import Optional, List, Dict, Any
from uuid import UUID
from app.database.database import database

class LiveAudioRoomsCRUD:
    """
    FIXED CRUD operations for live audio rooms
    """

    async def create_room(
        self,
        room_data: Dict[str, Any],
        user_id: UUID
    ) -> Optional[asyncpg.Record]:
        """
        Create a new live audio room
        """
        async with database.pool.acquire() as conn:
            # Set RLS context
            await conn.execute("SELECT set_config('app.current_user_id', $1, true)", str(user_id))
            
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
        """
        FIXED: Leave a live audio room
        """
        async with database.pool.acquire() as conn:
            # Set RLS context
            await conn.execute("SELECT set_config('app.current_user_id', $1, true)", str(user_id))
            
            try:
                # Mark participant as left
                result = await conn.execute(
                    """
                    UPDATE live_audio_room_participants 
                    SET left_at = NOW(), is_active = false
                    WHERE room_id = $1 AND user_id = $2 AND left_at IS NULL
                    """,
                    room_id, user_id
                )
                
                # Check if update was successful
                return "UPDATE 1" in result
                
            except Exception as e:
                print(f"Leave room error: {e}")
                return False

    # ... keep all other methods the same as in live_audio_rooms.py
    async def get_active_rooms(
        self,
        room_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[asyncpg.Record]:
        """Get active rooms user can access"""
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
        """Get specific room details"""
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
        """Join a live audio room"""
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_config('app.current_user_id', $1, true)", str(user_id))
            
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

    async def get_room_participants(
        self,
        room_id: UUID,
        user_id: UUID
    ) -> List[asyncpg.Record]:
        """Get current participants in a room"""
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

# Replace the global instance
live_audio_rooms_crud = LiveAudioRoomsCRUD()
