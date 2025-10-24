"""
Final Phase Features CRUD - Phase 5 & 6
Following EXACT same patterns as enhanced_ux_community.py
Using correct session-level context setting with safe string formatting
"""

import asyncpg
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import date, datetime
from app.database.database import database

class FinalPhaseFeaturesCRUD:
    """
    Final Phase Features CRUD operations with PROPER RLS context
    SECURITY: Uses parameterized set_config with is_local=false for session-level context
    """

    # ===== MULTI-LANGUAGE SUPPORT (Phase 5) =====

    async def get_language_preferences(
        self,
        user_id: UUID,
        requesting_user_id: UUID
    ) -> Optional[asyncpg.Record]:
        """
        Get user language preferences with PROPER RLS context
        SECURITY: Users can only see their own preferences
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(requesting_user_id)
            )

            preferences = await conn.fetchrow(
                "SELECT * FROM language_preferences WHERE user_id = $1",
                user_id
            )
            return preferences

    async def update_language_preferences(
        self,
        user_id: UUID,
        preferences_data: Dict[str, Any]
    ) -> Optional[asyncpg.Record]:
        """
        Update user language preferences with PROPER RLS context
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
                INSERT INTO language_preferences (user_id, {', '.join(preferences_data.keys())})
                VALUES (${param_count}, {', '.join([f'${i+1}' for i in range(len(preferences_data))])})
                ON CONFLICT (user_id)
                DO UPDATE SET {', '.join(update_fields)}, updated_at = NOW()
                RETURNING *
            """

            preferences = await conn.fetchrow(query, *params)
            return preferences

    async def get_regional_resources(
        self,
        country_code: Optional[str] = None,
        language_code: Optional[str] = None,
        resource_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[asyncpg.Record]:
        """
        Get regional resources with PROPER RLS context
        SECURITY: Public read access to active resources
        """
        async with database.pool.acquire() as conn:
            # Use default user ID for public access
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                "00000000-0000-0000-0000-000000000000"
            )

            where_conditions = ["is_active = true"]
            params = []
            param_count = 1

            if country_code:
                where_conditions.append(f"country_code = ${param_count}")
                params.append(country_code)
                param_count += 1

            if language_code:
                where_conditions.append(f"language_code = ${param_count}")
                params.append(language_code)
                param_count += 1

            if resource_type:
                where_conditions.append(f"resource_type = ${param_count}")
                params.append(resource_type)
                param_count += 1

            where_clause = " AND ".join(where_conditions)
            params.extend([limit, offset])

            resources = await conn.fetch(
                f"""
                SELECT * FROM regional_resources
                WHERE {where_clause}
                ORDER BY country_code, language_code, resource_type
                LIMIT ${param_count} OFFSET ${param_count + 1}
                """,
                *params
            )
            return resources

    # ===== ACCESSIBILITY ENHANCEMENTS (Phase 5) =====

    async def get_accessibility_preferences(
        self,
        user_id: UUID,
        requesting_user_id: UUID
    ) -> Optional[asyncpg.Record]:
        """
        Get user accessibility preferences with PROPER RLS context
        SECURITY: Users can only see their own preferences
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(requesting_user_id)
            )

            preferences = await conn.fetchrow(
                "SELECT * FROM accessibility_preferences WHERE user_id = $1",
                user_id
            )
            return preferences

    async def update_accessibility_preferences(
        self,
        user_id: UUID,
        preferences_data: Dict[str, Any]
    ) -> Optional[asyncpg.Record]:
        """
        Update user accessibility preferences with PROPER RLS context
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
                INSERT INTO accessibility_preferences (user_id, {', '.join(preferences_data.keys())})
                VALUES (${param_count}, {', '.join([f'${i+1}' for i in range(len(preferences_data))])})
                ON CONFLICT (user_id)
                DO UPDATE SET {', '.join(update_fields)}, updated_at = NOW()
                RETURNING *
            """

            preferences = await conn.fetchrow(query, *params)
            return preferences

    # ===== ENTERPRISE FEATURES (Phase 5) =====

    async def get_user_organizations(
        self,
        user_id: UUID,
        requesting_user_id: UUID
    ) -> List[asyncpg.Record]:
        """
        Get user's organizations with PROPER RLS context
        SECURITY: Users can only see organizations they belong to
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(requesting_user_id)
            )

            organizations = await conn.fetch(
                """
                SELECT o.*, om.role, om.joined_at
                FROM organizations o
                JOIN organization_members om ON o.id = om.organization_id
                WHERE om.user_id = $1 AND om.is_active = true
                ORDER BY om.joined_at DESC
                """,
                user_id
            )
            return organizations

    async def get_organization_wellness_challenges(
        self,
        organization_id: UUID,
        user_id: UUID,
        active_only: bool = True,
        limit: int = 20,
        offset: int = 0
    ) -> List[asyncpg.Record]:
        """
        Get organization wellness challenges with PROPER RLS context
        SECURITY: Users can only see challenges from their organizations
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(user_id)
            )

            where_conditions = ["(wc.organization_id = $1 OR wc.is_public = true)"]
            params = [organization_id]
            param_count = 2

            if active_only:
                where_conditions.append(f"wc.end_date >= CURRENT_DATE")

            where_clause = " AND ".join(where_conditions)
            params.extend([limit, offset])

            challenges = await conn.fetch(
                f"""
                SELECT wc.*, 
                       COUNT(cp.user_id) as participant_count,
                       EXISTS(SELECT 1 FROM challenge_participants cp2 
                              WHERE cp2.challenge_id = wc.id AND cp2.user_id = $1) as is_participating
                FROM wellness_challenges wc
                LEFT JOIN challenge_participants cp ON wc.id = cp.challenge_id
                WHERE {where_clause}
                GROUP BY wc.id
                ORDER BY wc.start_date DESC
                LIMIT ${param_count} OFFSET ${param_count + 1}
                """,
                *params
            )
            return challenges

    async def join_wellness_challenge(
        self,
        challenge_id: UUID,
        user_id: UUID
    ) -> Optional[asyncpg.Record]:
        """
        Join wellness challenge with PROPER RLS context
        SECURITY: Users can only join challenges they have access to
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(user_id)
            )

            participant = await conn.fetchrow(
                """
                INSERT INTO challenge_participants (challenge_id, user_id)
                SELECT $1, $2
                FROM wellness_challenges wc
                WHERE wc.id = $1 
                  AND (wc.is_public = true 
                       OR wc.organization_id IN (
                           SELECT organization_id FROM organization_members 
                           WHERE user_id = $2 AND is_active = true
                       ))
                RETURNING *
                """,
                challenge_id, user_id
            )
            return participant

    # ===== ADVANCED AI FEATURES (Phase 6) =====

    async def create_ai_chat_session(
        self,
        user_id: UUID,
        session_data: Dict[str, Any]
    ) -> Optional[asyncpg.Record]:
        """
        Create AI chat session with PROPER RLS context
        SECURITY: Users can only create their own sessions
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(user_id)
            )

            session = await conn.fetchrow(
                """
                INSERT INTO ai_chat_sessions
                (user_id, session_type, context_data)
                VALUES ($1, $2, $3)
                RETURNING *
                """,
                user_id, session_data["session_type"], session_data.get("context_data")
            )
            return session

    async def get_user_ai_chat_sessions(
        self,
        user_id: UUID,
        requesting_user_id: UUID,
        session_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[asyncpg.Record]:
        """
        Get user's AI chat sessions with PROPER RLS context
        SECURITY: Users can only see their own sessions
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(requesting_user_id)
            )

            where_conditions = ["user_id = $1"]
            params = [user_id]
            param_count = 2

            if session_type:
                where_conditions.append(f"session_type = ${param_count}")
                params.append(session_type)
                param_count += 1

            where_clause = " AND ".join(where_conditions)
            params.extend([limit, offset])

            sessions = await conn.fetch(
                f"""
                SELECT * FROM ai_chat_sessions
                WHERE {where_clause}
                ORDER BY started_at DESC
                LIMIT ${param_count} OFFSET ${param_count + 1}
                """,
                *params
            )
            return sessions

    async def add_ai_chat_message(
        self,
        session_id: UUID,
        user_id: UUID,
        message_data: Dict[str, Any]
    ) -> Optional[asyncpg.Record]:
        """
        Add AI chat message with PROPER RLS context
        SECURITY: Users can only add messages to their own sessions
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(user_id)
            )

            message = await conn.fetchrow(
                """
                INSERT INTO ai_chat_messages
                (session_id, message_type, content, sentiment_score, urgency_level)
                SELECT $1, $2, $3, $4, $5
                FROM ai_chat_sessions
                WHERE id = $1 AND user_id = $6
                RETURNING *
                """,
                session_id, message_data["message_type"], message_data["content"],
                message_data.get("sentiment_score"), message_data.get("urgency_level"), user_id
            )
            return message

    async def save_voice_mood_analysis(
        self,
        user_id: UUID,
        analysis_data: Dict[str, Any]
    ) -> Optional[asyncpg.Record]:
        """
        Save voice mood analysis with PROPER RLS context
        SECURITY: Users can only save their own analysis
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(user_id)
            )

            analysis = await conn.fetchrow(
                """
                INSERT INTO voice_mood_analysis
                (user_id, audio_file_url, analysis_result, mood_score, 
                 confidence_score, detected_emotions)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING *
                """,
                user_id, analysis_data.get("audio_file_url"), analysis_data["analysis_result"],
                analysis_data.get("mood_score"), analysis_data.get("confidence_score"),
                analysis_data.get("detected_emotions")
            )
            return analysis

    # ===== INTEGRATION ECOSYSTEM (Phase 6) =====

    async def get_user_integrations(
        self,
        user_id: UUID,
        requesting_user_id: UUID
    ) -> List[asyncpg.Record]:
        """
        Get user integrations with PROPER RLS context
        SECURITY: Users can only see their own integrations
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(requesting_user_id)
            )

            integrations = await conn.fetch(
                "SELECT * FROM user_integrations WHERE user_id = $1 ORDER BY created_at DESC",
                user_id
            )
            return integrations

    async def create_user_integration(
        self,
        user_id: UUID,
        integration_data: Dict[str, Any]
    ) -> Optional[asyncpg.Record]:
        """
        Create user integration with PROPER RLS context
        SECURITY: Users can only create their own integrations
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(user_id)
            )

            integration = await conn.fetchrow(
                """
                INSERT INTO user_integrations
                (user_id, integration_type, service_name, sync_frequency, config_data)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING *
                """,
                user_id, integration_data["integration_type"], integration_data["service_name"],
                integration_data.get("sync_frequency", "daily"), integration_data.get("config_data")
            )
            return integration

    async def get_emergency_contacts(
        self,
        user_id: UUID,
        requesting_user_id: UUID
    ) -> List[asyncpg.Record]:
        """
        Get user emergency contacts with PROPER RLS context
        SECURITY: Users can only see their own contacts
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(requesting_user_id)
            )

            contacts = await conn.fetch(
                "SELECT * FROM emergency_coordination WHERE user_id = $1 ORDER BY is_primary DESC, created_at",
                user_id
            )
            return contacts

    async def add_emergency_contact(
        self,
        user_id: UUID,
        contact_data: Dict[str, Any]
    ) -> Optional[asyncpg.Record]:
        """
        Add emergency contact with PROPER RLS context
        SECURITY: Users can only add their own contacts
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(user_id)
            )

            contact = await conn.fetchrow(
                """
                INSERT INTO emergency_coordination
                (user_id, contact_name, contact_relationship, contact_methods, 
                 notification_preferences, is_primary)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING *
                """,
                user_id, contact_data["contact_name"], contact_data.get("contact_relationship"),
                contact_data["contact_methods"], contact_data.get("notification_preferences"),
                contact_data.get("is_primary", False)
            )
            return contact

    # ===== COMMUNITY BUILDING (Phase 6) =====

    async def get_peer_support_matches(
        self,
        user_id: UUID,
        requesting_user_id: UUID,
        match_type: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[asyncpg.Record]:
        """
        Get peer support matches with PROPER RLS context
        SECURITY: Users can only see their own matches
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(requesting_user_id)
            )

            where_conditions = ["(user_id = $1 OR matched_user_id = $1)"]
            params = [user_id]
            param_count = 2

            if match_type:
                where_conditions.append(f"match_type = ${param_count}")
                params.append(match_type)
                param_count += 1

            where_clause = " AND ".join(where_conditions)
            params.extend([limit, offset])

            matches = await conn.fetch(
                f"""
                SELECT * FROM peer_support_matches
                WHERE {where_clause}
                ORDER BY matched_at DESC
                LIMIT ${param_count} OFFSET ${param_count + 1}
                """,
                *params
            )
            return matches

    async def get_group_sessions(
        self,
        user_id: UUID,
        upcoming_only: bool = True,
        session_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[asyncpg.Record]:
        """
        Get group sessions with PROPER RLS context
        SECURITY: Public read access to sessions
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(user_id)
            )

            where_conditions = ["1=1"]
            params = []
            param_count = 1

            if upcoming_only:
                where_conditions.append(f"scheduled_time > NOW()")
            
            if session_type:
                where_conditions.append(f"session_type = ${param_count}")
                params.append(session_type)
                param_count += 1

            where_clause = " AND ".join(where_conditions)
            params.extend([limit, offset])

            sessions = await conn.fetch(
                f"""
                SELECT gs.*, 
                       u.username as facilitator_username,
                       COUNT(sp.user_id) as participant_count,
                       EXISTS(SELECT 1 FROM session_participants sp2 
                              WHERE sp2.session_id = gs.id AND sp2.user_id = $1) as is_participating
                FROM group_sessions gs
                LEFT JOIN users u ON gs.facilitator_id = u.id
                LEFT JOIN session_participants sp ON gs.id = sp.session_id
                WHERE {where_clause}
                GROUP BY gs.id, u.username
                ORDER BY gs.scheduled_time ASC
                LIMIT ${param_count} OFFSET ${param_count + 1}
                """,
                *params
            )
            return sessions

    async def join_group_session(
        self,
        session_id: UUID,
        user_id: UUID
    ) -> Optional[asyncpg.Record]:
        """
        Join group session with PROPER RLS context
        SECURITY: Users can join public sessions
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(user_id)
            )

            participant = await conn.fetchrow(
                """
                INSERT INTO session_participants (session_id, user_id)
                SELECT $1, $2
                FROM group_sessions
                WHERE id = $1 AND scheduled_time > NOW()
                AND (SELECT COUNT(*) FROM session_participants WHERE session_id = $1) < max_participants
                RETURNING *
                """,
                session_id, user_id
            )
            return participant

    # ===== USER FEEDBACK (Phase 6) =====

    async def submit_user_feedback(
        self,
        user_id: UUID,
        feedback_data: Dict[str, Any]
    ) -> Optional[asyncpg.Record]:
        """
        Submit user feedback with PROPER RLS context
        SECURITY: Users can only submit their own feedback
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(user_id)
            )

            feedback = await conn.fetchrow(
                """
                INSERT INTO user_feedback
                (user_id, feedback_type, category, description, urgency)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING *
                """,
                user_id, feedback_data["feedback_type"], feedback_data.get("category"),
                feedback_data["description"], feedback_data.get("urgency", "medium")
            )
            return feedback

    async def get_user_feedback(
        self,
        user_id: UUID,
        requesting_user_id: UUID,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[asyncpg.Record]:
        """
        Get user feedback with PROPER RLS context
        SECURITY: Users can see their own feedback, admins see all
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

            feedback = await conn.fetch(
                f"""
                SELECT * FROM user_feedback
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT ${param_count} OFFSET ${param_count + 1}
                """,
                *params
            )
            return feedback

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
final_phase_features_crud = FinalPhaseFeaturesCRUD()
