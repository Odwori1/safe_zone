import asyncpg
from typing import Optional, List, Dict, Any
from uuid import UUID
from fastapi import HTTPException, status
from app.database.database import database

class CRUDCrisisResources:
    # ... keep all existing methods for resources, contacts, preferences ...
    
    # UPDATED SAFETY PLANS METHODS - USING ACTUAL SCHEMA
    async def create_safety_plan(self, user_id: UUID, plan_data) -> Optional[asyncpg.Record]:
        """Create a new safety plan for user - USING ACTUAL SCHEMA"""
        async with database.pool.acquire() as conn:
            return await conn.fetchrow(
                """
                INSERT INTO safety_plans (
                    user_id, plan_name, plan_version, is_active,
                    personal_warning_signs, early_warning_triggers,
                    internal_coping_strategies, social_coping_strategies, professional_coping_strategies,
                    emergency_contact_instructions, crisis_line_preferences,
                    means_restriction_plan, safe_locations,
                    last_reviewed_date, next_review_date
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                RETURNING *
                """,
                user_id,
                plan_data.plan_name,
                plan_data.plan_version if hasattr(plan_data, 'plan_version') else 1,
                plan_data.is_active if hasattr(plan_data, 'is_active') else True,
                plan_data.personal_warning_signs if hasattr(plan_data, 'personal_warning_signs') else [],
                plan_data.early_warning_triggers if hasattr(plan_data, 'early_warning_triggers') else [],
                plan_data.internal_coping_strategies if hasattr(plan_data, 'internal_coping_strategies') else [],
                plan_data.social_coping_strategies if hasattr(plan_data, 'social_coping_strategies') else [],
                plan_data.professional_coping_strategies if hasattr(plan_data, 'professional_coping_strategies') else [],
                plan_data.emergency_contact_instructions if hasattr(plan_data, 'emergency_contact_instructions') else None,
                plan_data.crisis_line_preferences if hasattr(plan_data, 'crisis_line_preferences') else [],
                plan_data.means_restriction_plan if hasattr(plan_data, 'means_restriction_plan') else None,
                plan_data.safe_locations if hasattr(plan_data, 'safe_locations') else [],
                plan_data.last_reviewed_date if hasattr(plan_data, 'last_reviewed_date') else None,
                plan_data.next_review_date if hasattr(plan_data, 'next_review_date') else None
            )

    async def get_safety_plans(self, user_id: UUID) -> List[asyncpg.Record]:
        """Get all safety plans for user"""
        async with database.pool.acquire() as conn:
            return await conn.fetch(
                "SELECT * FROM safety_plans WHERE user_id = $1 ORDER BY is_active DESC, updated_at DESC",
                user_id
            )

    async def get_active_safety_plan(self, user_id: UUID) -> Optional[asyncpg.Record]:
        """Get user's active safety plan"""
        async with database.pool.acquire() as conn:
            return await conn.fetchrow(
                "SELECT * FROM safety_plans WHERE user_id = $1 AND is_active = TRUE ORDER BY updated_at DESC LIMIT 1",
                user_id
            )

    # UPDATED CRISIS ALERTS METHODS - FIX LOCATION DATA
    async def create_crisis_alert(self, user_id: UUID, alert_data) -> Optional[asyncpg.Record]:
        """Create a new crisis alert - FIXED LOCATION DATA"""
        async with database.pool.acquire() as conn:
            location_json = alert_data.location_data if hasattr(alert_data, 'location_data') else None
            
            return await conn.fetchrow(
                """
                INSERT INTO crisis_alerts (
                    user_id, alert_type, severity_level, message, location_data
                ) VALUES ($1, $2, $3, $4, $5)
                RETURNING *
                """,
                user_id,
                alert_data.alert_type,
                alert_data.severity_level,
                alert_data.message if hasattr(alert_data, 'message') else None,
                location_json
            )

# Create instance
crisis_crud_fixed = CRUDCrisisResources()
