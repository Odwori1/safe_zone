import asyncpg
from typing import Optional, List
from uuid import UUID
from app.database.database import database
from app.schemas.post import PostResponse  # ADD MISSING IMPORT

class CRUDPost:
    async def get(self, post_id: UUID, user_id: UUID = None) -> Optional[asyncpg.Record]:
        """Get post by ID with like information"""
        async with database.pool.acquire() as conn:
            # Set user context for RLS if user_id is provided
            if user_id:
                await conn.execute("SELECT set_current_user_id($1);", str(user_id))

            post = await conn.fetchrow(
                "SELECT * FROM posts WHERE id = $1 AND status != 'deleted'",
                post_id
            )

            if post:
                post_dict = dict(post)

                # Get like count for this post
                like_count = await conn.fetchval(
                    "SELECT COUNT(*) FROM post_likes WHERE post_id = $1",
                    post_id
                )
                post_dict['like_count'] = like_count or 0

                # Check if current user has liked this post (only if user_id is provided)
                if user_id:
                    user_has_liked = await conn.fetchval(
                        "SELECT 1 FROM post_likes WHERE post_id = $1 AND user_id = $2",
                        post_id, user_id
                    )
                    post_dict['user_has_liked'] = user_has_liked is not None
                    print(f"🔍 GET: Post {post_id}, user {user_id} has_liked = {user_has_liked is not None}")
                else:
                    post_dict['user_has_liked'] = False

                # Get share count for this post
                share_count = await conn.fetchval(
                    "SELECT COUNT(*) FROM post_shares WHERE post_id = $1",
                    post_id
                )
                post_dict['share_count'] = share_count or 0

                # Check if current user has shared this post (only if user_id is provided)
                if user_id:
                    user_has_shared = await conn.fetchval(
                        "SELECT 1 FROM post_shares WHERE post_id = $1 AND user_id = $2",
                        post_id, user_id
                    )
                    post_dict['user_has_shared'] = user_has_shared is not None
                    print(f"🔍 GET: Post {post_id}, user {user_id} has_shared = {user_has_shared is not None}")
                else:
                    post_dict['user_has_shared'] = False

                return post_dict
            return None

    async def get_by_user(self, user_id: UUID, limit: int = 50, offset: int = 0) -> List[dict]:
        """Get posts by user ID with like information"""
        async with database.pool.acquire() as conn:
            # Set user context for RLS
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            posts = await conn.fetch(
                """
                SELECT p.*, u.username, u.profile_picture as user_avatar,
                       (SELECT COUNT(*) FROM post_likes WHERE post_id = p.id) as like_count,
                       EXISTS(
                         SELECT 1 FROM post_likes
                         WHERE post_id = p.id AND user_id = $1
                       ) as user_has_liked,
                       (SELECT COUNT(*) FROM post_shares WHERE post_id = p.id) as share_count,
                       EXISTS(
                         SELECT 1 FROM post_shares
                         WHERE post_id = p.id AND user_id = $1
                       ) as user_has_shared
                FROM posts p
                LEFT JOIN users u ON p.user_id = u.id
                WHERE p.user_id = $1 AND p.status != 'deleted'
                ORDER BY p.created_at DESC
                LIMIT $2 OFFSET $3
                """,
                user_id, limit, offset
            )

            # Convert asyncpg.Record to dict and ensure proper typing
            result = []
            for post in posts:
                post_dict = dict(post)
                # Ensure boolean conversion for user_has_liked
                post_dict['user_has_liked'] = bool(post_dict.get('user_has_liked', False))
                # Ensure integer conversion for like_count
                post_dict['like_count'] = int(post_dict.get('like_count', 0))
                # Ensure boolean conversion for user_has_shared
                post_dict['user_has_shared'] = bool(post_dict.get('user_has_shared', False))
                # Ensure integer conversion for share_count
                post_dict['share_count'] = int(post_dict.get('share_count', 0))
                result.append(post_dict)

            return result

    async def get_feed(
        self,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0,
        mood: Optional[str] = None,
        visibility: Optional[str] = None,
        user_id_filter: Optional[UUID] = None,
        search: Optional[str] = None
    ) -> List[dict]:
        """Get post feed for user (public posts and user's own posts) with optional filters and like information"""
        # Start building the query
        query_parts = [
            """
            SELECT p.*,
                   CASE WHEN p.is_anonymous THEN NULL ELSE u.username END as username,
                   CASE WHEN p.is_anonymous THEN NULL ELSE u.profile_picture END as user_avatar,
                   (SELECT COUNT(*) FROM post_likes WHERE post_id = p.id) as like_count,
                   EXISTS(
                     SELECT 1 FROM post_likes
                     WHERE post_id = p.id AND user_id = $1
                   ) as user_has_liked,
                   (SELECT COUNT(*) FROM post_shares WHERE post_id = p.id) as share_count,
                   EXISTS(
                     SELECT 1 FROM post_shares
                     WHERE post_id = p.id AND user_id = $1
                   ) as user_has_shared
            FROM posts p
            LEFT JOIN users u ON p.user_id = u.id
            WHERE p.status = 'active'
            AND (p.moderation_status = 'approved' OR p.user_id = $1)
            AND u.is_active = true
            """
        ]

        params = [user_id]
        param_count = 1

        # Add visibility filter
        if visibility:
            param_count += 1
            query_parts.append(f"AND p.visibility = ${param_count}")
            params.append(visibility)
        else:
            # Default visibility filter (show public posts and user's own posts)
            query_parts.append("AND (p.visibility = 'public' OR p.user_id = $1)")

        # Add mood filter
        if mood:
            param_count += 1
            query_parts.append(f"AND p.mood = ${param_count}")
            params.append(mood)

        # Add user_id filter (for "my posts" functionality)
        if user_id_filter:
            param_count += 1
            query_parts.append(f"AND p.user_id = ${param_count}")
            params.append(user_id_filter)

        # Add search filter (text search in post content)
        if search:
            param_count += 1
            query_parts.append(f"AND p.content ILIKE ${param_count}")
            params.append(f"%{search}%")

        # Add ordering and pagination
        query_parts.append("ORDER BY p.created_at DESC")
        param_count += 1
        query_parts.append(f"LIMIT ${param_count}")
        params.append(limit)
        param_count += 1
        query_parts.append(f"OFFSET ${param_count}")
        params.append(offset)

        # Combine all query parts
        final_query = "\n".join(query_parts)

        async with database.pool.acquire() as conn:
            # Set user context for RLS
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            posts = await conn.fetch(final_query, *params)

            # DEBUG: Check what data we're getting from database
            print(f"🔍 CRUD_GET_FEED: Got {len(posts)} posts from database")
            if posts:
                for i, post in enumerate(posts[:2]):
                    post_dict = dict(post)
                    print(f"🔍 CRUD_GET_FEED: Post {i} keys: {list(post_dict.keys())}")
                    print(f"🔍 CRUD_GET_FEED: Post {i} like_count: {post_dict.get('like_count', 'MISSING')}, user_has_liked: {post_dict.get('user_has_liked', 'MISSING')}")
                    print(f"🔍 CRUD_GET_FEED: Post {i} share_count: {post_dict.get('share_count', 'MISSING')}, user_has_shared: {post_dict.get('user_has_shared', 'MISSING')}")

            # Convert asyncpg.Record to dict and ensure proper typing
            result = []
            for post in posts:
                post_dict = dict(post)
                # Ensure boolean conversion for user_has_liked
                post_dict['user_has_liked'] = bool(post_dict.get('user_has_liked', False))
                # Ensure integer conversion for like_count
                post_dict['like_count'] = int(post_dict.get('like_count', 0))
                # Ensure boolean conversion for user_has_shared
                post_dict['user_has_shared'] = bool(post_dict.get('user_has_shared', False))
                # Ensure integer conversion for share_count
                post_dict['share_count'] = int(post_dict.get('share_count', 0))
                result.append(post_dict)

            return result

    async def create(self, user_id: UUID, post_in) -> asyncpg.Record:
        """Create new post - FIXED to properly set user context with AUTO-APPROVAL"""
        async with database.pool.acquire() as conn:
            # CRITICAL: Set user context for RLS policies
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))

            # Build the INSERT query based on available fields
            if hasattr(post_in, 'audio_url') and post_in.audio_url:
                # Audio post with additional fields - AUTO-APPROVED
                return await conn.fetchrow(
                    """
                    INSERT INTO posts (user_id, content, content_type, mood, visibility, is_anonymous,
                                     audio_url, audio_duration, file_size, mime_type, moderation_status)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, 'approved')
                    RETURNING *
                    """,
                    user_id, post_in.content, post_in.content_type, post_in.mood,
                    post_in.visibility, post_in.is_anonymous,
                    getattr(post_in, 'audio_url', None),
                    getattr(post_in, 'audio_duration', None),
                    getattr(post_in, 'file_size', None),
                    getattr(post_in, 'mime_type', None)
                )
            elif hasattr(post_in, 'video_url') and post_in.video_url:
                # Video post with additional fields - AUTO-APPROVED
                return await conn.fetchrow(
                    """
                    INSERT INTO posts (user_id, content, content_type, mood, visibility, is_anonymous,
                                     video_url, video_duration, thumbnail_url, video_width, video_height, moderation_status)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, 'approved')
                    RETURNING *
                    """,
                    user_id, post_in.content, post_in.content_type, post_in.mood,
                    post_in.visibility, post_in.is_anonymous,
                    getattr(post_in, 'video_url', None),
                    getattr(post_in, 'video_duration', None),
                    getattr(post_in, 'thumbnail_url', None),
                    getattr(post_in, 'video_width', None),
                    getattr(post_in, 'video_height', None)
                )
            elif hasattr(post_in, 'image_url') and post_in.image_url:
                # Image post - AUTO-APPROVED (images are text posts with image_url)
                return await conn.fetchrow(
                    """
                    INSERT INTO posts (user_id, content, content_type, mood, visibility, is_anonymous,
                                     image_url, moderation_status)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, 'approved')
                    RETURNING *
                    """,
                    user_id, post_in.content, post_in.content_type, post_in.mood,
                    post_in.visibility, post_in.is_anonymous,
                    getattr(post_in, 'image_url', None)
                )
            else:
                # Regular text post - AUTO-APPROVED
                return await conn.fetchrow(
                    """
                    INSERT INTO posts (user_id, content, content_type, mood, visibility, is_anonymous, moderation_status)
                    VALUES ($1, $2, $3, $4, $5, $6, 'approved')
                    RETURNING *
                    """,
                    user_id, post_in.content, post_in.content_type, post_in.mood,
                    post_in.visibility, post_in.is_anonymous
                )

    async def update(self, post_id: UUID, user_id: UUID, post_in) -> Optional[asyncpg.Record]:
        """Update post - only by owner"""
        if hasattr(post_in, 'dict'):
            update_data = post_in.dict(exclude_unset=True)
        else:
            update_data = post_in

        if not update_data:
            return await self.get(post_id)

        update_fields = []
        values = []
        index = 1

        for field, value in update_data.items():
            update_fields.append(f"{field} = ${index}")
            values.append(value)
            index += 1

        values.extend([post_id, user_id])
        query = f"""
            UPDATE posts
            SET {', '.join(update_fields)}, updated_at = NOW()
            WHERE id = ${index} AND user_id = ${index + 1}
            RETURNING *
        """

        async with database.pool.acquire() as conn:
            # Set user context for RLS
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            return await conn.fetchrow(query, *values)

    async def delete(self, post_id: UUID, user_id: UUID) -> bool:
        """Soft delete post - only by owner"""
        async with database.pool.acquire() as conn:
            # Set user context for RLS
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            result = await conn.execute(
                "UPDATE posts SET status = 'deleted' WHERE id = $1 AND user_id = $2",
                post_id, user_id
            )
            return "UPDATE 1" in result

    async def count_user_posts(self, user_id: UUID) -> int:
        """Count user's active posts"""
        async with database.pool.acquire() as conn:
            return await conn.fetchval(
                "SELECT COUNT(*) FROM posts WHERE user_id = $1 AND status != 'deleted'",
                user_id
            )

    # The following methods are now properly indented as part of the class
    async def has_user_liked(self, post_id: UUID, user_id: UUID) -> bool:
        """Check if user has liked a post - FOLLOWING RLS PATTERN"""
        async with database.pool.acquire() as conn:
            # Set user context for RLS (same pattern as other methods)
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            result = await conn.fetchval(
                "SELECT 1 FROM post_likes WHERE post_id = $1 AND user_id = $2",
                post_id, user_id
            )
            return result is not None

    async def add_like(self, post_id: UUID, user_id: UUID) -> bool:
        """Add a like to a post - FOLLOWING RLS PATTERN"""
        async with database.pool.acquire() as conn:
            # Set user context for RLS (same pattern as other methods)
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            try:
                result = await conn.execute(
                    "INSERT INTO post_likes (post_id, user_id) VALUES ($1, $2)",
                    post_id, user_id
                )
                return "INSERT 0 1" in result
            except asyncpg.exceptions.UniqueViolationError:
                # User already liked this post (RLS will prevent this but handle gracefully)
                return False

    async def remove_like(self, post_id: UUID, user_id: UUID) -> bool:
        """Remove a like from a post - FOLLOWING RLS PATTERN"""
        async with database.pool.acquire() as conn:
            # Set user context for RLS (same pattern as other methods)
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            result = await conn.execute(
                "DELETE FROM post_likes WHERE post_id = $1 AND user_id = $2",
                post_id, user_id
            )
            return "DELETE 1" in result

    async def get_like_count(self, post_id: UUID, user_id: UUID) -> int:
        """Get the number of likes for a post - FOLLOWING RLS PATTERN"""
        async with database.pool.acquire() as conn:
            # Set user context for RLS (same pattern as other methods)
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            return await conn.fetchval(
                "SELECT COUNT(*) FROM post_likes WHERE post_id = $1",
                post_id
            )

    async def has_user_shared(self, post_id: UUID, user_id: UUID) -> bool:
        """Check if user has shared a post"""
        async with database.pool.acquire() as conn:
            # Set user context for RLS
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            result = await conn.fetchval(
                "SELECT 1 FROM post_shares WHERE post_id = $1 AND user_id = $2",
                post_id, user_id
            )
            return result is not None

    async def add_share(self, post_id: UUID, user_id: UUID) -> bool:
        """Add a share to a post"""
        async with database.pool.acquire() as conn:
            # Set user context for RLS
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            try:
                result = await conn.execute(
                    "INSERT INTO post_shares (post_id, user_id) VALUES ($1, $2)",
                    post_id, user_id
                )
                return "INSERT 0 1" in result
            except asyncpg.exceptions.UniqueViolationError:
                # User already shared this post
                return False

    async def remove_share(self, post_id: UUID, user_id: UUID) -> bool:
        """Remove a share from a post"""
        async with database.pool.acquire() as conn:
            # Set user context for RLS
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            result = await conn.execute(
                "DELETE FROM post_shares WHERE post_id = $1 AND user_id = $2",
                post_id, user_id
            )
            return "DELETE 1" in result

    async def get_share_count(self, post_id: UUID, user_id: UUID) -> int:
        """Get the number of shares for a post"""
        async with database.pool.acquire() as conn:
            # Set user context for RLS
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            return await conn.fetchval(
                "SELECT COUNT(*) FROM post_shares WHERE post_id = $1",
                post_id
            )

    # ========== SAVED POSTS METHODS (ADDED TO CLASS) ==========

    async def save_post(self, post_id: UUID, user_id: UUID) -> bool:
        """Save a post for later"""
        try:
            # Check if post exists and user has access
            post = await self.get(post_id, user_id)
            if not post:
                return False

            # Check if already saved
            already_saved = await self.is_post_saved(post_id, user_id)
            if already_saved:
                return True  # Already saved, consider it success

            # Save the post
            async with database.pool.acquire() as conn:
                await conn.execute("SELECT set_current_user_id($1);", str(user_id))
                result = await conn.execute(
                    "INSERT INTO saved_posts (post_id, user_id) VALUES ($1, $2)",
                    post_id, user_id
                )
                return "INSERT 0 1" in result

        except Exception as e:
            print(f"Error saving post: {e}")
            return False

    async def unsave_post(self, post_id: UUID, user_id: UUID) -> bool:
        """Remove a post from saved"""
        try:
            async with database.pool.acquire() as conn:
                await conn.execute("SELECT set_current_user_id($1);", str(user_id))
                result = await conn.execute(
                    "DELETE FROM saved_posts WHERE post_id = $1 AND user_id = $2",
                    post_id, user_id
                )
                return "DELETE 1" in result
        except Exception as e:
            print(f"Error unsaving post: {e}")
            return False

    async def get_saved_posts(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[dict]:
        """Get user's saved posts"""
        try:
            async with database.pool.acquire() as conn:
                await conn.execute("SELECT set_current_user_id($1);", str(user_id))
                posts = await conn.fetch(
                    """
                    SELECT
                        p.*,
                        u.username as username,
                        u.profile_picture as user_avatar,
                        (SELECT COUNT(*) FROM post_likes WHERE post_id = p.id) as like_count,
                        EXISTS(
                            SELECT 1 FROM post_likes
                            WHERE post_id = p.id AND user_id = $1
                        ) as user_has_liked,
                        (SELECT COUNT(*) FROM post_shares WHERE post_id = p.id) as share_count,
                        EXISTS(
                            SELECT 1 FROM post_shares
                            WHERE post_id = p.id AND user_id = $1
                        ) as user_has_shared,
                        sp.saved_at as saved_at
                    FROM saved_posts sp
                    JOIN posts p ON sp.post_id = p.id
                    LEFT JOIN users u ON p.user_id = u.id
                    WHERE sp.user_id = $1
                    AND p.status = 'active'
                    AND p.moderation_status = 'approved'
                    ORDER BY sp.saved_at DESC
                    LIMIT $2 OFFSET $3
                    """,
                    user_id, limit, skip
                )

                # Convert asyncpg.Record to dict and ensure proper typing
                result = []
                for post in posts:
                    post_dict = dict(post)
                    # Ensure boolean conversion for user_has_liked
                    post_dict['user_has_liked'] = bool(post_dict.get('user_has_liked', False))
                    # Ensure integer conversion for like_count
                    post_dict['like_count'] = int(post_dict.get('like_count', 0))
                    # Ensure boolean conversion for user_has_shared
                    post_dict['user_has_shared'] = bool(post_dict.get('user_has_shared', False))
                    # Ensure integer conversion for share_count
                    post_dict['share_count'] = int(post_dict.get('share_count', 0))
                    result.append(post_dict)

                return result
        except Exception as e:
            print(f"Error getting saved posts: {e}")
            return []

    async def is_post_saved(self, post_id: UUID, user_id: UUID) -> bool:
        """Check if a post is saved by user"""
        try:
            async with database.pool.acquire() as conn:
                await conn.execute("SELECT set_current_user_id($1);", str(user_id))
                result = await conn.fetchval(
                    "SELECT 1 FROM saved_posts WHERE post_id = $1 AND user_id = $2",
                    post_id, user_id
                )
                return bool(result)
        except Exception as e:
            print(f"Error checking if post saved: {e}")
            return False

    async def get_saved_posts_count(self, user_id: UUID) -> int:
        """Get count of user's saved posts"""
        try:
            async with database.pool.acquire() as conn:
                await conn.execute("SELECT set_current_user_id($1);", str(user_id))
                result = await conn.fetchval(
                    "SELECT COUNT(*) FROM saved_posts WHERE user_id = $1",
                    user_id
                )
                return result if result else 0
        except Exception as e:
            print(f"Error getting saved posts count: {e}")
            return 0

# Create instance
post_crud = CRUDPost()
