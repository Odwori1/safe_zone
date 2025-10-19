from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from uuid import UUID
from app.schemas.mood import (
    MoodEntryCreate, 
    MoodEntryResponse, 
    MoodEntryUpdate, 
    MoodHistoryResponse,
    MoodStats,
    MoodHistoryQuery,
    MoodTrendQuery
)
from app.schemas.user import User
from app.core.security import get_current_user
from app.crud.mood import mood_crud

router = APIRouter()

@router.post("/entries/", response_model=MoodEntryResponse)
async def create_mood_entry(
    mood_entry: MoodEntryCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new mood entry
    """
    try:
        result = await mood_crud.create(current_user.id, mood_entry)
        if result:
            return MoodEntryResponse(**dict(result))
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create mood entry"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating mood entry: {str(e)}"
        )

@router.get("/entries/", response_model=MoodHistoryResponse)
async def get_mood_entries(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    days: Optional[int] = Query(None, ge=1, le=365, description="Number of days to look back"),
    current_user: User = Depends(get_current_user)
):
    """
    Get mood history with pagination
    """
    try:
        skip = (page - 1) * limit
        
        if days:
            # Get recent entries for specific days
            entries = await mood_crud.get_recent_entries(current_user.id, days)
            total = len(entries)
            # Apply pagination manually for recent entries
            paginated_entries = entries[skip:skip + limit]
            entries_list = [MoodEntryResponse(**dict(entry)) for entry in paginated_entries]
        else:
            # Get all entries with pagination
            entries = await mood_crud.get_user_entries(current_user.id, limit, skip)
            total = await mood_crud.count_user_entries(current_user.id)
            entries_list = [MoodEntryResponse(**dict(entry)) for entry in entries]

        return MoodHistoryResponse(
            entries=entries_list,
            total=total,
            page=page,
            has_next=(skip + len(entries_list)) < total
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving mood entries: {str(e)}"
        )

@router.get("/entries/{entry_id}", response_model=MoodEntryResponse)
async def get_mood_entry(
    entry_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific mood entry by ID
    """
    try:
        entry = await mood_crud.get(UUID(entry_id), current_user.id)
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mood entry not found"
            )
        return MoodEntryResponse(**dict(entry))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving mood entry: {str(e)}"
        )

@router.put("/entries/{entry_id}", response_model=MoodEntryResponse)
async def update_mood_entry(
    entry_id: str,
    mood_update: MoodEntryUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update a mood entry
    """
    try:
        # First check if entry exists and user owns it
        existing_entry = await mood_crud.get(UUID(entry_id), current_user.id)
        if not existing_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mood entry not found"
            )

        # Update the entry
        updated_entry = await mood_crud.update(UUID(entry_id), current_user.id, mood_update)
        if updated_entry:
            return MoodEntryResponse(**dict(updated_entry))
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update mood entry"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating mood entry: {str(e)}"
        )

@router.delete("/entries/{entry_id}")
async def delete_mood_entry(
    entry_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a mood entry
    """
    try:
        # First check if entry exists
        existing_entry = await mood_crud.get(UUID(entry_id), current_user.id)
        if not existing_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mood entry not found"
            )

        # Delete the entry
        success = await mood_crud.delete(UUID(entry_id), current_user.id)
        if success:
            return {"message": "Mood entry deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete mood entry"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting mood entry: {str(e)}"
        )

@router.get("/stats/", response_model=MoodStats)
async def get_mood_statistics(
    days: int = Query(30, ge=1, le=365, description="Number of days for statistics"),
    current_user: User = Depends(get_current_user)
):
    """
    Get mood statistics and trends
    """
    try:
        stats = await mood_crud.get_mood_stats(current_user.id, days)
        return MoodStats(**stats)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving mood statistics: {str(e)}"
        )
