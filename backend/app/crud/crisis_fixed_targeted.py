import asyncpg
from typing import Optional, List, Dict, Any
from uuid import UUID
from fastapi import HTTPException, status
from app.database.database import database

class CRUDCrisisResources:
    # ========== EXISTING METHODS ==========
    async def get_all_resources(self, category: Optional[str] = None,
                              geographic_scope: Optional[str] = None,
                              limit: int = 50, offset: int = 0) -> List[asyncpg.Record]:
        """Get all crisis resources with optional filtering"""
        async with database.pool.acquire() as conn:
            query = "SELECT * FROM crisis_resources WHERE is_active = true"
            params = []
            param_count = 0

            if category:
                param_count += 1
                query += f" AND category = ${param_count}"
                params.append(category)

            if geographic_scope:
                param_count += 1
                query += f" AND (geographic_scope = 'global' OR geographic_scope = ${param_count})"
                params.append(geographic_scope)

            query += " ORDER BY priority DESC, created_at DESC"
            param_count += 1
            query += f" LIMIT ${param_count}"
            params.append(limit)
            param_count += 1
            query += f" OFFSET ${param_count}"
            params.append(offset)

            return await conn.fetch(query, *params)

    async def get_resource(self, resource_id: UUID) -> Optional[asyncpg.Record]:
        """Get crisis resource by ID"""
        async with database.pool.acquire() as conn:
            return await conn.fetchrow(
                "SELECT * FROM crisis_resources WHERE id = $1 AND is_active = true",
                resource_id
            )

    async def get_resources_by_category(self, category: str) -> List[asyncpg.Record]:
        """Get crisis resources by category"""
        async with database.pool.acquire() as conn:
            return await conn.fetch(
                "SELECT * FROM crisis_resources WHERE category = $1 AND is_active = true ORDER BY priority DESC",
                category
            )

    async def search_resources(self, query: str, limit: int = 20) -> List[asyncpg.Record]:
        """Search crisis resources by name, description, or tags"""
        async with database.pool.acquire() as conn:
            search_term = f"%{query}%"
            return await conn.fetch(
                """
                SELECT * FROM crisis_resources
                WHERE is_active = true
                AND (name ILIKE $1 OR description ILIKE $1 OR $2::text = ANY(tags::text[]))
                ORDER BY priority DESC
                LIMIT $3
                """,
                search_term, query, limit
            )

    async def get_emergency_contacts(self, user_id: UUID) -> List[asyncpg.Record]:
        """Get emergency contacts for user"""
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            return await conn.fetch(
                "SELECT * FROM emergency_contacts WHERE user_id = $1 ORDER BY is_primary DESC, created_at DESC",
                user_id
            )

    async def get_emergency_contact(self, contact_id: UUID, user_id: UUID) -> Optional[asyncpg.Record]:
        """Get emergency contact by ID (user-specific)"""
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            return await conn.fetchrow(
                "SELECT * FROM emergency_contacts WHERE id = $1 AND user_id = $2",
                contact_id, user_id
            )

    async def create_emergency_contact(self, user_id: UUID, contact_in) -> Optional[asyncpg.Record]:
        """Create new emergency contact"""
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            
            # If this is set as primary, unset any existing primary contacts
            if hasattr(contact_in, 'is_primary') and contact_in.is_primary:
                await conn.execute(
                    "UPDATE emergency_contacts SET is_primary = false WHERE user_id = $1",
                    user_id
                )

            return await conn.fetchrow(
                """
                INSERT INTO emergency_contacts
                (user_id, name, relationship, phone_number, email, is_primary, can_receive_alerts, notes)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING *
                """,
                user_id, contact_in.name, contact_in.relationship, contact_in.phone_number,
                contact_in.email, contact_in.is_primary, contact_in.can_receive_alerts,
                contact_in.notes
            )

    async def update_emergency_contact(self, contact_id: UUID, user_id: UUID, contact_in) -> Optional[asyncpg.Record]:
        """Update emergency contact - only by owner"""
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            
            if hasattr(contact_in, 'dict'):
                update_data = contact_in.dict(exclude_unset=True)
            else:
                update_data = contact_in

            if not update_data:
                return await self.get_emergency_contact(contact_id, user_id)

            # If setting as primary, unset any existing primary contacts
            if update_data.get('is_primary'):
                await conn.execute(
                    "UPDATE emergency_contacts SET is_primary = false WHERE user_id = $1 AND id != $2",
                    user_id, contact_id
                )

            update_fields = []
            values = []
            index = 1

            for field, value in update_data.items():
                update_fields.append(f"{field} = ${index}")
                values.append(value)
                index += 1

            values.extend([contact_id, user_id])
            query = f"""
                UPDATE emergency_contacts
                SET {', '.join(update_fields)}, updated_at = NOW()
                WHERE id = ${index} AND user_id = ${index + 1}
                RETURNING *
            """

            return await conn.fetchrow(query, *values)

    async def delete_emergency_contact(self, contact_id: UUID, user_id: UUID) -> bool:
        """Delete emergency contact - only by owner"""
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            result = await conn.execute(
                "DELETE FROM emergency_contacts WHERE id = $1 AND user_id = $2",
                contact_id, user_id
            )
            return "DELETE 1" in result

    async def get_user_crisis_preferences(self, user_id: UUID) -> Optional[asyncpg.Record]:
        """Get user crisis preferences"""
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            return await conn.fetchrow(
                "SELECT * FROM user_crisis_preferences WHERE user_id = $1",
                user_id
            )

    async def create_user_crisis_preferences(self, user_id: UUID, preferences_in) -> Optional[asyncpg.Record]:
        """Create user crisis preferences"""
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            return await conn.fetchrow(
                """
                INSERT INTO user_crisis_preferences
                (user_id, preferred_language, country_code, emergency_contact_instructions,
                 medical_information, consent_to_contact)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING *
                """,
                user_id, preferences_in.preferred_language, preferences_in.country_code,
                preferences_in.emergency_contact_instructions, preferences_in.medical_information,
                preferences_in.consent_to_contact
            )

    async def update_user_crisis_preferences(self, user_id: UUID, preferences_in) -> Optional[asyncpg.Record]:
        """Update user crisis preferences"""
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            
            if hasattr(preferences_in, 'dict'):
                update_data = preferences_in.dict(exclude_unset=True)
            else:
                update_data = preferences_in

            if not update_data:
                return await self.get_user_crisis_preferences(user_id)

            update_fields = []
            values = []
            index = 1

            for field, value in update_data.items():
                update_fields.append(f"{field} = ${index}")
                values.append(value)
                index += 1

            values.append(user_id)
            query = f"""
                UPDATE user_crisis_preferences
                SET {', '.join(update_fields)}, updated_at = NOW()
                WHERE user_id = ${index}
                RETURNING *
            """

            return await conn.fetchrow(query, *values)

    # ... (rest of the methods follow the same pattern - adding await conn.execute("SELECT set_current_user_id($1);", str(user_id)))
    # Safety Plans Methods
    async def create_safety_plan(self, user_id: UUID, plan_data) -> Optional[asyncpg.Record]:
        """Create a new safety plan for user"""
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            return await conn.fetchrow(
                """
                INSERT INTO safety_plans (
                    user_id, plan_name, warning_signs, internal_coping_strategies,
                    external_coping_strategies, social_contacts, professional_contacts,
                    environment_safety, reasons_for_living
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                RETURNING *
                """,
                user_id,
                plan_data.plan_name,
                plan_data.warning_signs,
                plan_data.internal_coping_strategies,
                plan_data.external_coping_strategies,
                plan_data.social_contacts,
                plan_data.professional_contacts,
                plan_data.environment_safety,
                plan_data.reasons_for_living
            )

    async def get_safety_plans(self, user_id: UUID) -> List[asyncpg.Record]:
        """Get all safety plans for user"""
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            return await conn.fetch(
                "SELECT * FROM safety_plans WHERE user_id = $1 ORDER BY is_active DESC, updated_at DESC",
                user_id
            )

    # Add the same fix to ALL methods that have user_id parameter...
    # For brevity, I'm showing the pattern - all methods need await conn.execute("SELECT set_current_user_id($1);", str(user_id))

# Create instance
crisis_crud = CRUDCrisisResources()
