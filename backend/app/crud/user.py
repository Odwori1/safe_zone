import asyncpg
from typing import Optional, List
from uuid import UUID
from app.database.database import database
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password

class CRUDUser:
    async def get(self, user_id: UUID) -> Optional[asyncpg.Record]:
        """Get user by ID"""
        async with database.pool.acquire() as conn:
            return await conn.fetchrow(
                "SELECT * FROM users WHERE id = $1",
                user_id
            )

    async def get_by_email(self, email: str) -> Optional[asyncpg.Record]:
        """Get user by email"""
        async with database.pool.acquire() as conn:
            return await conn.fetchrow(
                "SELECT * FROM users WHERE email = $1",
                email
            )

    async def get_by_username(self, username: str) -> Optional[asyncpg.Record]:
        """Get user by username"""
        async with database.pool.acquire() as conn:
            return await conn.fetchrow(
                "SELECT * FROM users WHERE username = $1",
                username
            )

    async def create(self, user_in: UserCreate) -> asyncpg.Record:
        """Create new user"""
        hashed_password = get_password_hash(user_in.password)

        async with database.pool.acquire() as conn:
            return await conn.fetchrow(
                """
                INSERT INTO users (email, username, hashed_password, full_name, timezone, locale)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING *
                """,
                user_in.email, user_in.username, hashed_password,
                user_in.full_name, user_in.timezone, user_in.locale
            )

    async def update(self, user_id: UUID, user_in) -> Optional[asyncpg.Record]:
        """Update user - handles both Pydantic models and dicts"""
        # Convert Pydantic model to dict if needed
        if hasattr(user_in, 'dict'):
            update_data = user_in.dict(exclude_unset=True)
        else:
            update_data = user_in

        if not update_data:
            return await self.get(user_id)

        update_fields = []
        values = []
        index = 1

        for field, value in update_data.items():
            update_fields.append(f"{field} = ${index}")
            values.append(value)
            index += 1

        values.append(user_id)
        query = f"""
            UPDATE users
            SET {', '.join(update_fields)}, updated_at = NOW()
            WHERE id = ${index}
            RETURNING *
        """

        async with database.pool.acquire() as conn:
            return await conn.fetchrow(query, *values)

    async def authenticate(self, email: str, password: str) -> Optional[asyncpg.Record]:
        """Authenticate user"""
        user = await self.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user['hashed_password']):
            return None
        return user

    async def update_last_login(self, user_id: UUID) -> None:
        """Update user's last login timestamp"""
        async with database.pool.acquire() as conn:
            await conn.execute(
                "UPDATE users SET last_login = NOW() WHERE id = $1",
                user_id
            )

    async def search_users(
        self,
        current_user_id: UUID,
        search_query: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
        include_unverified: bool = False
    ) -> List[asyncpg.Record]:
        """
        Search users with RLS enforcement
        """
        print(f"🔍 CRUD SEARCH: current_user_id={current_user_id}, query='{search_query}', include_unverified={include_unverified}")
        
        query_parts = [
            """
            SELECT
                id,
                username,
                email,
                full_name,
                bio,
                profile_picture,
                is_helper,
                helper_specialties,
                is_verified,
                is_active,  -- ADD THIS LINE
                created_at
            FROM users
            WHERE id != $1
            AND is_active = true
            """
        ]

        params = [current_user_id]
        param_count = 1

        if not include_unverified:
            query_parts.append("AND is_verified = true")

        if search_query:
            param_count += 1
            query_parts.append(f"AND (username ILIKE ${param_count} OR email ILIKE ${param_count} OR full_name ILIKE ${param_count})")
            params.append(f"%{search_query}%")

        query_parts.append("ORDER BY created_at DESC")
        param_count += 1
        query_parts.append(f"LIMIT ${param_count}")
        params.append(limit)
        param_count += 1
        query_parts.append(f"OFFSET ${param_count}")
        params.append(offset)

        final_query = "\n".join(query_parts)
        print(f"📝 EXECUTING QUERY: {final_query}")
        print(f"📝 WITH PARAMS: {params}")

        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_current_user_id($1);", str(current_user_id))
            users = await conn.fetch(final_query, *params)
            print(f"✅ CRUD SEARCH FOUND: {len(users)} users")
            return users

    async def get_user_suggestions(
        self,
        current_user_id: UUID,
        limit: int = 10
    ) -> List[asyncpg.Record]:
        """
        Get user discovery suggestions based on activity
        """
        query = """
            SELECT
                id,
                username,
                full_name,
                bio,
                profile_picture,
                is_helper,
                helper_specialties,
                is_verified,
                is_active,  -- ADD THIS LINE
                created_at
            FROM users
            WHERE id != $1
            AND is_active = true
            ORDER BY last_login DESC NULLS LAST, created_at DESC
            LIMIT $2
        """

        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_current_user_id($1);", str(current_user_id))
            return await conn.fetch(query, current_user_id, limit)

# Create instance
user_crud = CRUDUser()
