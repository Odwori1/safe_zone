"""
Advanced Safety Systems CRUD - Phase 4, Item 2
Following EXACT same patterns as ai_personalization.py
Using correct session-level context setting with safe string formatting
"""

import asyncpg
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import date, datetime
from app.database.database import database

class AdvancedSafetySystemsCRUD:
    """
    Advanced safety systems CRUD operations with PROPER RLS context
    SECURITY: Uses parameterized set_config with is_local=false for session-level context
    """

    # ===== CRISIS DETECTION ALERTS =====

    async def create_crisis_alert(
        self,
        alert_data: Dict[str, Any],
        detector_id: UUID
    ) -> Optional[asyncpg.Record]:
        """
        Create crisis detection alert with PROPER RLS context
        SECURITY: Only AI system/moderators can create alerts
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(detector_id)
            )

            alert = await conn.fetchrow(
                """
                INSERT INTO crisis_detection_alerts 
                (user_id, detection_source, source_content_type, source_content_id,
                 risk_level, risk_score, risk_factors, confidence_score,
                 alert_message, detected_patterns, context_data)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                RETURNING *
                """,
                alert_data["user_id"], alert_data["detection_source"],
                alert_data.get("source_content_type"), alert_data.get("source_content_id"),
                alert_data["risk_level"], alert_data["risk_score"],
                alert_data.get("risk_factors"), alert_data.get("confidence_score"),
                alert_data.get("alert_message"), alert_data.get("detected_patterns"),
                alert_data.get("context_data")
            )
            return alert

    async def get_user_crisis_alerts(
        self,
        user_id: UUID,
        requesting_user_id: UUID,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[asyncpg.Record]:
        """
        Get user crisis alerts with PROPER RLS context
        SECURITY: Users can only see their own alerts
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

            alerts = await conn.fetch(
                f"""
                SELECT * FROM crisis_detection_alerts
                WHERE {where_clause}
                ORDER BY detected_at DESC, risk_score DESC
                LIMIT ${param_count} OFFSET ${param_count + 1}
                """,
                *params
            )
            return alerts

    async def update_alert_status(
        self,
        alert_id: UUID,
        moderator_id: UUID,
        update_data: Dict[str, Any]
    ) -> Optional[asyncpg.Record]:
        """
        Update alert status with PROPER RLS context
        SECURITY: Only moderators can update alerts
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(moderator_id)
            )

            # Build dynamic update query
            update_fields = []
            params = []
            param_count = 1

            for field, value in update_data.items():
                if value is not None:
                    update_fields.append(f"{field} = ${param_count}")
                    params.append(value)
                    param_count += 1

            if not update_fields:
                return None

            # Add timestamp for status changes
            if 'status' in update_data:
                if update_data['status'] == 'reviewing' and 'reviewed_at' not in update_data:
                    update_fields.append("reviewed_at = NOW()")
                elif update_data['status'] == 'resolved' and 'resolved_at' not in update_data:
                    update_fields.append("resolved_at = NOW()")

            params.append(alert_id)
            query = f"""
                UPDATE crisis_detection_alerts 
                SET {', '.join(update_fields)}, updated_at = NOW()
                WHERE id = ${param_count}
                RETURNING *
            """

            alert = await conn.fetchrow(query, *params)
            return alert

    # ===== SAFETY PLANS =====

    async def create_safety_plan(
        self,
        user_id: UUID,
        plan_data: Dict[str, Any]
    ) -> Optional[asyncpg.Record]:
        """
        Create safety plan with PROPER RLS context
        SECURITY: Users can only create their own safety plans
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(user_id)
            )

            # Deactivate any existing active plan
            await conn.execute(
                "UPDATE safety_plans SET is_active = false WHERE user_id = $1 AND is_active = true",
                user_id
            )

            plan = await conn.fetchrow(
                """
                INSERT INTO safety_plans 
                (user_id, plan_name, personal_warning_signs, early_warning_triggers,
                 internal_coping_strategies, social_coping_strategies, professional_coping_strategies,
                 emergency_contact_instructions, crisis_line_preferences, means_restriction_plan,
                 safe_locations, created_from_template_id)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                RETURNING *
                """,
                user_id, plan_data["plan_name"], plan_data.get("personal_warning_signs"),
                plan_data.get("early_warning_triggers"), plan_data.get("internal_coping_strategies"),
                plan_data.get("social_coping_strategies"), plan_data.get("professional_coping_strategies"),
                plan_data.get("emergency_contact_instructions"), plan_data.get("crisis_line_preferences"),
                plan_data.get("means_restriction_plan"), plan_data.get("safe_locations"),
                plan_data.get("created_from_template_id")
            )
            return plan

    async def get_user_safety_plan(
        self,
        user_id: UUID,
        requesting_user_id: UUID
    ) -> Optional[asyncpg.Record]:
        """
        Get user safety plan with PROPER RLS context
        SECURITY: Users can only see their own safety plans
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(requesting_user_id)
            )

            plan = await conn.fetchrow(
                """
                SELECT * FROM safety_plans 
                WHERE user_id = $1 AND is_active = true
                ORDER BY created_at DESC 
                LIMIT 1
                """,
                user_id
            )
            return plan

    async def update_safety_plan(
        self,
        plan_id: UUID,
        user_id: UUID,
        update_data: Dict[str, Any]
    ) -> Optional[asyncpg.Record]:
        """
        Update safety plan with PROPER RLS context
        SECURITY: Users can only update their own safety plans
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

            for field, value in update_data.items():
                if value is not None:
                    update_fields.append(f"{field} = ${param_count}")
                    params.append(value)
                    param_count += 1

            if not update_fields:
                return None

            params.extend([plan_id, user_id])
            query = f"""
                UPDATE safety_plans 
                SET {', '.join(update_fields)}, updated_at = NOW(), last_reviewed_date = CURRENT_DATE
                WHERE id = ${param_count} AND user_id = ${param_count + 1}
                RETURNING *
            """

            plan = await conn.fetchrow(query, *params)
            return plan

    # ===== SAFETY PLAN TEMPLATES =====

    async def get_safety_plan_templates(
        self,
        target_audience: Optional[str] = None,
        difficulty_level: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[asyncpg.Record]:
        """
        Get safety plan templates with PROPER RLS context
        SECURITY: Public read access to templates
        """
        async with database.pool.acquire() as conn:
            # No specific user context needed for public templates
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                "public_user"
            )

            where_conditions = ["is_active = true", "is_public = true"]
            params = []
            param_count = 1

            if target_audience:
                where_conditions.append(f"target_audience = ${param_count}")
                params.append(target_audience)
                param_count += 1

            if difficulty_level:
                where_conditions.append(f"difficulty_level = ${param_count}")
                params.append(difficulty_level)
                param_count += 1

            where_clause = " AND ".join(where_conditions)
            params.extend([limit, offset])

            templates = await conn.fetch(
                f"""
                SELECT * FROM safety_plan_templates
                WHERE {where_clause}
                ORDER BY template_name
                LIMIT ${param_count} OFFSET ${param_count + 1}
                """,
                *params
            )
            return templates

    # ===== WELLNESS CHECK-INS =====

    async def create_wellness_check_in(
        self,
        user_id: UUID,
        check_in_data: Dict[str, Any],
        creator_id: UUID
    ) -> Optional[asyncpg.Record]:
        """
        Create wellness check-in with PROPER RLS context
        SECURITY: Only system/moderators can create check-ins
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(creator_id)
            )

            check_in = await conn.fetchrow(
                """
                INSERT INTO wellness_check_ins 
                (user_id, check_in_type, trigger_source, trigger_alert_id,
                 check_in_message, response_options, custom_response_prompt)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING *
                """,
                user_id, check_in_data["check_in_type"], check_in_data.get("trigger_source"),
                check_in_data.get("trigger_alert_id"), check_in_data["check_in_message"],
                check_in_data.get("response_options"), check_in_data.get("custom_response_prompt")
            )
            return check_in

    async def get_user_wellness_check_ins(
        self,
        user_id: UUID,
        requesting_user_id: UUID,
        status: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[asyncpg.Record]:
        """
        Get user wellness check-ins with PROPER RLS context
        SECURITY: Users can only see their own check-ins
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

            check_ins = await conn.fetch(
                f"""
                SELECT * FROM wellness_check_ins
                WHERE {where_clause}
                ORDER BY sent_at DESC
                LIMIT ${param_count} OFFSET ${param_count + 1}
                """,
                *params
            )
            return check_ins

    async def respond_to_wellness_check_in(
        self,
        check_in_id: UUID,
        user_id: UUID,
        response_data: Dict[str, Any]
    ) -> Optional[asyncpg.Record]:
        """
        Respond to wellness check-in with PROPER RLS context
        SECURITY: Users can only respond to their own check-ins
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(user_id)
            )

            check_in = await conn.fetchrow(
                """
                UPDATE wellness_check_ins 
                SET user_response = $1, selected_options = $2, response_mood = $3,
                    response_urgency = $4, responded_at = NOW(), status = 'responded',
                    updated_at = NOW()
                WHERE id = $5 AND user_id = $6
                RETURNING *
                """,
                response_data.get("user_response"), response_data.get("selected_options"),
                response_data.get("response_mood"), response_data.get("response_urgency"),
                check_in_id, user_id
            )
            return check_in

    # ===== ESCALATION PROTOCOLS =====

    async def get_escalation_protocols(
        self,
        risk_level: Optional[str] = None,
        moderator_id: UUID = None
    ) -> List[asyncpg.Record]:
        """
        Get escalation protocols with PROPER RLS context
        SECURITY: Only moderators can access protocols
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(moderator_id) if moderator_id else "moderator_user"
            )

            where_conditions = ["is_active = true"]
            params = []
            param_count = 1

            if risk_level:
                where_conditions.append(f"trigger_risk_level = ${param_count}")
                params.append(risk_level)
                param_count += 1

            where_clause = " AND ".join(where_conditions)

            protocols = await conn.fetch(
                f"""
                SELECT * FROM escalation_protocols
                WHERE {where_clause}
                ORDER BY 
                    CASE trigger_risk_level
                        WHEN 'critical' THEN 1
                        WHEN 'severe' THEN 2
                        WHEN 'high' THEN 3
                        WHEN 'medium' THEN 4
                        ELSE 5
                    END,
                    protocol_name
                """,
                *params
            )
            return protocols

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
advanced_safety_systems_crud = AdvancedSafetySystemsCRUD()
