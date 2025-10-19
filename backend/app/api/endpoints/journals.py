from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from app.schemas.journal import JournalEntryCreate, JournalEntryResponse, JournalEntryUpdate, JournalFeedResponse, JournalStats
from app.schemas.user import User
from app.core.security import get_current_user
from app.crud.journal import journal_crud

router = APIRouter()

@router.post("/entries/", response_model=JournalEntryResponse)
async def create_journal_entry(
    entry: JournalEntryCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new private journal entry
    """
    try:
        result = await journal_crud.create_entry(current_user.id, entry)
        if result:
            return JournalEntryResponse(**dict(result))
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
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve user's private journal entries
    """
    try:
        skip = (page - 1) * limit
        entries = await journal_crud.get_user_entries(current_user.id, limit, skip)
        total = await journal_crud.count_user_entries(current_user.id)
        
        return JournalFeedResponse(
            entries=[JournalEntryResponse(**dict(entry)) for entry in entries],
            total=total,
            page=page,
            has_next=(skip + len(entries)) < total
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving journal entries: {str(e)}"
        )

@router.get("/entries/{entry_id}", response_model=JournalEntryResponse)
async def read_journal_entry(
    entry_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific journal entry
    """
    try:
        entry = await journal_crud.get_entry(UUID(entry_id), current_user.id)
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Journal entry not found"
            )
        return JournalEntryResponse(**dict(entry))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving journal entry: {str(e)}"
        )

@router.put("/entries/{entry_id}", response_model=JournalEntryResponse)
async def update_journal_entry(
    entry_id: str,
    entry_update: JournalEntryUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update a journal entry
    """
    try:
        # First check if entry exists and user owns it
        existing_entry = await journal_crud.get_entry(UUID(entry_id), current_user.id)
        if not existing_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Journal entry not found"
            )
        
        updated_entry = await journal_crud.update_entry(UUID(entry_id), current_user.id, entry_update)
        if updated_entry:
            return JournalEntryResponse(**dict(updated_entry))
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update journal entry"
            )
    except HTTPException:
        raise
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
    Delete a journal entry
    """
    try:
        # First check if entry exists
        existing_entry = await journal_crud.get_entry(UUID(entry_id), current_user.id)
        if not existing_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Journal entry not found"
            )
        
        success = await journal_crud.delete_entry(UUID(entry_id), current_user.id)
        if success:
            return {"message": "Journal entry deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete journal entry"
            )
    except HTTPException:
        raise
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
    Get journal statistics for the current user
    """
    try:
        stats = await journal_crud.get_journal_stats(current_user.id)
        return JournalStats(**stats)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving journal stats: {str(e)}"
        )
