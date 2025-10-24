"""
Enhanced UX & Community Management CRUD - Phase 4, Items 3 & 4
Following EXACT same patterns as advanced_safety_systems.py
Using correct session-level context setting with safe string formatting
"""

import asyncpg
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import date, datetime
from app.database.database import database

class EnhancedUXCommunityCRUD:
    """
    Enhanced UX & Community Management CRUD operations with PROPER RLS context
    SECURITY: Uses parameterized set_config with is_local=false for session-level context
    """

    # ===== USER UI PREFERENCES (Item 3) =====

    async def get_user_ui_preferences(
        self,
        user_id: UUID,
        requesting_user_id: UUID
    ) -> Optional[asyncpg.Record]:
        """
        Get user UI preferences with PROPER RLS context
        SECURITY: Users can only see their own preferences
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(requesting_user_id)
            )

            preferences = await conn.fetchrow(
                "SELECT * FROM user_ui_preferences WHERE user_id = $1",
                user_id
            )
            return preferences

    async def update_user_ui_preferences(
        self,
        user_id: UUID,
        preferences_data: Dict[str, Any]
    ) -> Optional[asyncpg.Record]:
        """
        Update user UI preferences with PROPER RLS context
        SECURITY: Users can only update their own preferences
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(user_id)
            )

            # Build dynamic update query
            update_fields = []
            params = []
            param_count = 1

            for field, value in preferences_data.items():
                if value is not None:
                    update_fields.append(f"{field} = ${param_count}")
                    params.append(value)
                    param_count += 1

            if not update_fields:
                return None

            params.append(user_id)
            query = f"""
                INSERT INTO user_ui_preferences (user_id, {', '.join(preferences_data.keys())})
                VALUES (${param_count}, {', '.join([f'${i+1}' for i in range(len(preferences_data))])})
                ON CONFLICT (user_id)
                DO UPDATE SET {', '.join(update_fields)}, updated_at = NOW()
                RETURNING *
            """

            preferences = await conn.fetchrow(query, *params)
            return preferences

    # ===== OFFLINE CONTENT (Item 3) =====

    async def get_offline_content(
        self,
        user_id: UUID,
        requesting_user_id: UUID,
        content_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[asyncpg.Record]:
        """
        Get user's offline content with PROPER RLS context
        SECURITY: Users can only see their own offline content
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(requesting_user_id)
            )

            where_conditions = ["user_id = $1"]
            params = [user_id]
            param_count = 2

            if content_type:
                where_conditions.append(f"content_type = ${param_count}")
                params.append(content_type)
                param_count += 1

            where_clause = " AND ".join(where_conditions)
            params.extend([limit, offset])

            content = await conn.fetch(
                f"""
                SELECT * FROM offline_content
                WHERE {where_clause}
                ORDER BY last_accessed DESC, created_at DESC
                LIMIT ${param_count} OFFSET ${param_count + 1}
                """,
                *params
            )
            return content

    async def save_offline_content(
        self,
        user_id: UUID,
        content_data: Dict[str, Any]
    ) -> Optional[asyncpg.Record]:
        """
        Save content for offline access with PROPER RLS context
        SECURITY: Users can only save their own offline content
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(user_id)
            )

            content = await conn.fetchrow(
                """
                INSERT INTO offline_content
                (user_id, content_type, content_id, content_data, file_size_bytes, expires_at)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (user_id, content_type, content_id)
                DO UPDATE SET
                    content_data = EXCLUDED.content_data,
                    file_size_bytes = EXCLUDED.file_size_bytes,
                    expires_at = EXCLUDED.expires_at,
                    last_accessed = NOW(),
                    access_count = offline_content.access_count + 1,
                    updated_at = NOW()
                RETURNING *
                """,
                user_id, content_data["content_type"], content_data["content_id"],
                content_data["content_data"], content_data.get("file_size_bytes"),
                content_data.get("expires_at")
            )
            return content

    async def delete_offline_content(
        self,
        content_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        Delete offline content with PROPER RLS context
        SECURITY: Users can only delete their own offline content
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(user_id)
            )

            result = await conn.execute(
                "DELETE FROM offline_content WHERE id = $1 AND user_id = $2",
                content_id, user_id
            )
            return "DELETE 1" in result

    # ===== DATA EXPORT JOBS (Item 3) =====

    async def create_data_export_job(
        self,
        user_id: UUID,
        export_data: Dict[str, Any]
    ) -> Optional[asyncpg.Record]:
        """
        Create data export job with PROPER RLS context
        SECURITY: Users can only create their own export jobs
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(user_id)
            )

            job = await conn.fetchrow(
                """
                INSERT INTO data_export_jobs
                (user_id, export_format, data_categories, date_range_start, date_range_end)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING *
                """,
                user_id, export_data["export_format"], export_data.get("data_categories"),
                export_data.get("date_range_start"), export_data.get("date_range_end")
            )
            return job

    async def get_user_export_jobs(
        self,
        user_id: UUID,
        requesting_user_id: UUID,
        status: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[asyncpg.Record]:
        """
        Get user's data export jobs with PROPER RLS context
        SECURITY: Users can only see their own export jobs
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(requesting_user_id)
            )

            where_conditions = ["user_id = $1"]
            params = [user_id]
            param_count = 2

            if status:
                where_conditions.append(f"status = ${param_count}")
                params.append(status)
                param_count += 1

            where_clause = " AND ".join(where_conditions)
            params.extend([limit, offset])

            jobs = await conn.fetch(
                f"""
                SELECT * FROM data_export_jobs
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT ${param_count} OFFSET ${param_count + 1}
                """,
                *params
            )
            return jobs

    async def get_export_job_by_token(
        self,
        access_token: UUID,
        requesting_user_id: UUID
    ) -> Optional[asyncpg.Record]:
        """
        Get export job by access token with PROPER RLS context
        SECURITY: Users can only access their own export jobs via token
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(requesting_user_id)
            )

            job = await conn.fetchrow(
                "SELECT * FROM data_export_jobs WHERE access_token = $1 AND user_id = $2",
                access_token, requesting_user_id
            )
            return job

    # ===== COMMUNITY ANALYTICS (Item 4) =====

    async def get_community_analytics(
        self,
        moderator_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 30,
        offset: int = 0
    ) -> List[asyncpg.Record]:
        """
        Get community analytics with PROPER RLS context
        SECURITY: Only moderators/admins can access analytics
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(moderator_id)
            )

            where_conditions = ["1=1"]
            params = []
            param_count = 1

            if start_date:
                where_conditions.append(f"date >= ${param_count}")
                params.append(start_date)
                param_count += 1

            if end_date:
                where_conditions.append(f"date <= ${param_count}")
                params.append(end_date)
                param_count += 1

            where_clause = " AND ".join(where_conditions)
            params.extend([limit, offset])

            analytics = await conn.fetch(
                f"""
                SELECT * FROM community_analytics
                WHERE {where_clause}
                ORDER BY date DESC
                LIMIT ${param_count} OFFSET ${param_count + 1}
                """,
                *params
            )
            return analytics

    # ===== USER REPUTATION (Item 4) =====

    async def get_user_reputation(
        self,
        user_id: UUID,
        requesting_user_id: UUID
    ) -> Optional[asyncpg.Record]:
        """
        Get user reputation with PROPER RLS context
        SECURITY: Users can see their own, moderators can see all
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(requesting_user_id)
            )

            reputation = await conn.fetchrow(
                "SELECT * FROM user_reputation_scores WHERE user_id = $1",
                user_id
            )
            return reputation

    # ===== CONFLICT RESOLUTION (Item 4) =====

    async def get_user_conflict_cases(
        self,
        user_id: UUID,
        requesting_user_id: UUID,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[asyncpg.Record]:
        """
        Get user's conflict resolution cases with PROPER RLS context
        SECURITY: Users can only see cases they're involved in
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(requesting_user_id)
            )

            where_conditions = ["(reporter_id = $1 OR reported_user_id = $1 OR assigned_moderator_id = $1)"]
            params = [user_id]
            param_count = 2

            if status:
                where_conditions.append(f"status = ${param_count}")
                params.append(status)
                param_count += 1

            where_clause = " AND ".join(where_conditions)
            params.extend([limit, offset])

            cases = await conn.fetch(
                f"""
                SELECT * FROM conflict_resolution_cases
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT ${param_count} OFFSET ${param_count + 1}
                """,
                *params
            )
            return cases

    async def create_conflict_case(
        self,
        case_data: Dict[str, Any],
        reporter_id: UUID
    ) -> Optional[asyncpg.Record]:
        """
        Create conflict resolution case with PROPER RLS context
        SECURITY: Users can create cases, moderators have full access
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(reporter_id)
            )

            case = await conn.fetchrow(
                """
                INSERT INTO conflict_resolution_cases
                (case_type, title, description, priority, reporter_id, reported_user_id,
                 content_reference_type, content_reference_id)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING *
                """,
                case_data["case_type"], case_data["title"], case_data.get("description"),
                case_data.get("priority", "medium"), reporter_id, case_data.get("reported_user_id"),
                case_data.get("content_reference_type"), case_data.get("content_reference_id")
            )
            return case

    # ===== COMMUNITY EVENTS (Item 4) =====

    async def get_community_events(
        self,
        user_id: UUID,
        event_type: Optional[str] = None,
        upcoming_only: bool = True,
        limit: int = 20,
        offset: int = 0
    ) -> List[asyncpg.Record]:
        """
        Get community events with PROPER RLS context
        SECURITY: Public read access to events
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(user_id)
            )

            where_conditions = ["is_public = true"]
            params = []
            param_count = 1

            if upcoming_only:
                where_conditions.append(f"start_time >= NOW()")
            
            if event_type:
                where_conditions.append(f"event_type = ${param_count}")
                params.append(event_type)
                param_count += 1

            where_clause = " AND ".join(where_conditions)
            params.extend([limit, offset])

            events = await conn.fetch(
                f"""
                SELECT * FROM community_events
                WHERE {where_clause}
                ORDER BY start_time ASC
                LIMIT ${param_count} OFFSET ${param_count + 1}
                """,
                *params
            )
            return events

    # ===== MODERATOR TRAINING (Item 4) =====

    async def get_training_modules(
        self,
        user_id: UUID,
        required_for_role: Optional[str] = None,
        difficulty_level: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[asyncpg.Record]:
        """
        Get training modules with PROPER RLS context
        SECURITY: Public read access to active modules
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(user_id)
            )

            where_conditions = ["is_active = true"]
            params = []
            param_count = 1

            if required_for_role:
                where_conditions.append(f"required_for_role = ${param_count}")
                params.append(required_for_role)
                param_count += 1

            if difficulty_level:
                where_conditions.append(f"difficulty_level = ${param_count}")
                params.append(difficulty_level)
                param_count += 1

            where_clause = " AND ".join(where_conditions)
            params.extend([limit, offset])

            modules = await conn.fetch(
                f"""
                SELECT * FROM moderator_training_modules
                WHERE {where_clause}
                ORDER BY required_for_role, difficulty_level, title
                LIMIT ${param_count} OFFSET ${param_count + 1}
                """,
                *params
            )
            return modules

    async def get_user_training_progress(
        self,
        user_id: UUID,
        requesting_user_id: UUID,
        module_id: Optional[UUID] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[asyncpg.Record]:
        """
        Get user's training progress with PROPER RLS context
        SECURITY: Users can only see their own progress
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(requesting_user_id)
            )

            where_conditions = ["user_id = $1"]
            params = [user_id]
            param_count = 2

            if module_id:
                where_conditions.append(f"module_id = ${param_count}")
                params.append(module_id)
                param_count += 1

            where_clause = " AND ".join(where_conditions)
            params.extend([limit, offset])

            progress = await conn.fetch(
                f"""
                SELECT tp.*, tm.title, tm.content_type, tm.estimated_duration_minutes
                FROM moderator_training_progress tp
                JOIN moderator_training_modules tm ON tp.module_id = tm.id
                WHERE {where_clause}
                ORDER BY tp.status, tp.created_at DESC
                LIMIT ${param_count} OFFSET ${param_count + 1}
                """,
                *params
            )
            return progress

    async def update_training_progress(
        self,
        user_id: UUID,
        module_id: UUID,
        progress_data: Dict[str, Any]
    ) -> Optional[asyncpg.Record]:
        """
        Update training progress with PROPER RLS context
        SECURITY: Users can only update their own progress
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(user_id)
            )

            progress = await conn.fetchrow(
                """
                INSERT INTO moderator_training_progress
                (user_id, module_id, status, progress_percent, score, attempts, feedback)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (user_id, module_id)
                DO UPDATE SET
                    status = EXCLUDED.status,
                    progress_percent = EXCLUDED.progress_percent,
                    score = EXCLUDED.score,
                    attempts = EXCLUDED.attempts,
                    feedback = EXCLUDED.feedback,
                    updated_at = NOW(),
                    started_at = CASE 
                        WHEN moderator_training_progress.started_at IS NULL AND EXCLUDED.status != 'not_started' 
                        THEN NOW() 
                        ELSE moderator_training_progress.started_at 
                    END,
                    completed_at = CASE 
                        WHEN EXCLUDED.status = 'completed' OR EXCLUDED.status = 'passed' 
                        THEN NOW() 
                        ELSE NULL 
                    END
                RETURNING *
                """,
                user_id, module_id, progress_data.get("status"),
                progress_data.get("progress_percent"), progress_data.get("score"),
                progress_data.get("attempts", 0), progress_data.get("feedback")
            )
            return progress

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
enhanced_ux_community_crud = EnhancedUXCommunityCRUD()
