from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from uuid import UUID
from app.schemas.post import PostCreate, PostResponse, PostUpdate, PostFeedResponse, ModerationAction
from app.schemas.user import User
from app.core.security import get_current_user
from app.crud.post_audio import post_crud
from app.crud.feed import get_post_feed, get_posts_count, get_moderation_queue, get_moderation_queue_count, update_moderation_status

router = APIRouter()

# ... (all other endpoints remain the same until the problematic section)

# FIXED: Move specific routes BEFORE parameter routes
@router.get("/audio", response_model=List[PostResponse])
async def read_audio_posts(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve audio posts only
    Phase 3, Item 1: Audio Post Support
    """
    try:
        posts = await post_crud.get_audio_posts(current_user.id, limit, skip)
        return [PostResponse(**dict(post)) for post in posts]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving audio posts: {str(e)}"
        )

@router.get("/video", response_model=List[PostResponse])
async def read_video_posts(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve video posts only
    Phase 3, Item 2: Video Post Support
    """
    try:
        posts = await post_crud.get_video_posts(current_user.id, limit, skip)
        return [PostResponse(**dict(post)) for post in posts]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving video posts: {str(e)}"
        )

# PARAMETER ROUTES MUST COME AFTER SPECIFIC ROUTES
@router.get("/{post_id}", response_model=PostResponse)
async def read_post(
    post_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific post by ID
    """
    try:
        post = await post_crud.get(UUID(post_id))
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        return PostResponse(**dict(post))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving post: {str(e)}"
        )
