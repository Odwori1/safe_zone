from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from uuid import UUID
from datetime import date

from app.schemas.crisis import (
    CrisisResourceResponse,
    CrisisResourcesResponse,
    EmergencyContactCreate,
    EmergencyContactResponse,
    EmergencyContactUpdate,
    EmergencyContactsResponse,
    UserCrisisPreferencesCreate,
    UserCrisisPreferencesResponse,
    UserCrisisPreferencesUpdate,
    ResourceRecommendationRequest,
    ResourceRecommendationResponse,
    # New schemas
    SafetyPlanCreate,
    SafetyPlanResponse,
    SafetyPlanUpdate,
    SafetyPlansResponse,
    WellnessCheckinCreate,
    WellnessCheckinResponse,
    WellnessCheckinUpdate,
    WellnessCheckinsResponse,
    CrisisAlertCreate,
    CrisisAlertResponse,
    CrisisAlertsResponse
)
from app.schemas.user import User
from app.core.security import get_current_user
from app.crud.crisis import crisis_crud

router = APIRouter()

# ========== EXISTING ENDPOINTS ==========

@router.get("/resources/", response_model=CrisisResourcesResponse)
async def get_crisis_resources(
    category: Optional[str] = Query(None, description="Filter by category"),
    geographic_scope: Optional[str] = Query(None, description="Filter by geographic scope"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user)
):
    """
    Get crisis resources with optional filtering
    """
    try:
        skip = (page - 1) * limit
        resources = await crisis_crud.get_all_resources(category, geographic_scope, limit, skip)
        total = await crisis_crud.count_resources(category, geographic_scope)

        # Get user location from preferences for personalized response
        user_preferences = await crisis_crud.get_user_crisis_preferences(current_user.id)
        user_location = user_preferences['country_code'] if user_preferences else None

        return CrisisResourcesResponse(
            resources=[CrisisResourceResponse(**dict(resource)) for resource in resources],
            total=total,
            user_location=user_location
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving crisis resources: {str(e)}"
        )

@router.get("/resources/search/", response_model=CrisisResourcesResponse)
async def search_crisis_resources(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
    current_user: User = Depends(get_current_user)
):
    """
    Search crisis resources by name, description, or tags
    """
    try:
        resources = await crisis_crud.search_resources(q, limit)
        return CrisisResourcesResponse(
            resources=[CrisisResourceResponse(**dict(resource)) for resource in resources],
            total=len(resources)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching crisis resources: {str(e)}"
        )

@router.get("/resources/recommendations/", response_model=ResourceRecommendationResponse)
async def get_recommended_resources(
    content: Optional[str] = Query(None, description="Content to analyze for recommendations"),
    mood: Optional[str] = Query(None, description="Current mood for recommendations"),
    category: Optional[str] = Query(None, description="Filter by specific category"),
    limit: int = Query(5, ge=1, le=20, description="Maximum recommendations"),
    current_user: User = Depends(get_current_user)
):
    """
    Get personalized crisis resource recommendations
    """
    try:
        resources = await crisis_crud.get_recommended_resources(
            current_user.id, content, mood, category, limit
        )

        # Determine if emergency resources are suggested
        emergency_suggested = any(
            resource['category'] in ['suicide_prevention', 'emergency']
            for resource in resources
        )

        # Generate reason for recommendations
        reason = None
        if content and any(keyword in content.lower() for keyword in ['suicide', 'kill myself', 'harm']):
            reason = "Based on your content, we recommend these emergency resources"
        elif mood and mood.lower() in ['sad', 'depressed', 'hopeless']:
            reason = f"Based on your mood ({mood}), these resources might help"
        elif category:
            reason = f"Resources in the {category} category"
        else:
            reason = "General crisis support resources"

        return ResourceRecommendationResponse(
            resources=[CrisisResourceResponse(**dict(resource)) for resource in resources],
            recommendations_based_on={"mood": mood, "content_analysis": bool(content)},
            user_preferences_used=False  # Simple implementation for now
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recommendations: {str(e)}"
        )

@router.get("/emergency-contacts/", response_model=EmergencyContactsResponse)
async def get_emergency_contacts(
    current_user: User = Depends(get_current_user)
):
    """
    Get user's emergency contacts
    """
    try:
        contacts = await crisis_crud.get_emergency_contacts(current_user.id)
        has_primary = any(contact['is_primary'] for contact in contacts)
        total = await crisis_crud.count_user_contacts(current_user.id)

        return EmergencyContactsResponse(
            contacts=[EmergencyContactResponse(**dict(contact)) for contact in contacts],
            total=total,
            has_primary=has_primary
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving emergency contacts: {str(e)}"
        )

