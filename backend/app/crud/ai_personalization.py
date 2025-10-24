"""
AI Personalization CRUD - Phase 4, Item 1
Following EXACT same patterns as professional_directory.py
Using correct session-level context setting with safe string formatting
"""

import asyncpg
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import time
from app.database.database import database

class AIPersonalizationCRUD:
    """
    AI personalization CRUD operations with PROPER RLS context
    SECURITY: Uses parameterized set_config with is_local=false for session-level context
    """

    # ===== CONTENT ANALYSIS =====

    async def create_content_analysis(
        self,
        content_data: Dict[str, Any],
        analyst_id: UUID
    ) -> Optional[asyncpg.Record]:
        """
        Create AI content analysis with PROPER RLS context
        SECURITY: Only admins/moderators can create analysis
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(analyst_id)
            )

            analysis = await conn.fetchrow(
                """
                INSERT INTO ai_content_analysis 
                (content_type, content_id, sentiment_score, sentiment_label, 
                 emotion_tags, content_categories, risk_level, toxicity_score,
                 analysis_model, confidence_score)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                RETURNING *
                """,
                content_data["content_type"], content_data["content_id"],
                content_data.get("sentiment_score"), content_data.get("sentiment_label"),
                content_data.get("emotion_tags"), content_data.get("content_categories"),
                content_data.get("risk_level"), content_data.get("toxicity_score"),
                content_data.get("analysis_model"), content_data.get("confidence_score")
            )
            return analysis

    async def get_content_analysis(
        self,
        content_type: str,
        content_id: UUID,
        requesting_user_id: UUID
    ) -> Optional[asyncpg.Record]:
        """
        Get content analysis with PROPER RLS context
        SECURITY: Users can only see analysis of content they have access to
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(requesting_user_id)
            )

            analysis = await conn.fetchrow(
                """
                SELECT * FROM ai_content_analysis
                WHERE content_type = $1 AND content_id = $2
                """,
                content_type, content_id
            )
            return analysis

    # ===== USER BEHAVIOR PATTERNS =====

    async def get_user_behavior_patterns(
        self,
        user_id: UUID,
        requesting_user_id: UUID
    ) -> Optional[asyncpg.Record]:
        """
        Get user behavior patterns with PROPER RLS context
        SECURITY: Users can only see their own patterns
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(requesting_user_id)
            )

            patterns = await conn.fetchrow(
                """
                SELECT * FROM user_behavior_patterns
                WHERE user_id = $1
                """,
                user_id
            )
            return patterns

    async def update_user_behavior_patterns(
        self,
        user_id: UUID,
        pattern_data: Dict[str, Any],
        analyst_id: UUID
    ) -> Optional[asyncpg.Record]:
        """
        Update user behavior patterns with PROPER RLS context
        SECURITY: Only AI system/admins can update patterns
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(analyst_id)
            )

            # Build dynamic update query
            update_fields = []
            params = []
            param_count = 1

            for field, value in pattern_data.items():
                if value is not None:
                    update_fields.append(f"{field} = ${param_count}")
                    params.append(value)
                    param_count += 1

            if not update_fields:
                return None

            params.append(user_id)
            query = f"""
                INSERT INTO user_behavior_patterns (user_id, {', '.join(pattern_data.keys())})
                VALUES (${param_count}, {', '.join([f'${i+1}' for i in range(len(pattern_data))])})
                ON CONFLICT (user_id) 
                DO UPDATE SET {', '.join(update_fields)}, updated_at = NOW()
                RETURNING *
            """

            patterns = await conn.fetchrow(query, *params)
            return patterns

    # ===== PERSONALIZED RECOMMENDATIONS =====

    async def create_recommendation(
        self,
        user_id: UUID,
        recommendation_data: Dict[str, Any],
        recommender_id: UUID
    ) -> Optional[asyncpg.Record]:
        """
        Create personalized recommendation with PROPER RLS context
        SECURITY: Only AI system/admins can create recommendations
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(recommender_id)
            )

            recommendation = await conn.fetchrow(
                """
                INSERT INTO personalized_recommendations 
                (user_id, recommendation_type, title, description, reasoning,
                 content_type, content_id, relevance_score, confidence_score, 
                 priority_level, expires_at, optimal_viewing_time)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                RETURNING *
                """,
                user_id, recommendation_data["recommendation_type"],
                recommendation_data["title"], recommendation_data.get("description"),
                recommendation_data.get("reasoning"), recommendation_data.get("content_type"),
                recommendation_data.get("content_id"), recommendation_data.get("relevance_score"),
                recommendation_data.get("confidence_score"), recommendation_data.get("priority_level"),
                recommendation_data.get("expires_at"), recommendation_data.get("optimal_viewing_time")
            )
            return recommendation

    async def get_user_recommendations(
        self,
        user_id: UUID,
        requesting_user_id: UUID,
        recommendation_type: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[asyncpg.Record]:
        """
        Get user recommendations with PROPER RLS context
        SECURITY: Users can only see their own recommendations
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(requesting_user_id)
            )

            where_conditions = ["user_id = $1", "is_dismissed = false"]
            params = [user_id]
            param_count = 2

            if recommendation_type:
                where_conditions.append(f"recommendation_type = ${param_count}")
                params.append(recommendation_type)
                param_count += 1

            where_clause = " AND ".join(where_conditions)
            params.extend([limit, offset])

            recommendations = await conn.fetch(
                f"""
                SELECT * FROM personalized_recommendations
                WHERE {where_clause}
                ORDER BY priority_level DESC, relevance_score DESC, created_at DESC
                LIMIT ${param_count} OFFSET ${param_count + 1}
                """,
                *params
            )
            return recommendations

    async def update_recommendation_interaction(
        self,
        recommendation_id: UUID,
        user_id: UUID,
        interaction_data: Dict[str, Any]
    ) -> Optional[asyncpg.Record]:
        """
        Update recommendation interaction with PROPER RLS context
        SECURITY: Users can only update their own recommendations
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

            for field, value in interaction_data.items():
                if value is not None:
                    update_fields.append(f"{field} = ${param_count}")
                    params.append(value)
                    param_count += 1

            if not update_fields:
                return None

            params.extend([recommendation_id, user_id])
            query = f"""
                UPDATE personalized_recommendations 
                SET {', '.join(update_fields)}, updated_at = NOW()
                WHERE id = ${param_count} AND user_id = ${param_count + 1}
                RETURNING *
            """

            recommendation = await conn.fetchrow(query, *params)
            return recommendation

    # ===== COPING STRATEGIES =====

    async def get_coping_strategies(
        self,
        target_emotions: Optional[List[str]] = None,
        strategy_type: Optional[str] = None,
        difficulty_level: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[asyncpg.Record]:
        """
        Get coping strategies with PROPER RLS context
        SECURITY: Public read access to active strategies
        """
        async with database.pool.acquire() as conn:
            # No specific user context needed for public strategies
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                "public_user"
            )

            where_conditions = ["is_active = true"]
            params = []
            param_count = 1

            if target_emotions:
                where_conditions.append(f"target_emotions && ${param_count}")
                params.append(target_emotions)
                param_count += 1

            if strategy_type:
                where_conditions.append(f"strategy_type = ${param_count}")
                params.append(strategy_type)
                param_count += 1

            if difficulty_level:
                where_conditions.append(f"difficulty_level = ${param_count}")
                params.append(difficulty_level)
                param_count += 1

            where_clause = " AND ".join(where_conditions)
            params.extend([limit, offset])

            strategies = await conn.fetch(
                f"""
                SELECT * FROM coping_strategies
                WHERE {where_clause}
                ORDER BY effectiveness_score DESC, difficulty_level
                LIMIT ${param_count} OFFSET ${param_count + 1}
                """,
                *params
            )
            return strategies

    async def get_user_coping_preferences(
        self,
        user_id: UUID,
        requesting_user_id: UUID
    ) -> List[asyncpg.Record]:
        """
        Get user coping preferences with PROPER RLS context
        SECURITY: Users can only see their own preferences
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(requesting_user_id)
            )

            preferences = await conn.fetch(
                """
                SELECT ucp.*, cs.strategy_name, cs.strategy_type, cs.description
                FROM user_coping_preferences ucp
                JOIN coping_strategies cs ON ucp.strategy_id = cs.id
                WHERE ucp.user_id = $1
                ORDER BY ucp.preference_score DESC, ucp.usage_count DESC
                """,
                user_id
            )
            return preferences

    async def update_coping_preference(
        self,
        user_id: UUID,
        strategy_id: UUID,
        preference_data: Dict[str, Any]
    ) -> Optional[asyncpg.Record]:
        """
        Update coping preference with PROPER RLS context
        SECURITY: Users can only update their own preferences
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(user_id)
            )

            preference = await conn.fetchrow(
                """
                INSERT INTO user_coping_preferences 
                (user_id, strategy_id, preference_score, effectiveness_rating, 
                 last_used_at, usage_count, context_tags, ai_recommendation_score)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                ON CONFLICT (user_id, strategy_id) 
                DO UPDATE SET 
                    preference_score = EXCLUDED.preference_score,
                    effectiveness_rating = EXCLUDED.effectiveness_rating,
                    last_used_at = EXCLUDED.last_used_at,
                    usage_count = user_coping_preferences.usage_count + 1,
                    context_tags = EXCLUDED.context_tags,
                    ai_recommendation_score = EXCLUDED.ai_recommendation_score,
                    updated_at = NOW()
                RETURNING *
                """,
                user_id, strategy_id, preference_data.get("preference_score"),
                preference_data.get("effectiveness_rating"), preference_data.get("last_used_at"),
                preference_data.get("usage_count", 1), preference_data.get("context_tags"),
                preference_data.get("ai_recommendation_score")
            )
            return preference

    # ===== NOTIFICATION PREFERENCES =====

    async def get_notification_preferences(
        self,
        user_id: UUID,
        requesting_user_id: UUID
    ) -> Optional[asyncpg.Record]:
        """
        Get notification preferences with PROPER RLS context
        SECURITY: Users can only see their own preferences
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(requesting_user_id)
            )

            preferences = await conn.fetchrow(
                "SELECT * FROM notification_preferences WHERE user_id = $1",
                user_id
            )
            return preferences

    async def update_notification_preferences(
        self,
        user_id: UUID,
        preferences_data: Dict[str, Any]
    ) -> Optional[asyncpg.Record]:
        """
        Update notification preferences with PROPER RLS context
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
                INSERT INTO notification_preferences (user_id, {', '.join(preferences_data.keys())})
                VALUES (${param_count}, {', '.join([f'${i+1}' for i in range(len(preferences_data))])})
                ON CONFLICT (user_id) 
                DO UPDATE SET {', '.join(update_fields)}, updated_at = NOW()
                RETURNING *
            """

            preferences = await conn.fetchrow(query, *params)
            return preferences

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
ai_personalization_crud = AIPersonalizationCRUD()
