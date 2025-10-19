from typing import Optional, List
from uuid import UUID
from app.database.database import database
from app.schemas.post import PostResponse

async def get_post_feed(
    user_id: UUID,
    skip: int = 0,
    limit: int = 100,
    visibility: Optional[str] = None,
    content_type: Optional[str] = None,
    mood: Optional[str] = None
) -> List[PostResponse]:
    """
    Get posts for user feed (public posts + user's own posts)
    RLS ensures users only see appropriate content
    """
    query = """
        SELECT
            p.*,
            u.username as username,
            u.profile_picture as user_avatar
        FROM posts p
        LEFT JOIN users u ON p.user_id = u.id
        WHERE p.status = 'active'
        AND (p.visibility = 'public' OR p.user_id = $1)
        AND p.moderation_status = 'approved'
    """
    params = [user_id]
    param_count = 1

    if visibility:
        param_count += 1
        query += f" AND p.visibility = ${param_count}"
        params.append(visibility)

    if content_type:
        param_count += 1
        query += f" AND p.content_type = ${param_count}"
        params.append(content_type)

    if mood:
        param_count += 1
        query += f" AND p.mood = ${param_count}"
        params.append(mood)

    query += " ORDER BY p.created_at DESC LIMIT $2 OFFSET $3"
    params.extend([limit, skip])

    # Use the correct database method
    rows = await database.fetch(query, *params)
    return [PostResponse(**dict(row)) for row in rows]

async def get_posts_count(
    user_id: UUID,
    visibility: Optional[str] = None,
    content_type: Optional[str] = None,
    mood: Optional[str] = None
) -> int:
    """Get total count of posts for pagination"""
    query = """
        SELECT COUNT(*) FROM posts
        WHERE status = 'active'
        AND (visibility = 'public' OR user_id = $1)
        AND moderation_status = 'approved'
    """
    params = [user_id]
    param_count = 1

    if visibility:
        param_count += 1
        query += f" AND visibility = ${param_count}"
        params.append(visibility)

    if content_type:
        param_count += 1
        query += f" AND content_type = ${param_count}"
        params.append(content_type)

    if mood:
        param_count += 1
        query += f" AND mood = ${param_count}"
        params.append(mood)

    result = await database.fetchval(query, *params)
    return result if result else 0

async def get_moderation_queue(
    skip: int = 0,
    limit: int = 100,
    status: str = "pending"
) -> List[PostResponse]:
    """
    Get posts for moderation (admin only)
    """
    query = """
        SELECT
            p.*,
            u.username as username,
            u.profile_picture as user_avatar
        FROM posts p
        LEFT JOIN users u ON p.user_id = u.id
        WHERE p.moderation_status = $1
        ORDER BY p.created_at ASC
        LIMIT $2 OFFSET $3
    """

    # Use the correct database method
    rows = await database.fetch(query, status, limit, skip)
    return [PostResponse(**dict(row)) for row in rows]

async def get_moderation_queue_count(status: str = "pending") -> int:
    """Get total count of posts in moderation queue"""
    query = "SELECT COUNT(*) FROM posts WHERE moderation_status = $1"
    result = await database.fetchval(query, status)
    return result if result else 0

async def update_moderation_status(
    post_id: UUID,
    status: str,
    moderator_notes: Optional[str] = None
) -> bool:
    """
    Update post moderation status (admin only)
    """
    query = """
        UPDATE posts
        SET moderation_status = $1,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = $2
    """

    try:
        await database.execute(query, status, post_id)
        return True
    except Exception:
        return False
