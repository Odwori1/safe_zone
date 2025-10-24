"""
Enhanced Moderation Endpoints for Phase 3, Item 6
Following EXACT same patterns as live_audio_rooms.py endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from uuid import UUID

from app.schemas.enhanced_moderation import (
    ModerationActionCreate, ModerationActionResponse,
    ReportContentCreate, RoomLockStatus
)
from app.crud.enhanced_moderation import enhanced_moderation_crud
from app.core.security import get_current_user
from app.schemas.user import User

router = APIRouter()

@router.post("/rooms/{room_id}/moderate", response_model=ModerationActionResponse)
async def perform_moderation_action(
    room_id: UUID,
    action_data: ModerationActionCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Perform moderation action (mute, remove, ban, promote, etc.)
    SECURITY: RLS ensures only moderators/hosts can perform actions
    """
    try:
        # Create moderation action
        action = await enhanced_moderation_crud.create_moderation_action(
            room_id, action_data.dict(), current_user.id
        )

        if not action:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to perform moderation action or invalid target"
            )

        return action

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform moderation action"
        )

@router.get("/rooms/{room_id}/moderation-status/{user_id}")
async def get_user_moderation_status(
    room_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Get moderation status for a user in a room
    SECURITY: RLS ensures users can only see actions they're authorized for
    """
    try:
        actions = await enhanced_moderation_crud.get_user_moderation_status(
            room_id, user_id, current_user.id
        )

        is_muted = await enhanced_moderation_crud.is_user_muted(
            room_id, user_id, current_user.id
        )

        return {
            "user_id": str(user_id),
            "room_id": str(room_id),
            "is_muted": is_muted,
            "recent_actions": [
                {
                    "id": str(action["id"]),
                    "action_type": action["action_type"],
                    "moderator_id": str(action["moderator_id"]),
                    "reason": action["reason"],
                    "created_at": action["created_at"].isoformat()
                }
                for action in actions
            ]
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch moderation status"
        )

@router.get("/rooms/{room_id}/moderators")
async def get_room_moderators(
    room_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Get all moderators for a room
    SECURITY: RLS ensures users can only see moderators in rooms they have access to
    """
    try:
        moderators = await enhanced_moderation_crud.get_room_moderators(
            room_id, current_user.id
        )

        return {
            "room_id": str(room_id),
            "moderators": [
                {
                    "user_id": str(mod["user_id"]),
                    "username": mod["username"],
                    "role": mod["role"],
                    "joined_at": mod["joined_at"].isoformat()
                }
                for mod in moderators
            ]
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch room moderators"
        )

@router.post("/rooms/{room_id}/promote/{user_id}")
async def promote_to_moderator(
    room_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Promote user to moderator role
    SECURITY: RLS ensures only hosts can promote
    """
    try:
        updated = await enhanced_moderation_crud.promote_to_moderator(
            room_id, user_id, current_user.id
        )

        if not updated:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to promote users or user not found"
            )

        return {
            "message": "User promoted to moderator successfully",
            "user_id": str(user_id),
            "room_id": str(room_id)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to promote user"
        )

@router.post("/rooms/{room_id}/demote/{user_id}")
async def demote_from_moderator(
    room_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Demote user from moderator to participant
    SECURITY: RLS ensures only hosts can demote
    """
    try:
        updated = await enhanced_moderation_crud.demote_from_moderator(
            room_id, user_id, current_user.id
        )

        if not updated:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to demote users or user not found"
            )

        return {
            "message": "User demoted to participant successfully",
            "user_id": str(user_id),
            "room_id": str(room_id)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to demote user"
        )

@router.post("/rooms/{room_id}/lock")
async def lock_room(
    room_id: UUID,
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Lock room to prevent new joins
    SECURITY: RLS ensures only room hosts/moderators can lock
    """
    try:
        room = await enhanced_moderation_crud.lock_room(
            room_id, current_user.id, reason
        )

        if not room:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to lock room or room not found"
            )

        return {
            "message": "Room locked successfully",
            "room_id": str(room_id),
            "is_locked": True,
            "locked_by": str(current_user.id)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to lock room"
        )

@router.post("/rooms/{room_id}/unlock")
async def unlock_room(
    room_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Unlock room to allow new joins
    SECURITY: RLS ensures only room hosts/moderators can unlock
    """
    try:
        room = await enhanced_moderation_crud.unlock_room(
            room_id, current_user.id
        )

        if not room:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to unlock room or room not found"
            )

        return {
            "message": "Room unlocked successfully",
            "room_id": str(room_id),
            "is_locked": False
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unlock room"
        )

@router.post("/rooms/{room_id}/remove/{user_id}")
async def remove_user_from_room(
    room_id: UUID,
    user_id: UUID,
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Remove user from room (force leave)
    SECURITY: RLS ensures only moderators/hosts can remove users
    """
    try:
        success = await enhanced_moderation_crud.remove_user_from_room(
            room_id, user_id, current_user.id, reason
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to remove user or user not found"
            )

        return {
            "message": "User removed from room successfully",
            "user_id": str(user_id),
            "room_id": str(room_id)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove user from room"
        )

@router.post("/rooms/{room_id}/ban/{user_id}")
async def ban_user_from_room(
    room_id: UUID,
    user_id: UUID,
    reason: Optional[str] = None,
    duration_minutes: Optional[int] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Ban user from room (prevent rejoining)
    SECURITY: RLS ensures only moderators/hosts can ban users
    """
    try:
        success = await enhanced_moderation_crud.ban_user_from_room(
            room_id, user_id, current_user.id, reason, duration_minutes
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to ban user or user not found"
            )

        return {
            "message": "User banned from room successfully",
            "user_id": str(user_id),
            "room_id": str(room_id),
            "duration_minutes": duration_minutes
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to ban user from room"
        )

@router.post("/reports/content")
async def report_content(
    report_data: ReportContentCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Report inappropriate content
    SECURITY: RLS ensures users can only report their own content
    """
    try:
        # Create content report using the actual CRUD method
        report = await enhanced_moderation_crud.create_content_report(
            report_data.dict(), current_user.id
        )

        if not report:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create content report"
            )

        return {
            "message": "Content reported successfully",
            "report_id": str(report["id"]),
            "content_type": report_data.content_type,
            "content_id": str(report_data.content_id)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to report content"
        )

@router.get("/reports/my-reports")
async def get_my_reports(
    current_user: User = Depends(get_current_user)
):
    """
    Get all reports created by the current user
    SECURITY: RLS ensures users can only see their own reports
    """
    try:
        reports = await enhanced_moderation_crud.get_user_reports(current_user.id)

        return {
            "reports": [
                {
                    "id": str(report["id"]),
                    "content_type": report["content_type"],
                    "content_id": str(report["content_id"]),
                    "reason": report["reason"],
                    "status": report["status"],
                    "created_at": report["created_at"].isoformat()
                }
                for report in reports
            ]
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user reports"
        )
