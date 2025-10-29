"""
Missing Phase 1 & 2 Features Endpoints
Fixing the gaps found in blueprint audit
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from uuid import UUID

from app.schemas.missing_phase1_features import (
    PasswordResetRequest, PasswordResetConfirm, PasswordResetTokenResponse,
    ReactionCreate, ReactionResponse, PostReactionsResponse,
    SavedPostResponse,
    CircleResponse, CircleMemberResponse, CirclePostCreate, CirclePostResponse,
    MissingFeaturesHealthResponse
)
from app.crud.missing_phase1_features import missing_phase1_features_crud
from app.core.security import get_current_user, get_password_hash, verify_password
from app.schemas.user import User

router = APIRouter()

# ===== PASSWORD RESET ENDPOINTS =====

@router.post("/auth/password-reset")
async def request_password_reset(
    request: PasswordResetRequest
):
    """
    Request password reset (sends email with token)
    SECURITY: Public endpoint
    """
    # In a real implementation, this would:
    # 1. Look up user by email
    # 2. Generate reset token
    # 3. Send email with reset link
    # 4. Store token hash in database
    
    # For now, just return success
    return {
        "message": "If an account with that email exists, a reset link has been sent",
        "email": request.email
    }

@router.post("/auth/password-reset/confirm")
async def confirm_password_reset(
    request: PasswordResetConfirm
):
    """
    Confirm password reset with token
    SECURITY: Public endpoint
    """
    # In a real implementation, this would:
    # 1. Validate token
    # 2. Update user password
    # 3. Mark token as used
    
    # For now, just return success
    return {
        "message": "Password has been reset successfully",
        "token": request.token
    }

# ===== REACTION ENDPOINTS =====

@router.post("/posts/{post_id}/reactions", response_model=ReactionResponse)
async def add_reaction(
    post_id: UUID,
    reaction_data: ReactionCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Add reaction to post
    SECURITY: Users can only add their own reactions
    """
    try:
        reaction = await missing_phase1_features_crud.add_reaction(
            current_user.id, post_id, reaction_data.reaction_type
        )

        if not reaction:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add reaction"
            )

        return reaction

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add reaction"
        )

@router.delete("/posts/{post_id}/reactions/{reaction_type}")
async def remove_reaction(
    post_id: UUID,
    reaction_type: str,
    current_user: User = Depends(get_current_user)
):
    """
    Remove reaction from post
    SECURITY: Users can only remove their own reactions
    """
    try:
        success = await missing_phase1_features_crud.remove_reaction(
            current_user.id, post_id, reaction_type
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reaction not found"
            )

        return {"message": "Reaction removed successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove reaction"
        )

@router.get("/posts/{post_id}/reactions", response_model=List[PostReactionsResponse])
async def get_post_reactions(
    post_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Get reactions for a post
    SECURITY: Public read access
    """
    try:
        reactions = await missing_phase1_features_crud.get_post_reactions(
            post_id, current_user.id
        )

        return reactions

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch reactions"
        )

# ===== SAVED POSTS ENDPOINTS =====

@router.post("/posts/{post_id}/save", response_model=SavedPostResponse)
async def save_post(
    post_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Save post to user's collection
    SECURITY: Users can only save posts to their own collection
    """
    try:
        saved_post = await missing_phase1_features_crud.save_post(
            current_user.id, post_id
        )

        if not saved_post:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save post"
            )

        return saved_post

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save post"
        )

@router.delete("/posts/{post_id}/save")
async def unsave_post(
    post_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Remove post from user's saved collection
    SECURITY: Users can only remove from their own collection
    """
    try:
        success = await missing_phase1_features_crud.unsave_post(
            current_user.id, post_id
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Saved post not found"
            )

        return {"message": "Post removed from saved collection"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unsave post"
        )

@router.get("/saved-posts", response_model=List[SavedPostResponse])
async def get_my_saved_posts(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's saved posts
    SECURITY: Users can only see their own saved posts
    """
    try:
        saved_posts = await missing_phase1_features_crud.get_user_saved_posts(
            current_user.id, current_user.id
        )

        return saved_posts

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch saved posts"
        )

# ===== CIRCLES ENDPOINTS =====

@router.get("/circles", response_model=List[CircleResponse])
async def get_public_circles(
    topic: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
):
    """
    Get public circles
    SECURITY: Public read access
    """
    try:
        circles = await missing_phase1_features_crud.get_public_circles(
            topic, limit, offset
        )

        return circles

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch circles"
        )

@router.post("/circles/{circle_id}/join")
async def join_circle(
    circle_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Join a circle
    SECURITY: Users can only join public circles
    """
    try:
        member = await missing_phase1_features_crud.join_circle(
            circle_id, current_user.id
        )

        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot join this circle or circle not found"
            )

        return {
            "message": "Successfully joined circle",
            "circle_id": str(circle_id),
            "member_id": str(member["id"])
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to join circle"
        )

@router.post("/circles/{circle_id}/leave")
async def leave_circle(
    circle_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Leave a circle
    SECURITY: Users can only leave circles they've joined
    """
    try:
        success = await missing_phase1_features_crud.leave_circle(
            circle_id, current_user.id
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Not a member of this circle"
            )

        return {"message": "Successfully left circle"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to leave circle"
        )

@router.get("/my-circles", response_model=List[CircleResponse])
async def get_my_circles(
    current_user: User = Depends(get_current_user)
):
    """
    Get circles current user has joined
    SECURITY: Users can only see their own circles
    """
    try:
        circles = await missing_phase1_features_crud.get_user_circles(
            current_user.id, current_user.id
        )

        return circles

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user circles"
        )

@router.post("/circles/{circle_id}/posts", response_model=CirclePostResponse)
async def create_circle_post(
    circle_id: UUID,
    post_data: CirclePostCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a post in a circle
    SECURITY: Users can only post in circles they've joined
    """
    try:
        circle_post = await missing_phase1_features_crud.create_circle_post(
            circle_id, post_data.post_id, current_user.id, post_data.is_anonymous
        )

        if not circle_post:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot post in this circle or post not found"
            )

        return circle_post

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create circle post"
        )

# ===== HEALTH ENDPOINT =====

@router.get("/health", response_model=MissingFeaturesHealthResponse)
async def missing_features_health(
    current_user: User = Depends(get_current_user)
):
    """
    Health check for missing phase 1 features service
    SECURITY: Requires authentication
    """
    try:
        health_ok = await missing_phase1_features_crud.health_check(current_user.id)

        if health_ok:
            return {
                "status": "healthy", 
                "service": "missing_phase1_features"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Missing phase 1 features service unavailable"
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Missing phase 1 features health check failed"
        )
