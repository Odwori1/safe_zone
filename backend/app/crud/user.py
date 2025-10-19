import asyncpg
from typing import Optional
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

# Create instance
user_crud = CRUDUser()
