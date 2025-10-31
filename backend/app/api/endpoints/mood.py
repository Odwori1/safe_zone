from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from uuid import UUID
from app.schemas.mood import (
    MoodEntryCreate, MoodEntryResponse, MoodEntryUpdate, MoodEntryHybridResponse,
    MoodHistoryResponse, MoodStats, MoodHistoryQuery, MoodTrendQuery,
    MoodTaxonomyResponse, ClinicalInsights
)
from app.schemas.user import User
from app.core.security import get_current_user
from app.crud.mood import mood_crud

router = APIRouter()

@router.post("/entries/", response_model=MoodEntryResponse)
async def create_mood_entry(
    mood_in: MoodEntryCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new mood entry"""
    try:
        entry = await mood_crud.create(current_user.id, mood_in)
        if not entry:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not create mood entry")
        return MoodEntryResponse(**dict(entry))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error creating mood entry: {str(e)}")

@router.get("/entries/", response_model=dict)
async def get_mood_entries(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    days: Optional[int] = Query(None, ge=1, le=365, description="Number of days to look back"),
    current_user: User = Depends(get_current_user)
):
    """Get mood history with pagination"""
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
            entries = await mood_crud.get_mood_entries_by_user(current_user.id, limit, skip)
            total = len(entries)
            entries_list = [MoodEntryResponse(**dict(entry)) for entry in entries]

        return {
            "entries": entries_list,
            "total": total,
            "page": page,
            "has_next": (skip + limit) < total
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error retrieving mood entries: {str(e)}")

@router.get("/stats/", response_model=dict)
async def get_mood_stats(
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    current_user: User = Depends(get_current_user)
):
    """Get mood statistics and insights"""
    try:
        stats = await mood_crud.get_mood_stats(current_user.id, days)
        return stats
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error retrieving mood statistics: {str(e)}")

@router.post("/entries/from-post/{post_id}", response_model=MoodEntryResponse)
async def create_mood_from_post(
    post_id: UUID,
    mood: str = Query(..., description="Mood type"),
    intensity: int = Query(..., ge=1, le=10, description="Mood intensity 1-10"),
    current_user: User = Depends(get_current_user)
):
    """Create mood entry from existing post"""
    try:
        entry = await mood_crud.create_from_post(current_user.id, post_id, mood, intensity)
        if not entry:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not create mood entry from post")
        return MoodEntryResponse(**dict(entry))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error creating mood entry from post: {str(e)}")

@router.post("/entries/from-journal/{journal_id}", response_model=MoodEntryResponse)
async def create_mood_from_journal(
    journal_id: UUID,
    mood: str = Query(..., description="Mood type"),
    intensity: int = Query(..., ge=1, le=10, description="Mood intensity 1-10"),
    current_user: User = Depends(get_current_user)
):
    """Create mood entry from existing journal"""
    try:
        entry = await mood_crud.create_from_journal(current_user.id, journal_id, mood, intensity)
        if not entry:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not create mood entry from journal")
        return MoodEntryResponse(**dict(entry))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error creating mood entry from journal: {str(e)}")

# Simple working hybrid endpoint
@router.get("/entries/hybrid-working")
async def get_hybrid_mood_working(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user)
):
    """WORKING HYBRID: Simple endpoint that returns mood entries"""
    try:
        entries = await mood_crud.get_recent_entries(current_user.id, days)
        return {
            "count": len(entries),
            "entries": [dict(entry) for entry in entries]
        }
    except Exception as e:
        return {"error": str(e)}

@router.get("/entries/hybrid-enhanced")
async def get_hybrid_mood_enhanced(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user)
):
    """ENHANCED HYBRID: Returns mood entries with post/journal context"""
    try:
        entries = await mood_crud.get_enhanced_hybrid_entries(current_user.id, days)
        return {
            "count": len(entries),
            "entries": entries
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving enhanced hybrid entries: {str(e)}"
        )

@router.get("/taxonomy", response_model=MoodTaxonomyResponse)
async def get_mood_taxonomy():
    """
    Get professional mood taxonomy
    Returns all available moods organized by clinical categories
    """
    try:
        taxonomy = await mood_crud.get_mood_taxonomy()
        return MoodTaxonomyResponse(**taxonomy)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving mood taxonomy: {str(e)}"
        )

@router.get("/stats/enhanced", response_model=MoodStats)
async def get_enhanced_mood_stats(
    days: int = Query(30, ge=1, le=365, description="Number of days for analysis"),
    current_user: User = Depends(get_current_user)
):
    """
    Get enhanced mood statistics with clinical insights
    Includes category analysis and professional recommendations
    """
    try:
        stats = await mood_crud.get_enhanced_stats(current_user.id, days)
        return MoodStats(**stats)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving enhanced mood statistics: {str(e)}"
        )

@router.get("/insights/clinical")
async def get_clinical_insights(
    days: int = Query(30, ge=1, le=365, description="Number of days for analysis"),
    current_user: User = Depends(get_current_user)
):
    """
    Get clinical insights from mood patterns
    Provides professional analysis and recommendations
    """
    try:
        insights = await mood_crud.get_clinical_insights(current_user.id, days)
        return insights
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving clinical insights: {str(e)}"
        )
