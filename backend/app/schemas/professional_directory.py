"""
Professional Directory Schemas for Phase 3, Item 7
Following EXACT same patterns as enhanced_moderation.py schemas
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import time, date, datetime

# ===== PROFESSIONAL PROFILE SCHEMAS =====

class ProfessionalProfileBase(BaseModel):
    professional_title: str = Field(..., min_length=1, max_length=100)
    license_number: Optional[str] = Field(None, max_length=100)
    license_state: Optional[str] = Field(None, max_length=50)
    years_of_experience: Optional[int] = Field(None, ge=0, le=50)
    hourly_rate: Optional[float] = Field(None, ge=0, le=1000)
    bio: Optional[str] = Field(None, max_length=2000)
    approach: Optional[str] = Field(None, max_length=1000)
    specialties: Optional[List[str]] = Field(default_factory=list)
    professional_email: Optional[str] = Field(None, max_length=255)
    professional_phone: Optional[str] = Field(None, max_length=50)
    website_url: Optional[str] = Field(None, max_length=500)

class ProfessionalProfileCreate(ProfessionalProfileBase):
    pass

class ProfessionalProfileUpdate(BaseModel):
    professional_title: Optional[str] = Field(None, min_length=1, max_length=100)
    license_number: Optional[str] = Field(None, max_length=100)
    license_state: Optional[str] = Field(None, max_length=50)
    years_of_experience: Optional[int] = Field(None, ge=0, le=50)
    hourly_rate: Optional[float] = Field(None, ge=0, le=1000)
    bio: Optional[str] = Field(None, max_length=2000)
    approach: Optional[str] = Field(None, max_length=1000)
    specialties: Optional[List[str]] = None
    professional_email: Optional[str] = Field(None, max_length=255)
    professional_phone: Optional[str] = Field(None, max_length=50)
    website_url: Optional[str] = Field(None, max_length=500)
    accepts_new_clients: Optional[bool] = None

class ProfessionalProfileResponse(ProfessionalProfileBase):
    id: UUID
    user_id: UUID
    verification_status: str
    accepts_new_clients: bool
    session_types: List[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ===== PROFESSIONAL DIRECTORY SCHEMAS =====

class ProfessionalDirectoryResponse(BaseModel):
    id: UUID
    user_id: UUID
    username: str
    email: str
    full_name: Optional[str]
    professional_title: str
    license_number: Optional[str]
    license_state: Optional[str]
    years_of_experience: Optional[int]
    hourly_rate: Optional[float]
    bio: Optional[str]
    approach: Optional[str]
    specialties: Optional[List[str]]
    accepts_new_clients: bool
    session_types: List[str]
    verification_status: str
    is_active: bool
    average_rating: float
    review_count: int
    completed_sessions: int

    class Config:
        from_attributes = True

class ProfessionalSearchFilters(BaseModel):
    specialties: Optional[List[str]] = None
    session_types: Optional[List[str]] = None
    min_rating: Optional[float] = Field(None, ge=0, le=5)
    limit: int = Field(50, ge=1, le=100)
    offset: int = Field(0, ge=0)

# ===== VERIFICATION SCHEMAS =====

class ProfessionalVerificationBase(BaseModel):
    document_type: str = Field(..., pattern="^(license|certification|diploma|insurance)$")
    document_name: str = Field(..., min_length=1, max_length=255)
    s3_key: str = Field(..., min_length=1, max_length=500)
    file_size: Optional[int] = Field(None, ge=0)
    mime_type: Optional[str] = Field(None, max_length=100)

class ProfessionalVerificationCreate(ProfessionalVerificationBase):
    pass

class ProfessionalVerificationResponse(ProfessionalVerificationBase):
    id: UUID
    professional_id: UUID
    verification_status: str
    reviewed_by: Optional[UUID]
    reviewed_at: Optional[datetime]
    review_notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ===== AVAILABILITY SCHEMAS =====

class AvailabilitySlotBase(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6)
    start_time: time
    end_time: time
    timezone: str = Field(default="UTC")
    slot_duration_minutes: int = Field(default=60, ge=15, le=240)
    buffer_minutes: int = Field(default=15, ge=0, le=60)
    is_recurring: bool = Field(default=True)
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None

    @validator('end_time')
    def validate_time_range(cls, end_time, values):
        if 'start_time' in values and end_time <= values['start_time']:
            raise ValueError('End time must be after start time')
        return end_time

class AvailabilitySlotCreate(AvailabilitySlotBase):
    pass

class AvailabilitySlotResponse(AvailabilitySlotBase):
    id: UUID
    professional_id: UUID
    is_active: bool
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
