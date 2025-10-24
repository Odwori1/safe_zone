"""
AI Personalization Endpoints for Phase 4, Item 1
Following EXACT same patterns as professional_directory.py endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from uuid import UUID
from datetime import time

from app.schemas.ai_personalization import (
    ContentAnalysisResponse, UserBehaviorPatternsResponse,
    PersonalizedRecommendationCreate, PersonalizedRecommendationResponse,
    CopingStrategyResponse, UserCopingPreferenceUpdate,
    NotificationPreferencesUpdate, NotificationPreferencesResponse
)
from app.crud.ai_personalization import ai_personalization_crud
from app.core.security import get_current_user
from app.schemas.user import User

router = APIRouter()

# ===== CONTENT ANALYSIS ENDPOINTS =====

@router.get("/content/{content_type}/{content_id}/analysis", response_model=ContentAnalysisResponse)
async def get_content_analysis(
    content_type: str,
    content_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Get AI content analysis for specific content
    SECURITY: Users can only see analysis of content they have access to
    """
    try:
        analysis = await ai_personalization_crud.get_content_analysis(
            content_type, content_id, current_user.id
        )

        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content analysis not found"
            )

        return analysis

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch content analysis"
        )

# ===== USER BEHAVIOR PATTERNS ENDPOINTS =====

@router.get("/behavior/patterns", response_model=UserBehaviorPatternsResponse)
async def get_my_behavior_patterns(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's behavior patterns
    SECURITY: Users can only see their own patterns
    """
    try:
        patterns = await ai_personalization_crud.get_user_behavior_patterns(
            current_user.id, current_user.id
        )

        if not patterns:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Behavior patterns not found"
            )

        return patterns

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch behavior patterns"
        )

# ===== PERSONALIZED RECOMMENDATIONS ENDPOINTS =====

@router.get("/recommendations", response_model=List[PersonalizedRecommendationResponse])
async def get_my_recommendations(
    recommendation_type: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
    current_user: User = Depends(get_current_user)
):
    """
    Get personalized recommendations for current user
    SECURITY: Users can only see their own recommendations
    """
    try:
        recommendations = await ai_personalization_crud.get_user_recommendations(
            current_user.id, current_user.id, recommendation_type, limit, offset
        )

        return recommendations

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch recommendations"
        )

@router.post("/recommendations/{recommendation_id}/interact")
async def interact_with_recommendation(
    recommendation_id: UUID,
    interaction_data: dict,
    current_user: User = Depends(get_current_user)
):
    """
    Interact with a recommendation (dismiss, complete, provide feedback)
    SECURITY: Users can only interact with their own recommendations
    """
    try:
        recommendation = await ai_personalization_crud.update_recommendation_interaction(
            recommendation_id, current_user.id, interaction_data
        )

        if not recommendation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recommendation not found"
            )

        return {
            "message": "Recommendation interaction updated successfully",
            "recommendation_id": str(recommendation_id)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update recommendation interaction"
        )

# ===== COPING STRATEGIES ENDPOINTS =====

@router.get("/coping/strategies", response_model=List[CopingStrategyResponse])
async def get_coping_strategies(
    target_emotions: Optional[List[str]] = None,
    strategy_type: Optional[str] = None,
    difficulty_level: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
):
    """
    Get coping strategies with filtering options
    SECURITY: Public read access to active strategies
    """
    try:
        strategies = await ai_personalization_crud.get_coping_strategies(
            target_emotions, strategy_type, difficulty_level, limit, offset
        )

        return strategies

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch coping strategies"
        )

@router.get("/coping/preferences", response_model=List[CopingStrategyResponse])
async def get_my_coping_preferences(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's coping strategy preferences
    SECURITY: Users can only see their own preferences
    """
    try:
        preferences = await ai_personalization_crud.get_user_coping_preferences(
            current_user.id, current_user.id
        )

        # Convert to same format as coping strategies response
        strategies = []
        for pref in preferences:
            strategy_data = {
                "id": pref["strategy_id"],
                "strategy_name": pref["strategy_name"],
                "strategy_type": pref["strategy_type"],
                "description": pref["description"],
                "preference_score": pref["preference_score"],
                "effectiveness_rating": pref["effectiveness_rating"],
                "usage_count": pref["usage_count"],
                "last_used_at": pref["last_used_at"]
            }
            strategies.append(strategy_data)

        return strategies

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch coping preferences"
        )

@router.post("/coping/strategies/{strategy_id}/preference")
async def update_coping_preference(
    strategy_id: UUID,
    preference_data: UserCopingPreferenceUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update user preference for a coping strategy
    SECURITY: Users can only update their own preferences
    """
    try:
        preference = await ai_personalization_crud.update_coping_preference(
            current_user.id, strategy_id, preference_data.dict()
        )

        if not preference:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update coping preference"
            )

        return {
            "message": "Coping preference updated successfully",
            "strategy_id": str(strategy_id),
            "preference_score": preference["preference_score"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update coping preference"
        )

# ===== NOTIFICATION PREFERENCES ENDPOINTS =====

@router.get("/notifications/preferences", response_model=NotificationPreferencesResponse)
async def get_my_notification_preferences(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's notification preferences
    SECURITY: Users can only see their own preferences
    """
    try:
        preferences = await ai_personalization_crud.get_notification_preferences(
            current_user.id, current_user.id
        )

        if not preferences:
            # Return default preferences if none set
            return {
                "user_id": current_user.id,
                "optimal_morning_time": time(9, 0),
                "optimal_afternoon_time": time(14, 0),
                "optimal_evening_time": time(19, 0),
                "quiet_hours_start": time(22, 0),
                "quiet_hours_end": time(7, 0),
                "timezone": "UTC",
                "receive_mood_insights": True,
                "receive_wellness_tips": True,
                "receive_community_updates": True,
                "receive_professional_suggestions": True,
                "preferred_notification_types": ["push", "in_app"],
                "max_daily_notifications": 5,
                "mood_based_timing": True,
                "engagement_based_frequency": True
            }

        return preferences

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch notification preferences"
        )

@router.put("/notifications/preferences", response_model=NotificationPreferencesResponse)
async def update_my_notification_preferences(
    preferences_data: NotificationPreferencesUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update current user's notification preferences
    SECURITY: Users can only update their own preferences
    """
    try:
        preferences = await ai_personalization_crud.update_notification_preferences(
            current_user.id, preferences_data.dict(exclude_unset=True)
        )

        if not preferences:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update notification preferences"
            )

        return preferences

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update notification preferences"
        )

# ===== HEALTH ENDPOINT =====

@router.get("/health")
async def ai_personalization_health(
    current_user: User = Depends(get_current_user)
):
    """
    Health check for AI personalization service
    SECURITY: Requires authentication
    """
    try:
        health_ok = await ai_personalization_crud.health_check(current_user.id)
        
        if health_ok:
            return {"status": "healthy", "service": "ai_personalization"}
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI personalization service unavailable"
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI personalization health check failed"
        )
