"""
Enhanced Journal API Endpoints - Using separate journals table
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from uuid import UUID
from app.schemas.journal import (
    JournalCreate, JournalResponse, JournalUpdate,
    JournalWithPrompt, JournalStats, JournalPrompt, JournalFeedResponse
)
from app.schemas.user import User
from app.core.security import get_current_user
from app.crud.journal import journal_crud

router = APIRouter()

@router.post("/entries/", response_model=JournalResponse)
async def create_journal_entry(
    entry: JournalCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new journal entry in enhanced journals table
    """
    try:
        result = await journal_crud.create_entry(current_user.id, entry)
        if result:
            return JournalResponse(**dict(result))
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create journal entry"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating journal entry: {str(e)}"
        )

@router.get("/entries/", response_model=JournalFeedResponse)
async def read_journal_entries(
    page: int = 1,
    limit: int = 50,
    status_filter: Optional[str] = Query(None, description="Filter by status", alias="status"),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve user's journal entries from enhanced journals table
    """
    try:
        skip = (page - 1) * limit
        entries = await journal_crud.get_user_entries(
            current_user.id, 
            limit=limit, 
            offset=skip,
            status=status_filter
        )
        total = await journal_crud.count_user_entries(current_user.id, status_filter)

        return JournalFeedResponse(
            entries=[JournalWithPrompt(**dict(entry)) for entry in entries],
            total=total,
            page=page,
            has_next=(skip + len(entries)) < total
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving journal entries: {str(e)}"
        )

@router.get("/entries/{entry_id}", response_model=JournalWithPrompt)
async def read_journal_entry(
    entry_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific journal entry from enhanced journals table - FIXED ERROR HANDLING
    """
    try:
        # Convert string to UUID first
        entry_uuid = UUID(entry_id)

        # Debug: log what we're trying to retrieve
        print(f"DEBUG: User {current_user.id} trying to access journal {entry_id}")

        entry = await journal_crud.get_entry(entry_uuid, current_user.id)

        # Debug: log what we got back
        print(f"DEBUG: Retrieved entry: {entry is not None}")

        # If entry is None, it means either it doesn't exist or RLS blocked access
        if not entry:
            print(f"DEBUG: Journal {entry_id} not found or access denied for user {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Journal entry not found"
            )

        return JournalWithPrompt(**dict(entry))

    except ValueError as e:
        # Invalid UUID format
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid journal ID format"
        )
    except HTTPException:
        # Re-raise HTTPExceptions (like our 404) without catching them
        raise
    except Exception as e:
        # Log the actual error for debugging
        print(f"DEBUG: Unexpected error retrieving journal {entry_id}: {str(e)}")
        print(f"DEBUG: Error type: {type(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving journal entry"
        )

@router.put("/entries/{entry_id}", response_model=JournalResponse)
async def update_journal_entry(
    entry_id: str,
    entry_update: JournalUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update a journal entry in enhanced journals table
    """
    try:
        existing_entry = await journal_crud.get_entry(UUID(entry_id), current_user.id)
        if not existing_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Journal entry not found"
            )

        updated_entry = await journal_crud.update_entry(UUID(entry_id), current_user.id, entry_update)
        if not updated_entry:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update journal entry"
            )

        return JournalResponse(**dict(updated_entry))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid journal ID format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating journal entry: {str(e)}"
        )

@router.delete("/entries/{entry_id}")
async def delete_journal_entry(
    entry_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a journal entry from enhanced journals table
    """
    try:
        existing_entry = await journal_crud.get_entry(UUID(entry_id), current_user.id)
        if not existing_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Journal entry not found"
            )

        success = await journal_crud.delete_entry(UUID(entry_id), current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete journal entry"
            )

        return {"message": "Journal entry deleted successfully"}
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid journal ID format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting journal entry: {str(e)}"
        )

@router.get("/stats/", response_model=JournalStats)
async def get_journal_stats(
    current_user: User = Depends(get_current_user)
):
    """
    Get enhanced journal statistics for the current user
    """
    try:
        stats = await journal_crud.get_journal_stats(current_user.id)
        return JournalStats(**stats)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving journal stats: {str(e)}"
        )

@router.get("/prompts/", response_model=List[JournalPrompt])
async def get_journal_prompts(
    category: Optional[str] = Query(None, description="Filter by category"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty level"),
    current_user: User = Depends(get_current_user)
):
    """
    Get journal writing prompts from journal_prompts table
    """
    try:
        prompts = await journal_crud.get_prompts(category, difficulty)
        return [JournalPrompt(**dict(prompt)) for prompt in prompts]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting prompts: {str(e)}"
        )
