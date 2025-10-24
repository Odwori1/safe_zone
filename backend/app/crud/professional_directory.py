"""
Professional Directory CRUD - FOLLOWING EXACT SAME PATTERN AS enhanced_moderation.py
Using correct session-level context setting with safe string formatting
"""

import asyncpg
from typing import Optional, List, Dict, Any
from uuid import UUID
from app.database.database import database

class ProfessionalDirectoryCRUD:
    """
    Professional directory CRUD operations with PROPER RLS context
    SECURITY: Uses parameterized set_config with is_local=false for session-level context
    """

    # ===== PROFESSIONAL PROFILES =====

    async def create_professional_profile(
        self,
        user_id: UUID,
        profile_data: Dict[str, Any]
    ) -> Optional[asyncpg.Record]:
        """
        Create a professional profile with PROPER RLS context
        """
        async with database.pool.acquire() as conn:
            # FIX: Use set_config with is_local=false for session-level context
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(user_id)
            )

            profile = await conn.fetchrow(
                """
                INSERT INTO professional_profiles 
                (user_id, professional_title, license_number, license_state, 
                 years_of_experience, hourly_rate, bio, approach, specialties,
                 professional_email, professional_phone, website_url)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                RETURNING *
                """,
                user_id, profile_data["professional_title"], profile_data.get("license_number"),
                profile_data.get("license_state"), profile_data.get("years_of_experience"),
                profile_data.get("hourly_rate"), profile_data.get("bio"), 
                profile_data.get("approach"), profile_data.get("specialties"),
                profile_data.get("professional_email"), profile_data.get("professional_phone"),
                profile_data.get("website_url")
            )
            return profile

    async def get_professional_profile(
        self,
        user_id: UUID,
        requesting_user_id: UUID
    ) -> Optional[asyncpg.Record]:
        """
        Get professional profile with PROPER RLS context
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(requesting_user_id)
            )

            profile = await conn.fetchrow(
                """
                SELECT pp.*, u.username, u.email, u.full_name
                FROM professional_profiles pp
                JOIN users u ON pp.user_id = u.id
                WHERE pp.user_id = $1
                """,
                user_id
            )
            return profile

    async def update_professional_profile(
        self,
        user_id: UUID,
        profile_data: Dict[str, Any]
    ) -> Optional[asyncpg.Record]:
        """
        Update professional profile with PROPER RLS context
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

            for field, value in profile_data.items():
                if value is not None:
                    update_fields.append(f"{field} = ${param_count}")
                    params.append(value)
                    param_count += 1

            if not update_fields:
                return None

            params.append(user_id)
            query = f"""
                UPDATE professional_profiles 
                SET {', '.join(update_fields)}, updated_at = NOW()
                WHERE user_id = ${param_count}
                RETURNING *
            """

            profile = await conn.fetchrow(query, *params)
            return profile

    async def get_professional_directory(
        self,
        requesting_user_id: UUID,
        specialties: Optional[List[str]] = None,
        session_types: Optional[List[str]] = None,
        min_rating: Optional[float] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[asyncpg.Record]:
        """
        Get professional directory listings with PROPER RLS context
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(requesting_user_id)
            )

            # Build dynamic WHERE conditions
            where_conditions = ["pd.verification_status = 'verified'", "pd.is_active = true"]
            params = []
            param_count = 1

            if specialties:
                where_conditions.append(f"pd.specialties && ${param_count}")
                params.append(specialties)
                param_count += 1

            if session_types:
                where_conditions.append(f"pd.session_types && ${param_count}")
                params.append(session_types)
                param_count += 1

            if min_rating is not None:
                where_conditions.append(f"pd.average_rating >= ${param_count}")
                params.append(min_rating)
                param_count += 1

            where_clause = " AND ".join(where_conditions)
            params.extend([limit, offset])

            professionals = await conn.fetch(
                f"""
                SELECT * FROM professional_directory pd
                WHERE {where_clause}
                ORDER BY pd.average_rating DESC NULLS LAST, pd.review_count DESC
                LIMIT ${param_count} OFFSET ${param_count + 1}
                """,
                *params
            )
            return professionals

    # ===== PROFESSIONAL VERIFICATIONS =====

    async def create_professional_verification(
        self,
        user_id: UUID,
        verification_data: Dict[str, Any]
    ) -> Optional[asyncpg.Record]:
        """
        Create professional verification document with PROPER RLS context
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(user_id)
            )

            # First get the professional profile ID
            profile = await conn.fetchrow(
                "SELECT id FROM professional_profiles WHERE user_id = $1",
                user_id
            )

            if not profile:
                return None

            verification = await conn.fetchrow(
                """
                INSERT INTO professional_verifications
                (professional_id, document_type, document_name, s3_key, file_size, mime_type)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING *
                """,
                profile["id"], verification_data["document_type"], 
                verification_data["document_name"], verification_data["s3_key"],
                verification_data.get("file_size"), verification_data.get("mime_type")
            )
            return verification

    async def get_professional_verifications(
        self,
        user_id: UUID,
        requesting_user_id: UUID
    ) -> List[asyncpg.Record]:
        """
        Get professional verifications with PROPER RLS context
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(requesting_user_id)
            )

            verifications = await conn.fetch(
                """
                SELECT pv.* 
                FROM professional_verifications pv
                JOIN professional_profiles pp ON pv.professional_id = pp.id
                WHERE pp.user_id = $1
                ORDER BY pv.created_at DESC
                """,
                user_id
            )
            return verifications

    # ===== PROFESSIONAL AVAILABILITY =====

    async def create_availability_slot(
        self,
        user_id: UUID,
        availability_data: Dict[str, Any]
    ) -> Optional[asyncpg.Record]:
        """
        Create availability slot with PROPER RLS context
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(user_id)
            )

            # Get the professional profile ID
            profile = await conn.fetchrow(
                "SELECT id FROM professional_profiles WHERE user_id = $1",
                user_id
            )

            if not profile:
                return None

            availability = await conn.fetchrow(
                """
                INSERT INTO professional_availability
                (professional_id, day_of_week, start_time, end_time, timezone,
                 slot_duration_minutes, buffer_minutes, is_recurring, valid_from, valid_until)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                RETURNING *
                """,
                profile["id"], availability_data["day_of_week"], 
                availability_data["start_time"], availability_data["end_time"],
                availability_data.get("timezone", "UTC"),
                availability_data.get("slot_duration_minutes", 60),
                availability_data.get("buffer_minutes", 15),
                availability_data.get("is_recurring", True),
                availability_data.get("valid_from"), availability_data.get("valid_until")
            )
            return availability

    async def get_professional_availability(
        self,
        professional_id: UUID,
        requesting_user_id: UUID
    ) -> List[asyncpg.Record]:
        """
        Get professional availability with PROPER RLS context
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(requesting_user_id)
            )

            availability = await conn.fetch(
                """
                SELECT * FROM professional_availability
                WHERE professional_id = $1 AND is_active = true
                ORDER BY day_of_week, start_time
                """,
                professional_id
            )
            return availability

    # ===== BASIC HEALTH CHECK =====

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
professional_directory_crud = ProfessionalDirectoryCRUD()
