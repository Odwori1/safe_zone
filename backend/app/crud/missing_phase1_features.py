"""
Missing Phase 1 & 2 Features CRUD Operations
Fixing the gaps found in blueprint audit
"""

import asyncpg
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from app.database.database import database

class MissingPhase1FeaturesCRUD:
    """
    Missing Phase 1 & 2 Features CRUD with PROPER RLS context
    """

    # ===== PASSWORD RESET TOKENS =====

    async def create_password_reset_token(
        self,
        user_id: UUID,
        token_hash: str,
        expires_at: datetime
    ) -> Optional[asyncpg.Record]:
        """
        Create password reset token with PROPER RLS context
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(user_id)
            )

            token = await conn.fetchrow(
                """
                INSERT INTO password_reset_tokens
                (user_id, token_hash, expires_at)
                VALUES ($1, $2, $3)
                RETURNING *
                """,
                user_id, token_hash, expires_at
            )
            return token

    async def get_valid_password_reset_token(
        self,
        token_hash: str
    ) -> Optional[asyncpg.Record]:
        """
        Get valid password reset token (no user context needed for validation)
        """
        async with database.pool.acquire() as conn:
            # Use default context for token validation
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                "00000000-0000-0000-0000-000000000000"
            )

            token = await conn.fetchrow(
                """
                SELECT prt.*, u.email
                FROM password_reset_tokens prt
                JOIN users u ON prt.user_id = u.id
                WHERE prt.token_hash = $1 
                AND prt.expires_at > NOW() 
                AND prt.used = false
                """,
                token_hash
            )
            return token

    async def mark_token_used(
        self,
        token_id: UUID,
        user_id: UUID
    ) -> Optional[asyncpg.Record]:
        """
        Mark password reset token as used
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(user_id)
            )

            token = await conn.fetchrow(
                """
                UPDATE password_reset_tokens 
                SET used = true 
                WHERE id = $1 AND user_id = $2
                RETURNING *
                """,
                token_id, user_id
            )
            return token

    # ===== REACTIONS =====

    async def add_reaction(
        self,
        user_id: UUID,
        post_id: UUID,
        reaction_type: str
    ) -> Optional[asyncpg.Record]:
        """
        Add reaction to post with PROPER RLS context
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(user_id)
            )

            reaction = await conn.fetchrow(
                """
                INSERT INTO reactions (user_id, post_id, reaction_type)
                VALUES ($1, $2, $3)
                ON CONFLICT (user_id, post_id, reaction_type) 
                DO UPDATE SET created_at = NOW()
                RETURNING *
                """,
                user_id, post_id, reaction_type
            )
            return reaction

    async def remove_reaction(
        self,
        user_id: UUID,
        post_id: UUID,
        reaction_type: str
    ) -> bool:
        """
        Remove reaction from post
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(user_id)
            )

            result = await conn.execute(
                "DELETE FROM reactions WHERE user_id = $1 AND post_id = $2 AND reaction_type = $3",
                user_id, post_id, reaction_type
            )
            return "DELETE 1" in result

    async def get_post_reactions(
        self,
        post_id: UUID,
        user_id: UUID
    ) -> List[asyncpg.Record]:
        """
        Get reactions for a post with user context
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(user_id)
            )

            reactions = await conn.fetch(
                """
                SELECT reaction_type, COUNT(*) as count,
                       EXISTS(SELECT 1 FROM reactions r2 
                              WHERE r2.post_id = $1 
                              AND r2.user_id = $2 
                              AND r2.reaction_type = reactions.reaction_type) as user_reacted
                FROM reactions
                WHERE post_id = $1
                GROUP BY reaction_type
                ORDER BY count DESC
                """,
                post_id, user_id
            )
            return reactions

    # ===== SAVED POSTS =====

    async def save_post(
        self,
        user_id: UUID,
        post_id: UUID
    ) -> Optional[asyncpg.Record]:
        """
        Save post to user's collection
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(user_id)
            )

            saved_post = await conn.fetchrow(
                """
                INSERT INTO saved_posts (user_id, post_id)
                VALUES ($1, $2)
                ON CONFLICT (user_id, post_id) DO NOTHING
                RETURNING *
                """,
                user_id, post_id
            )
            return saved_post

    async def unsave_post(
        self,
        user_id: UUID,
        post_id: UUID
    ) -> bool:
        """
        Remove post from user's saved collection
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(user_id)
            )

            result = await conn.execute(
                "DELETE FROM saved_posts WHERE user_id = $1 AND post_id = $2",
                user_id, post_id
            )
            return "DELETE 1" in result

    async def get_user_saved_posts(
        self,
        user_id: UUID,
        requesting_user_id: UUID,
        limit: int = 20,
        offset: int = 0
    ) -> List[asyncpg.Record]:
        """
        Get user's saved posts
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(requesting_user_id)
            )

            saved_posts = await conn.fetch(
                """
                SELECT sp.*, p.*, u.username
                FROM saved_posts sp
                JOIN posts p ON sp.post_id = p.id
                JOIN users u ON p.user_id = u.id
                WHERE sp.user_id = $1
                ORDER BY sp.created_at DESC
                LIMIT $2 OFFSET $3
                """,
                user_id, limit, offset
            )
            return saved_posts

    # ===== CIRCLES SYSTEM =====

    async def get_public_circles(
        self,
        topic: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[asyncpg.Record]:
        """
        Get public circles
        """
        async with database.pool.acquire() as conn:
            # Use default context for public access
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                "00000000-0000-0000-0000-000000000000"
            )

            where_conditions = ["is_public = true"]
            params = []
            param_count = 1

            if topic:
                where_conditions.append(f"topic = ${param_count}")
                params.append(topic)
                param_count += 1

            where_clause = " AND ".join(where_conditions)
            params.extend([limit, offset])

            circles = await conn.fetch(
                f"""
                SELECT c.*, 
                       COUNT(cm.user_id) as member_count,
                       u.username as moderator_username
                FROM circles c
                LEFT JOIN circle_members cm ON c.id = cm.circle_id
                LEFT JOIN users u ON c.moderator_id = u.id
                WHERE {where_clause}
                GROUP BY c.id, u.username
                ORDER BY member_count DESC
                LIMIT ${param_count} OFFSET ${param_count + 1}
                """,
                *params
            )
            return circles

    async def join_circle(
        self,
        circle_id: UUID,
        user_id: UUID
    ) -> Optional[asyncpg.Record]:
        """
        Join a circle
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(user_id)
            )

            member = await conn.fetchrow(
                """
                INSERT INTO circle_members (circle_id, user_id)
                SELECT $1, $2
                FROM circles
                WHERE id = $1 AND is_public = true
                ON CONFLICT (circle_id, user_id) DO NOTHING
                RETURNING *
                """,
                circle_id, user_id
            )
            return member

    async def leave_circle(
        self,
        circle_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        Leave a circle
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(user_id)
            )

            result = await conn.execute(
                "DELETE FROM circle_members WHERE circle_id = $1 AND user_id = $2",
                circle_id, user_id
            )
            return "DELETE 1" in result

    async def get_user_circles(
        self,
        user_id: UUID,
        requesting_user_id: UUID
    ) -> List[asyncpg.Record]:
        """
        Get circles user has joined
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(requesting_user_id)
            )

            circles = await conn.fetch(
                """
                SELECT c.*, cm.role, cm.joined_at,
                       COUNT(cm2.user_id) as member_count
                FROM circle_members cm
                JOIN circles c ON cm.circle_id = c.id
                LEFT JOIN circle_members cm2 ON c.id = cm2.circle_id
                WHERE cm.user_id = $1
                GROUP BY c.id, cm.role, cm.joined_at
                ORDER BY cm.joined_at DESC
                """,
                user_id
            )
            return circles

    async def create_circle_post(
        self,
        circle_id: UUID,
        post_id: UUID,
        user_id: UUID,
        is_anonymous: bool = False
    ) -> Optional[asyncpg.Record]:
        """
        Create a post in a circle
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(user_id)
            )

            circle_post = await conn.fetchrow(
                """
                INSERT INTO circle_posts (circle_id, post_id, is_anonymous)
                SELECT $1, $2, $3
                FROM circle_members
                WHERE circle_id = $1 AND user_id = $4
                RETURNING *
                """,
                circle_id, post_id, is_anonymous, user_id
            )
            return circle_post

    # ===== HEALTH CHECK =====

    async def health_check(
        self,
        user_id: UUID
    ) -> bool:
        """
        Basic health check
        """
        async with database.pool.acquire() as conn:
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(user_id)
            )

            try:
                result = await conn.fetchval("SELECT 1")
                return result == 1
            except Exception:
                return False

# Instantiate the class
missing_phase1_features_crud = MissingPhase1FeaturesCRUD()