@router.post("/emergency-contacts/", response_model=EmergencyContactResponse)
async def create_emergency_contact(
    contact: EmergencyContactCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new emergency contact
    """
    try:
        result = await crisis_crud.create_emergency_contact(current_user.id, contact)
        if result:
            return EmergencyContactResponse(**dict(result))
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create emergency contact"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating emergency contact: {str(e)}"
        )

@router.put("/emergency-contacts/{contact_id}", response_model=EmergencyContactResponse)
async def update_emergency_contact(
    contact_id: str,
    contact_update: EmergencyContactUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update an emergency contact
    """
    try:
        # First check if contact exists and user owns it
        existing_contact = await crisis_crud.get_emergency_contact(UUID(contact_id), current_user.id)
        if not existing_contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Emergency contact not found"
            )

        # Update the contact
        updated_contact = await crisis_crud.update_emergency_contact(
            UUID(contact_id), current_user.id, contact_update
        )
        if updated_contact:
            return EmergencyContactResponse(**dict(updated_contact))
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update emergency contact"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating emergency contact: {str(e)}"
        )

@router.delete("/emergency-contacts/{contact_id}")
async def delete_emergency_contact(
    contact_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete an emergency contact
    """
    try:
        # First check if contact exists
        existing_contact = await crisis_crud.get_emergency_contact(UUID(contact_id), current_user.id)
        if not existing_contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Emergency contact not found"
            )

        # Delete the contact
        success = await crisis_crud.delete_emergency_contact(UUID(contact_id), current_user.id)
        if success:
            return {"message": "Emergency contact deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete emergency contact"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting emergency contact: {str(e)}"
        )

@router.get("/preferences/", response_model=UserCrisisPreferencesResponse)
async def get_crisis_preferences(
    current_user: User = Depends(get_current_user)
):
    """
    Get user's crisis preferences
    """
    try:
        preferences = await crisis_crud.get_user_crisis_preferences(current_user.id)
        if not preferences:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Crisis preferences not found"
            )
        return UserCrisisPreferencesResponse(**dict(preferences))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving crisis preferences: {str(e)}"
        )

@router.post("/preferences/", response_model=UserCrisisPreferencesResponse)
async def create_crisis_preferences(
    preferences: UserCrisisPreferencesCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create user's crisis preferences
    """
    try:
        # Check if preferences already exist
        existing = await crisis_crud.get_user_crisis_preferences(current_user.id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Crisis preferences already exist. Use PUT to update."
            )

        result = await crisis_crud.create_user_crisis_preferences(current_user.id, preferences)
        if result:
            return UserCrisisPreferencesResponse(**dict(result))
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create crisis preferences"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating crisis preferences: {str(e)}"
        )

@router.put("/preferences/", response_model=UserCrisisPreferencesResponse)
async def update_crisis_preferences(
    preferences: UserCrisisPreferencesUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update user's crisis preferences
    """
    try:
        # Check if preferences exist
        existing = await crisis_crud.get_user_crisis_preferences(current_user.id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Crisis preferences not found. Use POST to create first."
            )

        updated_preferences = await crisis_crud.update_user_crisis_preferences(
            current_user.id, preferences
        )
        if updated_preferences:
            return UserCrisisPreferencesResponse(**dict(updated_preferences))
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update crisis preferences"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating crisis preferences: {str(e)}"
        )

# ========== NEW ENDPOINTS FOR ADDITIONAL TABLES ==========

# Safety Plans Endpoints
@router.post("/safety-plans/", response_model=SafetyPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_safety_plan(
    plan: SafetyPlanCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new safety plan
    """
    try:
        result = await crisis_crud.create_safety_plan(current_user.id, plan)
        if result:
            return SafetyPlanResponse(**dict(result))
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create safety plan"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating safety plan: {str(e)}"
        )

@router.get("/safety-plans/", response_model=SafetyPlansResponse)
async def get_safety_plans(
    current_user: User = Depends(get_current_user)
):
    """
    Get user's safety plans
    """
    try:
        plans = await crisis_crud.get_safety_plans(current_user.id)
        active_plan = await crisis_crud.get_active_safety_plan(current_user.id)
        
        return SafetyPlansResponse(
            plans=[SafetyPlanResponse(**dict(plan)) for plan in plans],
            total=len(plans),
            active_plan=SafetyPlanResponse(**dict(active_plan)) if active_plan else None
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving safety plans: {str(e)}"
        )

@router.get("/safety-plans/{plan_id}", response_model=SafetyPlanResponse)
async def get_safety_plan(
    plan_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific safety plan
    """
    try:
        plan = await crisis_crud.get_safety_plan(UUID(plan_id), current_user.id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Safety plan not found"
            )
        return SafetyPlanResponse(**dict(plan))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving safety plan: {str(e)}"
        )

@router.put("/safety-plans/{plan_id}", response_model=SafetyPlanResponse)
async def update_safety_plan(
    plan_id: str,
    plan_update: SafetyPlanUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update a safety plan
    """
    try:
        # First check if plan exists and user owns it
        existing_plan = await crisis_crud.get_safety_plan(UUID(plan_id), current_user.id)
        if not existing_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Safety plan not found"
            )

        # Update the plan
        updated_plan = await crisis_crud.update_safety_plan(
            UUID(plan_id), current_user.id, plan_update
        )
        if updated_plan:
            return SafetyPlanResponse(**dict(updated_plan))
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update safety plan"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating safety plan: {str(e)}"
        )

