import asyncpg
from typing import List, Optional
from uuid import UUID
from app.core.security import get_password_hash
from app.schemas.audio import AudioRoomCreate, AudioRoomUpdate
from app.database.database import database

class AudioCRUD:
    """Secure CRUD operations for audio rooms with asyncpg Record conversion"""
    
    async def _record_to_dict(self, record: asyncpg.Record) -> dict:
        """Convert asyncpg Record to dictionary for Pydantic serialization"""
        if not record:
            return None
        return {key: record[key] for key in record.keys()}

    async def create_audio_room(self, room_data: AudioRoomCreate, user_id: UUID) -> Optional[dict]:
        """Create a new audio room"""
        async with database.pool.acquire() as conn:
            query = """
                INSERT INTO audio_rooms (
                    title, description, created_by, visibility,
                    max_participants, room_type, host_username
                ) VALUES ($1, $2, $3, $4, $5, $6, (
                    SELECT username FROM users WHERE id = $3
                ))
                RETURNING *
            """

            room = await conn.fetchrow(
                query,
                room_data.title,
                room_data.description,
                user_id,
                room_data.visibility,
                room_data.max_participants,
                room_data.room_type
            )
            return await self._record_to_dict(room) if room else None

    async def get_audio_rooms(
        self,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[UUID] = None
    ) -> List[dict]:
        """Get list of audio rooms with basic participant info"""
        async with database.pool.acquire() as conn:
            query = """
                SELECT
                    ar.*,
                    COUNT(arp.id) as current_participants
                FROM audio_rooms ar
                LEFT JOIN audio_room_participants arp ON ar.id = arp.room_id AND arp.left_at IS NULL
                WHERE ar.is_active = true
                GROUP BY ar.id
                ORDER BY ar.created_at DESC
                LIMIT $1 OFFSET $2
            """

            rooms = await conn.fetch(query, limit, skip)
            return [await self._record_to_dict(room) for room in rooms] if rooms else []

    async def get_audio_room_by_id(self, room_id: UUID) -> Optional[dict]:
        """Get audio room by ID"""
        async with database.pool.acquire() as conn:
            query = """
                SELECT
                    ar.*,
                    COUNT(arp.id) as current_participants
                FROM audio_rooms ar
                LEFT JOIN audio_room_participants arp ON ar.id = arp.room_id AND arp.left_at IS NULL
                WHERE ar.id = $1
                GROUP BY ar.id
            """

            room = await conn.fetchrow(query, room_id)
            return await self._record_to_dict(room) if room else None

    async def update_audio_room(
        self,
        room_id: UUID,
        room_data: AudioRoomUpdate
    ) -> Optional[dict]:
        """Update audio room"""
        # Build dynamic update query based on provided fields
        update_fields = []
        values = []
        param_count = 1

        if room_data.title is not None:
            update_fields.append(f"title = ${param_count}")
            values.append(room_data.title)
            param_count += 1

        if room_data.description is not None:
            update_fields.append(f"description = ${param_count}")
            values.append(room_data.description)
            param_count += 1

        if room_data.visibility is not None:
            update_fields.append(f"visibility = ${param_count}")
            values.append(room_data.visibility)
            param_count += 1

        if room_data.max_participants is not None:
            update_fields.append(f"max_participants = ${param_count}")
            values.append(room_data.max_participants)
            param_count += 1

        if room_data.room_type is not None:
            update_fields.append(f"room_type = ${param_count}")
            values.append(room_data.room_type)
            param_count += 1

        if room_data.is_active is not None:
            update_fields.append(f"is_active = ${param_count}")
            values.append(room_data.is_active)
            param_count += 1

        if room_data.is_locked is not None:
            update_fields.append(f"is_locked = ${param_count}")
            values.append(room_data.is_locked)
            param_count += 1

        if room_data.lock_reason is not None:
            update_fields.append(f"lock_reason = ${param_count}")
            values.append(room_data.lock_reason)
            param_count += 1

        if not update_fields:
            return await self.get_audio_room_by_id(room_id)

        update_fields.append("updated_at = NOW()")
        values.append(room_id)

        query = f"""
            UPDATE audio_rooms
            SET {', '.join(update_fields)}
            WHERE id = ${param_count}
            RETURNING *
        """

        room = await conn.fetchrow(query, *values)
        return await self._record_to_dict(room) if room else None

    async def delete_audio_room(self, room_id: UUID, user_id: UUID) -> bool:
        """Delete audio room (soft delete by setting is_active = false)"""
        async with database.pool.acquire() as conn:
            query = """
                UPDATE audio_rooms
                SET is_active = false, updated_at = NOW()
                WHERE id = $1 AND created_by = $2
                RETURNING id
            """

            result = await conn.fetchrow(query, room_id, user_id)
            return result is not None

    async def join_audio_room(
        self,
        room_id: UUID,
        user_id: UUID,
        is_speaker: bool = False,
        is_moderator: bool = False
    ) -> Optional[dict]:
        """Join an audio room as participant"""
        async with database.pool.acquire() as conn:
            query = """
                INSERT INTO audio_room_participants (room_id, user_id, is_speaker, is_moderator)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (room_id, user_id)
                DO UPDATE SET
                    left_at = NULL,
                    is_speaker = $3,
                    is_moderator = $4,
                    joined_at = NOW()
                RETURNING *
            """

            participant = await conn.fetchrow(query, room_id, user_id, is_speaker, is_moderator)
            return await self._record_to_dict(participant) if participant else None

    async def leave_audio_room(self, room_id: UUID, user_id: UUID) -> bool:
        """Leave an audio room"""
        async with database.pool.acquire() as conn:
            query = """
                UPDATE audio_room_participants
                SET left_at = NOW()
                WHERE room_id = $1 AND user_id = $2 AND left_at IS NULL
                RETURNING id
            """

            result = await conn.fetchrow(query, room_id, user_id)
            return result is not None

# Global audio CRUD instance
audio_crud = AudioCRUD()
