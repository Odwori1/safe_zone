"""
Advanced Safety Systems Schemas for Phase 4, Item 2
Following EXACT same patterns as ai_personalization.py schemas
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

# ===== CRISIS DETECTION ALERTS SCHEMAS =====

class CrisisAlertBase(BaseModel):
    user_id: UUID
    detection_source: str = Field(..., max_length=100)
    source_content_type: Optional[str] = Field(None, max_length=50)
    source_content_id: Optional[UUID] = None
    risk_level: str = Field(..., max_length=20)
    risk_score: float = Field(..., ge=0.0, le=1.0)
    risk_factors: Optional[List[str]] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    alert_message: Optional[str] = None
    detected_patterns: Optional[List[str]] = None
    context_data: Optional[Dict[str, Any]] = None

class CrisisAlertResponse(CrisisAlertBase):
    id: UUID
    status: str
    assigned_moderator_id: Optional[UUID]
    escalation_level: Optional[int]
    automated_actions_taken: Optional[List[str]]
    detected_at: datetime
    reviewed_at: Optional[datetime]
    resolved_at: Optional[datetime]
    moderator_notes: Optional[str]
    resolution_notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CrisisAlertUpdate(BaseModel):
    status: Optional[str] = Field(None, max_length=20)
    assigned_moderator_id: Optional[UUID] = None
    escalation_level: Optional[int] = Field(None, ge=1, le=5)
    moderator_notes: Optional[str] = None
    resolution_notes: Optional[str] = None
    automated_actions_taken: Optional[List[str]] = None

# ===== SAFETY PLANS SCHEMAS =====

class SafetyPlanBase(BaseModel):
    plan_name: str = Field(..., max_length=200)
    personal_warning_signs: Optional[List[str]] = None
    early_warning_triggers: Optional[List[str]] = None
    internal_coping_strategies: Optional[List[str]] = None
    social_coping_strategies: Optional[List[str]] = None
    professional_coping_strategies: Optional[List[str]] = None
    emergency_contact_instructions: Optional[str] = None
    crisis_line_preferences: Optional[List[str]] = None
    means_restriction_plan: Optional[str] = None
    safe_locations: Optional[List[str]] = None

class SafetyPlanCreate(SafetyPlanBase):
    created_from_template_id: Optional[UUID] = None

class SafetyPlanResponse(SafetyPlanBase):
    id: UUID
    user_id: UUID
    plan_version: int
    is_active: bool
    last_reviewed_date: Optional[datetime]
    next_review_date: Optional[datetime]
    created_from_template_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SafetyPlanUpdate(BaseModel):
    plan_name: Optional[str] = Field(None, max_length=200)
    personal_warning_signs: Optional[List[str]] = None
    early_warning_triggers: Optional[List[str]] = None
    internal_coping_strategies: Optional[List[str]] = None
    social_coping_strategies: Optional[List[str]] = None
    professional_coping_strategies: Optional[List[str]] = None
    emergency_contact_instructions: Optional[str] = None
    crisis_line_preferences: Optional[List[str]] = None
    means_restriction_plan: Optional[str] = None
    safe_locations: Optional[List[str]] = None
    is_active: Optional[bool] = None

# ===== SAFETY PLAN TEMPLATES SCHEMAS =====

class SafetyPlanTemplateBase(BaseModel):
    template_name: str = Field(..., max_length=200)
    template_description: Optional[str] = None
    target_audience: Optional[str] = Field(None, max_length=100)
    difficulty_level: Optional[str] = Field(None, max_length=20)
    default_warning_signs: Optional[List[str]] = None
    default_coping_strategies: Optional[List[str]] = None
    default_emergency_instructions: Optional[str] = None
    professional_notes: Optional[str] = None
    available_languages: Optional[List[str]] = None
    recommended_review_frequency_days: Optional[int] = Field(None, ge=1, le=365)

class SafetyPlanTemplateResponse(SafetyPlanTemplateBase):
    id: UUID
    is_public: bool
    is_active: bool
    created_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ===== WELLNESS CHECK-INS SCHEMAS =====

class WellnessCheckInBase(BaseModel):
    user_id: UUID
    check_in_type: str = Field(..., max_length=50)
    trigger_source: Optional[str] = Field(None, max_length=100)
    trigger_alert_id: Optional[UUID] = None
    check_in_message: str
    response_options: Optional[List[str]] = None
    custom_response_prompt: Optional[str] = None

class WellnessCheckInResponse(WellnessCheckInBase):
    id: UUID
    status: str
    user_response: Optional[str]
    selected_options: Optional[List[str]]
    response_mood: Optional[str]
    response_urgency: Optional[str]
    requires_follow_up: Optional[bool]
    follow_up_actions: Optional[List[str]]
    follow_up_notes: Optional[str]
    sent_at: datetime
    responded_at: Optional[datetime]
    follow_up_completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class WellnessCheckInResponseUpdate(BaseModel):
    user_response: Optional[str] = None
    selected_options: Optional[List[str]] = None
    response_mood: Optional[str] = Field(None, max_length=20)
    response_urgency: Optional[str] = Field(None, max_length=20)

# ===== ESCALATION PROTOCOLS SCHEMAS =====

class EscalationProtocolBase(BaseModel):
    protocol_name: str = Field(..., max_length=200)
    trigger_risk_level: str = Field(..., max_length=20)
    trigger_conditions: Optional[List[str]] = None
    required_resources: Optional[List[str]] = None
    immediate_actions: Optional[List[str]] = None
    follow_up_actions: Optional[List[str]] = None
    time_sensitive_actions: Optional[List[str]] = None
    external_services_involvement: Optional[List[str]] = None
    professional_involvement_required: Optional[bool] = None
    internal_communication_template: Optional[str] = None
    user_communication_template: Optional[str] = None
    emergency_contact_communication_template: Optional[str] = None

class EscalationProtocolResponse(EscalationProtocolBase):
    id: UUID
    version: str
    is_active: bool
    last_reviewed_date: Optional[datetime]
    created_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ===== HEALTH SCHEMA =====

class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True
