from pydantic import BaseModel, Field, field_validator, ConfigDict, HttpUrl
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from enum import Enum
from app.utils.timezone import timezone_handler
from .base import TimeStampedSchema

class ResourceCategory(str, Enum):
    """Crisis resource categories"""
    SUICIDE_PREVENTION = "suicide_prevention"
    CRISIS_SUPPORT = "crisis_support"
    MENTAL_HEALTH = "mental_health"
    SUBSTANCE_ABUSE = "substance_abuse"
    DOMESTIC_VIOLENCE = "domestic_violence"
    EMERGENCY = "emergency"
    INFORMATION = "information"
    SUPPORT_GROUP = "support_group"

class GeographicScope(str, Enum):
    """Geographic scope of resources"""
    GLOBAL = "global"
    US = "US"
    EUROPE = "europe"
    ASIA = "asia"
    AFRICA = "africa"
    LOCAL = "local"

class CrisisResourceBase(BaseModel):
    """Base crisis resource schema"""
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    category: ResourceCategory
    phone_number: Optional[str] = Field(None, max_length=50)
    website_url: Optional[str] = Field(None, max_length=500)
    chat_url: Optional[str] = Field(None, max_length=500)
    text_line: Optional[str] = Field(None, max_length=50)
    languages: List[str] = Field(default=["en"])
    operating_hours: Optional[Dict[str, Any]] = None
    geographic_scope: GeographicScope = GeographicScope.GLOBAL
    tags: List[str] = Field(default=[])

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name is not empty"""
        if not v.strip():
            raise ValueError('Resource name cannot be empty')
        return v.strip()

    @field_validator('website_url', 'chat_url')
    @classmethod
    def validate_urls(cls, v: Optional[str]) -> Optional[str]:
        """Validate URLs if provided"""
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v

class CrisisResourceCreate(CrisisResourceBase):
    """Schema for creating a crisis resource (admin only)"""
    is_active: bool = True
    priority: int = Field(1, ge=1, le=10)

class CrisisResourceUpdate(BaseModel):
    """Schema for updating a crisis resource"""
    model_config = ConfigDict(from_attributes=True)

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[ResourceCategory] = None
    phone_number: Optional[str] = Field(None, max_length=50)
    website_url: Optional[str] = Field(None, max_length=500)
    chat_url: Optional[str] = Field(None, max_length=500)
    text_line: Optional[str] = Field(None, max_length=50)
    languages: Optional[List[str]] = None
    operating_hours: Optional[Dict[str, Any]] = None
    geographic_scope: Optional[GeographicScope] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = Field(None, ge=1, le=10)
    tags: Optional[List[str]] = None

class CrisisResourceInDB(TimeStampedSchema):
    """Crisis resource schema as stored in database"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: Optional[str] = None
    category: ResourceCategory
    phone_number: Optional[str] = None
    website_url: Optional[str] = None
    chat_url: Optional[str] = None
    text_line: Optional[str] = None
    languages: List[str]
    operating_hours: Optional[Dict[str, Any]] = None
    geographic_scope: GeographicScope
    is_active: bool
    priority: int
    tags: List[str]

class CrisisResourceResponse(CrisisResourceInDB):
    """Crisis resource schema for API responses"""
    pass

class EmergencyContactBase(BaseModel):
    """Base emergency contact schema"""
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=1, max_length=200)
    relationship: Optional[str] = Field(None, max_length=100)
    phone_number: str = Field(..., min_length=1, max_length=50)
    email: Optional[str] = Field(None, max_length=200)
    is_primary: bool = False
    can_receive_alerts: bool = False
    notes: Optional[str] = Field(None, max_length=500)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name is not empty"""
        if not v.strip():
            raise ValueError('Contact name cannot be empty')
        return v.strip()

    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        """Validate phone number is not empty"""
        if not v.strip():
            raise ValueError('Phone number cannot be empty')
        return v.strip()

class EmergencyContactCreate(EmergencyContactBase):
    """Schema for creating an emergency contact"""
    pass

class EmergencyContactUpdate(BaseModel):
    """Schema for updating an emergency contact"""
    model_config = ConfigDict(from_attributes=True)

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    relationship: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[str] = Field(None, max_length=200)
    is_primary: Optional[bool] = None
    can_receive_alerts: Optional[bool] = None
    notes: Optional[str] = Field(None, max_length=500)

class EmergencyContactInDB(TimeStampedSchema):
    """Emergency contact schema as stored in database"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    name: str
    relationship: Optional[str] = None
    phone_number: str
    email: Optional[str] = None
    is_primary: bool
    can_receive_alerts: bool
    notes: Optional[str] = None

class EmergencyContactResponse(EmergencyContactInDB):
    """Emergency contact schema for API responses"""
    pass

class UserCrisisPreferencesBase(BaseModel):
    """Base user crisis preferences schema"""
    model_config = ConfigDict(from_attributes=True)

    preferred_language: str = Field("en", max_length=10)
    country_code: Optional[str] = Field(None, max_length=5)
    emergency_contact_instructions: Optional[str] = Field(None, max_length=1000)
    medical_information: Optional[str] = Field(None, max_length=2000)
    consent_to_contact: bool = False

class UserCrisisPreferencesCreate(UserCrisisPreferencesBase):
    """Schema for creating user crisis preferences"""
    pass

class UserCrisisPreferencesUpdate(BaseModel):
    """Schema for updating user crisis preferences"""
    model_config = ConfigDict(from_attributes=True)

    preferred_language: Optional[str] = Field(None, max_length=10)
    country_code: Optional[str] = Field(None, max_length=5)
    emergency_contact_instructions: Optional[str] = Field(None, max_length=1000)
    medical_information: Optional[str] = Field(None, max_length=2000)
    consent_to_contact: Optional[bool] = None

class UserCrisisPreferencesInDB(TimeStampedSchema):
    """User crisis preferences schema as stored in database"""
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    preferred_language: str
    country_code: Optional[str] = None
    emergency_contact_instructions: Optional[str] = None
    medical_information: Optional[str] = None
    consent_to_contact: bool

class UserCrisisPreferencesResponse(UserCrisisPreferencesInDB):
    """User crisis preferences schema for API responses"""
    pass

class CrisisResourcesResponse(BaseModel):
    """Response for crisis resources with filtering"""
    resources: List[CrisisResourceResponse]
    total: int
    user_location: Optional[str] = None

class EmergencyContactsResponse(BaseModel):
    """Response for emergency contacts"""
    contacts: List[EmergencyContactResponse]
    total: int
    has_primary: bool

class ResourceRecommendationRequest(BaseModel):
    """Request for resource recommendations"""
    content: Optional[str] = Field(None, description="Text content to analyze for recommendations")
    mood: Optional[str] = Field(None, description="Current mood")
    category_filter: Optional[ResourceCategory] = None
    limit: int = Field(5, ge=1, le=20)

class ResourceRecommendationResponse(BaseModel):
    """Response for resource recommendations"""
    recommended_resources: List[CrisisResourceResponse]
    reason: Optional[str] = None
    emergency_suggested: bool = False