@router.delete("/safety-plans/{plan_id}")
async def delete_safety_plan(
    plan_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a safety plan
    """
    try:
        # First check if plan exists
        existing_plan = await crisis_crud.get_safety_plan(UUID(plan_id), current_user.id)
        if not existing_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Safety plan not found"
            )

        # Delete the plan
        success = await crisis_crud.delete_safety_plan(UUID(plan_id), current_user.id)
        if success:
            return {"message": "Safety plan deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete safety plan"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting safety plan: {str(e)}"
        )

# Wellness Checkins Endpoints
@router.post("/wellness-checkins/", response_model=WellnessCheckinResponse, status_code=status.HTTP_201_CREATED)
async def create_wellness_checkin(
    checkin: WellnessCheckinCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new wellness checkin
    """
    try:
        result = await crisis_crud.create_wellness_checkin(current_user.id, checkin)
        if result:
            return WellnessCheckinResponse(**dict(result))
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create wellness checkin"
            )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating wellness checkin: {str(e)}"
        )

@router.get("/wellness-checkins/", response_model=WellnessCheckinsResponse)
async def get_wellness_checkins(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's wellness checkins
    """
    try:
        skip = (page - 1) * limit
        checkins = await crisis_crud.get_wellness_checkins(current_user.id, limit, skip)
        today_checkin = await crisis_crud.get_today_wellness_checkin(current_user.id)
        
        return WellnessCheckinsResponse(
            checkins=[WellnessCheckinResponse(**dict(checkin)) for checkin in checkins],
            total=len(checkins),
            today_checkin=WellnessCheckinResponse(**dict(today_checkin)) if today_checkin else None
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving wellness checkins: {str(e)}"
        )

@router.get("/wellness-checkins/today", response_model=WellnessCheckinResponse)
async def get_today_wellness_checkin(
    current_user: User = Depends(get_current_user)
):
    """
    Get today's wellness checkin
    """
    try:
        checkin = await crisis_crud.get_today_wellness_checkin(current_user.id)
        if not checkin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No wellness checkin found for today"
            )
        return WellnessCheckinResponse(**dict(checkin))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving today's wellness checkin: {str(e)}"
        )

@router.put("/wellness-checkins/{checkin_id}", response_model=WellnessCheckinResponse)
async def update_wellness_checkin(
    checkin_id: str,
    checkin_update: WellnessCheckinUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update a wellness checkin
    """
    try:
        # First check if checkin exists and user owns it
        existing_checkin = await crisis_crud.get_wellness_checkin(UUID(checkin_id), current_user.id)
        if not existing_checkin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wellness checkin not found"
            )

        # Update the checkin
        updated_checkin = await crisis_crud.update_wellness_checkin(
            UUID(checkin_id), current_user.id, checkin_update
        )
        if updated_checkin:
            return WellnessCheckinResponse(**dict(updated_checkin))
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update wellness checkin"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating wellness checkin: {str(e)}"
        )

# Crisis Alerts Endpoints
@router.post("/crisis-alerts/", response_model=CrisisAlertResponse, status_code=status.HTTP_201_CREATED)
async def create_crisis_alert(
    alert: CrisisAlertCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new crisis alert
    """
    try:
        result = await crisis_crud.create_crisis_alert(current_user.id, alert)
        if result:
            return CrisisAlertResponse(**dict(result))
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create crisis alert"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating crisis alert: {str(e)}"
        )

@router.get("/crisis-alerts/", response_model=CrisisAlertsResponse)
async def get_crisis_alerts(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's crisis alerts
    """
    try:
        skip = (page - 1) * limit
        alerts = await crisis_crud.get_user_crisis_alerts(current_user.id, limit, skip)
        active_alerts = await crisis_crud.get_active_crisis_alerts(current_user.id)
        
        return CrisisAlertsResponse(
            alerts=[CrisisAlertResponse(**dict(alert)) for alert in alerts],
            total=len(alerts),
            active_alerts=[CrisisAlertResponse(**dict(alert)) for alert in active_alerts]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving crisis alerts: {str(e)}"
        )

@router.post("/crisis-alerts/{alert_id}/resolve", response_model=CrisisAlertResponse)
async def resolve_crisis_alert(
    alert_id: str,
    resolution_notes: str = None,
    current_user: User = Depends(get_current_user)
):
    """
    Mark a crisis alert as resolved
    """
    try:
        # First check if alert exists and user owns it
        existing_alert = await crisis_crud.get_crisis_alert(UUID(alert_id), current_user.id)
        if not existing_alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Crisis alert not found"
            )

        # Resolve the alert
        resolved_alert = await crisis_crud.resolve_crisis_alert(
            UUID(alert_id), current_user.id, resolution_notes
        )
        if resolved_alert:
            return CrisisAlertResponse(**dict(resolved_alert))
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to resolve crisis alert"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resolving crisis alert: {str(e)}"
        )
