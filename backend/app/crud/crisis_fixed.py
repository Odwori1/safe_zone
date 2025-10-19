import asyncpg
from typing import Optional, List, Dict, Any
from uuid import UUID
from app.database.database import database

class CRUDCrisisResources:
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
            return await conn.fetch(
                "SELECT * FROM emergency_contacts WHERE user_id = $1 ORDER BY is_primary DESC, created_at DESC",
                user_id
            )

    async def get_emergency_contact(self, contact_id: UUID, user_id: UUID) -> Optional[asyncpg.Record]:
        """Get emergency contact by ID (user-specific)"""
        async with database.pool.acquire() as conn:
            return await conn.fetchrow(
                "SELECT * FROM emergency_contacts WHERE id = $1 AND user_id = $2",
                contact_id, user_id
            )

    async def create_emergency_contact(self, user_id: UUID, contact_in) -> Optional[asyncpg.Record]:
        """Create new emergency contact"""
        async with database.pool.acquire() as conn:
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
        if hasattr(contact_in, 'dict'):
            update_data = contact_in.dict(exclude_unset=True)
        else:
            update_data = contact_in

        if not update_data:
            return await self.get_emergency_contact(contact_id, user_id)

        # If setting as primary, unset any existing primary contacts
        if update_data.get('is_primary'):
            async with database.pool.acquire() as conn:
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

        async with database.pool.acquire() as conn:
            return await conn.fetchrow(query, *values)

    async def delete_emergency_contact(self, contact_id: UUID, user_id: UUID) -> bool:
        """Delete emergency contact - only by owner"""
        async with database.pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM emergency_contacts WHERE id = $1 AND user_id = $2",
                contact_id, user_id
            )
            return "DELETE 1" in result

    async def get_user_crisis_preferences(self, user_id: UUID) -> Optional[asyncpg.Record]:
        """Get user crisis preferences"""
        async with database.pool.acquire() as conn:
            return await conn.fetchrow(
                "SELECT * FROM user_crisis_preferences WHERE user_id = $1",
                user_id
            )

    async def create_user_crisis_preferences(self, user_id: UUID, preferences_in) -> Optional[asyncpg.Record]:
        """Create user crisis preferences"""
        async with database.pool.acquire() as conn:
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

        async with database.pool.acquire() as conn:
            return await conn.fetchrow(query, *values)

    async def get_recommended_resources(self, user_id: UUID, content: Optional[str] = None, 
                                      mood: Optional[str] = None, category: Optional[str] = None,
                                      limit: int = 5) -> List[asyncpg.Record]:
        """Get recommended crisis resources based on content, mood, and user preferences"""
        async with database.pool.acquire() as conn:
            # Get user preferences to personalize recommendations
            preferences = await self.get_user_crisis_preferences(user_id)
            user_country = preferences['country_code'] if preferences else None
            user_language = preferences['preferred_language'] if preferences else 'en'
            
            base_query = """
                SELECT * FROM crisis_resources 
                WHERE is_active = true
            """
            params = []
            param_count = 0
            
            # Filter by geographic scope
            if user_country:
                param_count += 1
                base_query += f" AND (geographic_scope = 'global' OR geographic_scope = ${param_count})"
                params.append(user_country.lower())
            
            # Filter by language - FIXED: Proper JSONB array checking
            param_count += 1
            base_query += f" AND (languages ? ${param_count} OR languages ? 'en')"
            params.append(user_language)
            
            # Simple content-based recommendation logic
            emergency_keywords = ['suicide', 'kill myself', 'end it all', 'harm myself', 'emergency', 'urgent']
            crisis_keywords = ['depressed', 'anxious', 'overwhelmed', 'crisis', 'help', 'support']
            
            if content:
                content_lower = content.lower()
                # Check for emergency keywords
                if any(keyword in content_lower for keyword in emergency_keywords):
                    base_query += " AND (category = 'suicide_prevention' OR category = 'emergency')"
                # Check for crisis keywords  
                elif any(keyword in content_lower for keyword in crisis_keywords):
                    base_query += " AND (category = 'crisis_support' OR category = 'mental_health')"
            
            # Filter by specific category if provided
            if category:
                param_count += 1
                base_query += f" AND category = ${param_count}"
                params.append(category)
            
            # Mood-based recommendations
            if mood:
                mood_lower = mood.lower()
                if mood_lower in ['sad', 'depressed', 'hopeless']:
                    base_query += " AND category IN ('suicide_prevention', 'crisis_support', 'mental_health')"
                elif mood_lower in ['anxious', 'panicked', 'overwhelmed']:
                    base_query += " AND category IN ('crisis_support', 'mental_health')"
                elif mood_lower in ['angry', 'frustrated']:
                    base_query += " AND category IN ('crisis_support', 'mental_health')"
            
            base_query += " ORDER BY priority DESC, created_at DESC"
            param_count += 1
            base_query += f" LIMIT ${param_count}"
            params.append(limit)
            
            return await conn.fetch(base_query, *params)

    async def count_resources(self, category: Optional[str] = None, 
                            geographic_scope: Optional[str] = None) -> int:
        """Count crisis resources with optional filtering"""
        async with database.pool.acquire() as conn:
            query = "SELECT COUNT(*) FROM crisis_resources WHERE is_active = true"
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
            
            return await conn.fetchval(query, *params)

    async def count_user_contacts(self, user_id: UUID) -> int:
        """Count user's emergency contacts"""
        async with database.pool.acquire() as conn:
            return await conn.fetchval(
                "SELECT COUNT(*) FROM emergency_contacts WHERE user_id = $1",
                user_id
            )

# Create instance
crisis_crud = CRUDCrisisResources()
