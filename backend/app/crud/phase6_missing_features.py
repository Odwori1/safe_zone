"""
Phase 6 Missing Features CRUD Operations
Following EXACT same patterns as final_phase_features.py
"""

import asyncpg
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from app.database.database import database

class Phase6MissingFeaturesCRUD:
    """
    Phase 6 Missing Features CRUD with PROPER RLS context
    SECURITY: Uses parameterized set_config with is_local=false for session-level context
    """

    # ===== TELEHEALTH SESSIONS =====

    async def create_telehealth_session(
        self,
        user_id: UUID,
        session_data: Dict[str, Any]
    ) -> Optional[asyncpg.Record]:
        """
        Create telehealth session with PROPER RLS context
        SECURITY: Users can only create their own sessions
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(user_id)
            )

            session = await conn.fetchrow(
                """
                INSERT INTO telehealth_sessions
                (user_id, professional_id, scheduled_time, duration_minutes, 
                 session_status, meeting_url, notes)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING *
                """,
                user_id, session_data["professional_id"], session_data["scheduled_time"],
                session_data.get("duration_minutes", 60), session_data.get("session_status", "scheduled"),
                session_data.get("meeting_url"), session_data.get("notes")
            )
            return session

    async def get_user_telehealth_sessions(
        self,
        user_id: UUID,
        requesting_user_id: UUID,
        status: Optional[str] = None,
        upcoming_only: bool = True,
        limit: int = 20,
        offset: int = 0
    ) -> List[asyncpg.Record]:
        """
        Get user telehealth sessions with PROPER RLS context
        SECURITY: Users can only see their own sessions
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(requesting_user_id)
            )

            where_conditions = ["(user_id = $1 OR professional_id = $1)"]
            params = [user_id]
            param_count = 2

            if status:
                where_conditions.append(f"session_status = ${param_count}")
                params.append(status)
                param_count += 1

            if upcoming_only:
                where_conditions.append(f"scheduled_time > NOW()")

            where_clause = " AND ".join(where_conditions)
            params.extend([limit, offset])

            sessions = await conn.fetch(
                f"""
                SELECT ts.*,
                       u1.username as patient_username,
                       u2.username as professional_username
                FROM telehealth_sessions ts
                LEFT JOIN users u1 ON ts.user_id = u1.id
                LEFT JOIN users u2 ON ts.professional_id = u2.id
                WHERE {where_clause}
                ORDER BY ts.scheduled_time ASC
                LIMIT ${param_count} OFFSET ${param_count + 1}
                """,
                *params
            )
            return sessions

    # ===== EMR CONNECTIONS =====

    async def create_emr_connection(
        self,
        user_id: UUID,
        connection_data: Dict[str, Any]
    ) -> Optional[asyncpg.Record]:
        """
        Create EMR connection with PROPER RLS context
        SECURITY: Users can only create their own connections
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(user_id)
            )

            connection = await conn.fetchrow(
                """
                INSERT INTO emr_connections
                (user_id, emr_system, connection_status, consent_given_at, 
                 consent_expires_at, access_token_encrypted, refresh_token_encrypted)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING *
                """,
                user_id, connection_data["emr_system"], connection_data.get("connection_status", "pending"),
                connection_data["consent_given_at"], connection_data["consent_expires_at"],
                connection_data.get("access_token_encrypted"), connection_data.get("refresh_token_encrypted")
            )
            return connection

    async def get_user_emr_connections(
        self,
        user_id: UUID,
        requesting_user_id: UUID
    ) -> List[asyncpg.Record]:
        """
        Get user EMR connections with PROPER RLS context
        SECURITY: Users can only see their own connections
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(requesting_user_id)
            )

            connections = await conn.fetch(
                "SELECT * FROM emr_connections WHERE user_id = $1 ORDER BY created_at DESC",
                user_id
            )
            return connections

    # ===== COMMUNITY MILESTONES =====

    async def get_community_milestones(
        self,
        milestone_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[asyncpg.Record]:
        """
        Get community milestones with PROPER RLS context
        SECURITY: Public read access
        """
        async with database.pool.acquire() as conn:
            # Use default user ID for public access
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                "00000000-0000-0000-0000-000000000000"
            )

            where_conditions = ["1=1"]
            params = []
            param_count = 1

            if milestone_type:
                where_conditions.append(f"milestone_type = ${param_count}")
                params.append(milestone_type)
                param_count += 1

            where_clause = " AND ".join(where_conditions)
            params.extend([limit, offset])

            milestones = await conn.fetch(
                f"""
                SELECT * FROM community_milestones
                WHERE {where_clause}
                ORDER BY achieved_at DESC
                LIMIT ${param_count} OFFSET ${param_count + 1}
                """,
                *params
            )
            return milestones

    # ===== SUCCESS STORIES =====

    async def create_success_story(
        self,
        user_id: UUID,
        story_data: Dict[str, Any]
    ) -> Optional[asyncpg.Record]:
        """
        Create success story with PROPER RLS context
        SECURITY: Users can only create their own stories
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(user_id)
            )

            story = await conn.fetchrow(
                """
                INSERT INTO success_stories
                (user_id, title, story_content, consent_given, consent_given_at, 
                 anonymized, featured)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING *
                """,
                user_id, story_data["title"], story_data["story_content"],
                story_data.get("consent_given", False), story_data.get("consent_given_at"),
                story_data.get("anonymized", True), story_data.get("featured", False)
            )
            return story

    async def get_featured_success_stories(
        self,
        limit: int = 10,
        offset: int = 0
    ) -> List[asyncpg.Record]:
        """
        Get featured success stories with PROPER RLS context
        SECURITY: Public read access to featured stories with consent
        """
        async with database.pool.acquire() as conn:
            # Use default user ID for public access
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                "00000000-0000-0000-0000-000000000000"
            )

            stories = await conn.fetch(
                """
                SELECT ss.*, u.username
                FROM success_stories ss
                LEFT JOIN users u ON ss.user_id = u.id
                WHERE ss.featured = true AND ss.consent_given = true
                ORDER BY ss.featured_at DESC NULLS LAST, ss.created_at DESC
                LIMIT $1 OFFSET $2
                """,
                limit, offset
            )
            return stories

    # ===== USER SESSIONS (Timeout Management) =====

    async def create_user_session(
        self,
        user_id: UUID,
        session_data: Dict[str, Any]
    ) -> Optional[asyncpg.Record]:
        """
        Create user session for timeout management
        SECURITY: Users can only create their own sessions
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(user_id)
            )

            session = await conn.fetchrow(
                """
                INSERT INTO user_sessions
                (user_id, device_id, expires_at)
                VALUES ($1, $2, $3)
                RETURNING *
                """,
                user_id, session_data["device_id"], session_data["expires_at"]
            )
            return session

    async def update_user_session_activity(
        self,
        session_id: UUID,
        user_id: UUID
    ) -> Optional[asyncpg.Record]:
        """
        Update user session last activity
        SECURITY: Users can only update their own sessions
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(user_id)
            )

            session = await conn.fetchrow(
                """
                UPDATE user_sessions 
                SET last_activity = NOW()
                WHERE id = $1 AND user_id = $2
                RETURNING *
                """,
                session_id, user_id
            )
            return session

    # ===== DEVICE SYNC =====

    async def register_device(
        self,
        user_id: UUID,
        device_data: Dict[str, Any]
    ) -> Optional[asyncpg.Record]:
        """
        Register device for cross-device sync
        SECURITY: Users can only register their own devices
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(user_id)
            )

            device = await conn.fetchrow(
                """
                INSERT INTO device_sync
                (user_id, device_type, device_id, sync_token)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (user_id, device_id) 
                DO UPDATE SET last_sync = NOW(), sync_token = $4
                RETURNING *
                """,
                user_id, device_data["device_type"], device_data["device_id"],
                device_data.get("sync_token")
            )
            return device

    async def get_user_devices(
        self,
        user_id: UUID,
        requesting_user_id: UUID
    ) -> List[asyncpg.Record]:
        """
        Get user devices for sync
        SECURITY: Users can only see their own devices
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(requesting_user_id)
            )

            devices = await conn.fetch(
                "SELECT * FROM device_sync WHERE user_id = $1 ORDER BY last_sync DESC",
                user_id
            )
            return devices

    # ===== TUTORIAL PROGRESS =====

    async def update_tutorial_progress(
        self,
        user_id: UUID,
        progress_data: Dict[str, Any]
    ) -> Optional[asyncpg.Record]:
        """
        Update tutorial progress with PROPER RLS context
        SECURITY: Users can only update their own progress
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(user_id)
            )

            progress = await conn.fetchrow(
                """
                INSERT INTO tutorial_progress
                (user_id, tutorial_module, progress_percentage, completed, completed_at)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (user_id, tutorial_module) 
                DO UPDATE SET 
                    progress_percentage = EXCLUDED.progress_percentage,
                    completed = EXCLUDED.completed,
                    completed_at = EXCLUDED.completed_at,
                    updated_at = NOW()
                RETURNING *
                """,
                user_id, progress_data["tutorial_module"], progress_data.get("progress_percentage", 0),
                progress_data.get("completed", False), progress_data.get("completed_at")
            )
            return progress

    async def get_user_tutorial_progress(
        self,
        user_id: UUID,
        requesting_user_id: UUID
    ) -> List[asyncpg.Record]:
        """
        Get user tutorial progress with PROPER RLS context
        SECURITY: Users can only see their own progress
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(requesting_user_id)
            )

            progress = await conn.fetch(
                "SELECT * FROM tutorial_progress WHERE user_id = $1 ORDER BY created_at",
                user_id
            )
            return progress

    # ===== CONTENT SUMMARIZATION =====

    async def update_content_summary(
        self,
        analysis_id: UUID,
        user_id: UUID,
        summary_data: Dict[str, Any]
    ) -> Optional[asyncpg.Record]:
        """
        Update content summary in AI analysis
        SECURITY: Users can only update their own content analysis
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(user_id)
            )

            analysis = await conn.fetchrow(
                """
                UPDATE ai_content_analysis 
                SET content_summary = $1, summary_confidence = $2, updated_at = NOW()
                WHERE id = $3 AND user_id = $4
                RETURNING *
                """,
                summary_data.get("content_summary"), summary_data.get("summary_confidence"),
                analysis_id, user_id
            )
            return analysis

    # ===== HEALTH CHECK =====

    async def health_check(
        self,
        user_id: UUID
    ) -> bool:
        """
        Basic health check to verify CRUD operations work
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(user_id)
            )

            try:
                # Simple query to verify connection and RLS context
                result = await conn.fetchval("SELECT 1")
                return result == 1
            except Exception:
                return False

# Instantiate the class - FOLLOWING EXACT SAME PATTERN
phase6_missing_features_crud = Phase6MissingFeaturesCRUD()
