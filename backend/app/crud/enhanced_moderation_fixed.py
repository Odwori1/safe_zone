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
    Enhanced moderation CRUD operations with PROPERLY FIXED RLS context
    SECURITY: Uses parameterized set_config with is_local=false for session-level context
    """

    async def create_moderation_action(
        self,
        room_id: UUID,
        action_data: Dict[str, Any],
        moderator_id: UUID
    ) -> Optional[asyncpg.Record]:
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
            return action

    async def get_user_moderation_status(
        self,
        room_id: UUID,
        user_id: UUID,
        requesting_user_id: UUID
    ) -> List[asyncpg.Record]:
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
            return actions

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
    ) -> List[asyncpg.Record]:
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
            return moderators

    async def create_content_report(
        self,
        report_data: Dict[str, Any],
        reporter_id: UUID
    ) -> Optional[asyncpg.Record]:
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
            return report

    async def get_user_reports(
        self,
        reporter_id: UUID
    ) -> List[asyncpg.Record]:
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
            return reports

    # ... Include all other methods with the same fix ...

# Global instance
enhanced_moderation_crud = EnhancedModerationCRUD()
