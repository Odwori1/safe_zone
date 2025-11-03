"""
Enhanced Moderation CRUD - PROPERLY FIXED RLS CONTEXT
Using correct session-level context setting with safe string formatting
"""

import asyncpg
from typing import Optional, List, Dict, Any
from uuid import UUID
from app.database.database import database

class EnhancedModerationCRUD:
    """
    Enhanced moderation CRUD operations with PROPER RLS context
    SECURITY: Uses parameterized set_config with is_local=false for session-level context
    """

    async def _record_to_dict(self, record: asyncpg.Record) -> dict:
        """Convert asyncpg Record to dictionary for Pydantic serialization"""
        if not record:
            return None
        return {key: record[key] for key in record.keys()}

    async def create_moderation_action(
        self,
        room_id: UUID,
        action_data: Dict[str, Any],
        moderator_id: UUID
    ) -> Optional[dict]:
        """
        Create a moderation action with PROPER RLS context
        """
        async with database.pool.acquire() as conn:
            # FIX: Use set_config with is_local=false for session-level context
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(moderator_id)
            )

            action = await conn.fetchrow(
                """
                INSERT INTO live_audio_room_moderations
                (room_id, moderator_id, target_user_id, action_type, reason, duration_minutes)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING *
                """,
                room_id, moderator_id, action_data["target_user_id"],
                action_data["action_type"], action_data.get("reason"),
                action_data.get("duration_minutes")
            )
            return await self._record_to_dict(action) if action else None

    async def get_user_moderation_status(
        self,
        room_id: UUID,
        user_id: UUID,
        requesting_user_id: UUID
    ) -> List[dict]:
        """
        Get moderation status with PROPER RLS context
        """
        async with database.pool.acquire() as conn:
            # FIX: Use set_config with is_local=false
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(requesting_user_id)
            )

            actions = await conn.fetch(
                """
                SELECT * FROM live_audio_room_moderations
                WHERE room_id = $1 AND target_user_id = $2
                ORDER BY created_at DESC
                LIMIT 10
                """,
                room_id, user_id
            )
            return [await self._record_to_dict(action) for action in actions] if actions else []

    async def is_user_muted(
        self,
        room_id: UUID,
        user_id: UUID,
        requesting_user_id: UUID
    ) -> bool:
        """Check if user is muted with PROPER RLS context"""
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(requesting_user_id)
            )

            mute_action = await conn.fetchrow(
                """
                SELECT * FROM live_audio_room_moderations
                WHERE room_id = $1 AND target_user_id = $2
                AND action_type = 'mute'
                AND (duration_minutes IS NULL
                     OR created_at + (duration_minutes * INTERVAL '1 minute') > NOW())
                ORDER BY created_at DESC
                LIMIT 1
                """,
                room_id, user_id
            )
            return mute_action is not None

    async def get_room_moderators(
        self,
        room_id: UUID,
        requesting_user_id: UUID
    ) -> List[dict]:
        """Get room moderators with PROPER RLS context"""
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(requesting_user_id)
            )

            moderators = await conn.fetch(
                """
                SELECT p.*, u.username, u.email
                FROM live_audio_room_participants p
                JOIN users u ON p.user_id = u.id
                WHERE p.room_id = $1
                AND p.role IN ('host', 'moderator')
                AND p.left_at IS NULL
                ORDER BY
                    CASE p.role
                        WHEN 'host' THEN 1
                        WHEN 'moderator' THEN 2
                    END,
                    p.joined_at
                """,
                room_id
            )
            return [await self._record_to_dict(mod) for mod in moderators] if moderators else []

    async def create_content_report(
        self,
        report_data: Dict[str, Any],
        reporter_id: UUID
    ) -> Optional[dict]:
        """Create content report with PROPER RLS context"""
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(reporter_id)
            )

            report = await conn.fetchrow(
                """
                INSERT INTO content_reports
                (reporter_id, content_type, content_id, reason, description)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING *
                """,
                reporter_id, report_data["content_type"], report_data["content_id"],
                report_data["reason"], report_data.get("description")
            )
            return await self._record_to_dict(report) if report else None

    async def get_user_reports(
        self,
        reporter_id: UUID
    ) -> List[dict]:
        """Get user reports with PROPER RLS context"""
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(reporter_id)
            )

            reports = await conn.fetch(
                """
                SELECT * FROM content_reports
                WHERE reporter_id = $1
                ORDER BY created_at DESC
                """,
                reporter_id
            )
            return [await self._record_to_dict(report) for report in reports] if reports else []

    async def promote_to_moderator(
        self,
        room_id: UUID,
        target_user_id: UUID,
        promoter_id: UUID
    ) -> Optional[dict]:
        """Promote user to moderator with PROPER RLS context"""
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(promoter_id)
            )

            # Update user role to moderator
            updated = await conn.fetchrow(
                """
                UPDATE live_audio_room_participants
                SET role = 'moderator'
                WHERE room_id = $1 AND user_id = $2 AND left_at IS NULL
                RETURNING *
                """,
                room_id, target_user_id
            )
            return await self._record_to_dict(updated) if updated else None

    async def demote_from_moderator(
        self,
        room_id: UUID,
        target_user_id: UUID,
        demoter_id: UUID
    ) -> Optional[dict]:
        """Demote user from moderator with PROPER RLS context"""
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(demoter_id)
            )

            # Update user role to participant
            updated = await conn.fetchrow(
                """
                UPDATE live_audio_room_participants
                SET role = 'participant'
                WHERE room_id = $1 AND user_id = $2 AND left_at IS NULL
                RETURNING *
                """,
                room_id, target_user_id
            )
            return await self._record_to_dict(updated) if updated else None

    async def remove_user_from_room(
        self,
        room_id: UUID,
        target_user_id: UUID,
        moderator_id: UUID,
        reason: Optional[str] = None
    ) -> bool:
        """Remove user from room with PROPER RLS context"""
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(moderator_id)
            )

            try:
                # Mark participant as removed (force leave)
                result = await conn.execute(
                    """
                    UPDATE live_audio_room_participants
                    SET left_at = NOW(), is_active = false
                    WHERE room_id = $1 AND user_id = $2 AND left_at IS NULL
                    """,
                    room_id, target_user_id
                )

                # Also create a moderation action record
                if "UPDATE 1" in result:
                    await self.create_moderation_action(
                        room_id,
                        {
                            "target_user_id": target_user_id,
                            "action_type": "remove",
                            "reason": reason or "Removed by moderator"
                        },
                        moderator_id
                    )
                    return True

                return False

            except Exception as e:
                print(f"Remove user error: {e}")
                return False

    async def ban_user_from_room(
        self,
        room_id: UUID,
        target_user_id: UUID,
        moderator_id: UUID,
        reason: Optional[str] = None,
        duration_minutes: Optional[int] = None
    ) -> bool:
        """Ban user from room with PROPER RLS context"""
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(moderator_id)
            )

            try:
                # First remove user from room
                await self.remove_user_from_room(room_id, target_user_id, moderator_id, reason)

                # Then create ban action
                ban_action = await self.create_moderation_action(
                    room_id,
                    {
                        "target_user_id": target_user_id,
                        "action_type": "ban",
                        "reason": reason or "Banned by moderator",
                        "duration_minutes": duration_minutes
                    },
                    moderator_id
                )

                return ban_action is not None

            except Exception as e:
                print(f"Ban user error: {e}")
                return False

    async def lock_room(
        self,
        room_id: UUID,
        moderator_id: UUID,
        reason: Optional[str] = None
    ) -> Optional[dict]:
        """Lock room to prevent new joins with PROPER RLS context"""
        async with database.pool.acquire() as conn:
            # FIX: Use set_config with is_local=false for session-level context
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(moderator_id)
            )

            # Update room to locked status
            room = await conn.fetchrow(
                """
                UPDATE live_audio_rooms
                SET is_locked = true,
                    locked_by = $1,
                    lock_reason = $2,
                    locked_at = NOW(),
                    updated_at = NOW()
                WHERE id = $3
                RETURNING *
                """,
                str(moderator_id), reason, room_id
            )

            # Create moderation action record
            if room:
                await self.create_moderation_action(
                    room_id,
                    {
                        "target_user_id": None,  # Room-level action
                        "action_type": "lock_room",
                        "reason": reason or "Room locked by moderator"
                    },
                    moderator_id
                )

            return await self._record_to_dict(room) if room else None

    async def unlock_room(
        self,
        room_id: UUID,
        moderator_id: UUID
    ) -> Optional[dict]:
        """Unlock room to allow new joins with PROPER RLS context"""
        async with database.pool.acquire() as conn:
            # FIX: Use set_config with is_local=false for session-level context
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(moderator_id)
            )

            # Update room to unlocked status
            room = await conn.fetchrow(
                """
                UPDATE live_audio_rooms
                SET is_locked = false,
                    locked_by = NULL,
                    lock_reason = NULL,
                    locked_at = NULL,
                    updated_at = NOW()
                WHERE id = $1
                RETURNING *
                """,
                room_id
            )

            # Create moderation action record
            if room:
                await self.create_moderation_action(
                    room_id,
                    {
                        "target_user_id": None,  # Room-level action
                        "action_type": "unlock_room",
                        "reason": "Room unlocked by moderator"
                    },
                    moderator_id
                )

            return await self._record_to_dict(room) if room else None

# Instantiate the class
enhanced_moderation_crud = EnhancedModerationCRUD()
