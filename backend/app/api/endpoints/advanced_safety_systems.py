"""
Advanced Safety Systems Endpoints for Phase 4, Item 2
Following EXACT same patterns as ai_personalization.py endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from uuid import UUID

from app.schemas.advanced_safety_systems import (
    CrisisAlertResponse, CrisisAlertUpdate,
    SafetyPlanCreate, SafetyPlanResponse, SafetyPlanUpdate,
    SafetyPlanTemplateResponse,
    WellnessCheckInResponse, WellnessCheckInResponseUpdate,
    EscalationProtocolResponse,
    HealthResponse
)
from app.crud.advanced_safety_systems import advanced_safety_systems_crud
from app.core.security import get_current_user
from app.schemas.user import User

router = APIRouter()

# ===== CRISIS DETECTION ALERTS ENDPOINTS =====

@router.get("/alerts/user/{user_id}", response_model=List[CrisisAlertResponse])
async def get_user_crisis_alerts(
    user_id: UUID,
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user)
):
    """
    Get crisis alerts for a specific user
    SECURITY: Users can only see their own alerts
    """
    try:
        # Users can only access their own alerts
        if user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot access alerts for other users"
            )

        alerts = await advanced_safety_systems_crud.get_user_crisis_alerts(
            user_id, current_user.id, status, limit, offset
        )

        return alerts

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch crisis alerts"
        )

# ===== SAFETY PLANS ENDPOINTS =====

@router.get("/safety-plans/current", response_model=SafetyPlanResponse)
async def get_my_safety_plan(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's active safety plan
    SECURITY: Users can only see their own safety plans
    """
    try:
        plan = await advanced_safety_systems_crud.get_user_safety_plan(
            current_user.id, current_user.id
        )

        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active safety plan found"
            )

        return plan

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch safety plan"
        )

@router.post("/safety-plans", response_model=SafetyPlanResponse)
async def create_safety_plan(
    plan_data: SafetyPlanCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new safety plan for current user
    SECURITY: Users can only create their own safety plans
    """
    try:
        plan = await advanced_safety_systems_crud.create_safety_plan(
            current_user.id, plan_data.dict()
        )

        if not plan:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create safety plan"
            )

        return plan

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create safety plan"
        )

@router.put("/safety-plans/{plan_id}", response_model=SafetyPlanResponse)
async def update_safety_plan(
    plan_id: UUID,
    plan_data: SafetyPlanUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update user's safety plan
    SECURITY: Users can only update their own safety plans
    """
    try:
        plan = await advanced_safety_systems_crud.update_safety_plan(
            plan_id, current_user.id, plan_data.dict(exclude_unset=True)
        )

        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Safety plan not found or access denied"
            )

        return plan

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update safety plan"
        )

# ===== SAFETY PLAN TEMPLATES ENDPOINTS =====

@router.get("/safety-plan-templates", response_model=List[SafetyPlanTemplateResponse])
async def get_safety_plan_templates(
    target_audience: Optional[str] = None,
    difficulty_level: Optional[str] = None,
    limit: int = 10,
    offset: int = 0
):
    """
    Get safety plan templates with filtering options
    SECURITY: Public read access to active templates
    """
    try:
        templates = await advanced_safety_systems_crud.get_safety_plan_templates(
            target_audience, difficulty_level, limit, offset
        )

        return templates

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch safety plan templates"
        )

# ===== WELLNESS CHECK-INS ENDPOINTS =====

@router.get("/wellness-check-ins", response_model=List[WellnessCheckInResponse])
async def get_my_wellness_check_ins(
    status: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's wellness check-ins
    SECURITY: Users can only see their own check-ins
    """
    try:
        check_ins = await advanced_safety_systems_crud.get_user_wellness_check_ins(
            current_user.id, current_user.id, status, limit, offset
        )

        return check_ins

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch wellness check-ins"
        )

@router.post("/wellness-check-ins/{check_in_id}/respond")
async def respond_to_wellness_check_in(
    check_in_id: UUID,
    response_data: WellnessCheckInResponseUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Respond to a wellness check-in
    SECURITY: Users can only respond to their own check-ins
    """
    try:
        check_in = await advanced_safety_systems_crud.respond_to_wellness_check_in(
            check_in_id, current_user.id, response_data.dict()
        )

        if not check_in:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wellness check-in not found or access denied"
            )

        return {
            "message": "Wellness check-in response recorded successfully",
            "check_in_id": str(check_in_id),
            "status": check_in["status"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record wellness check-in response"
        )

# ===== ESCALATION PROTOCOLS ENDPOINTS =====

@router.get("/escalation-protocols", response_model=List[EscalationProtocolResponse])
async def get_escalation_protocols(
    risk_level: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Get escalation protocols for different risk levels
    SECURITY: Requires authentication (moderators/admins typically)
    """
    try:
        protocols = await advanced_safety_systems_crud.get_escalation_protocols(
            risk_level, current_user.id
        )

        return protocols

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch escalation protocols"
        )

# ===== HEALTH ENDPOINT =====

@router.get("/health")
async def advanced_safety_systems_health(
    current_user: User = Depends(get_current_user)
):
    """
    Health check for advanced safety systems service
    SECURITY: Requires authentication
    """
    try:
        health_ok = await advanced_safety_systems_crud.health_check(current_user.id)

        if health_ok:
            return {"status": "healthy", "service": "advanced_safety_systems"}
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Advanced safety systems service unavailable"
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Advanced safety systems health check failed"
        )
