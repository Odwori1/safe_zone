from pydantic import BaseModel, EmailStr, validator, ConfigDict, field_validator
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
import json
from app.utils.timezone import timezone_handler
from .base import TimeStampedSchema

class UserBase(BaseModel):
    """Base user schema with common fields"""
    model_config = ConfigDict(from_attributes=True)
    
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    timezone: str = "UTC"
    locale: str = "en-US"
    
    @validator('timezone')
    def validate_timezone(cls, v):
        if not timezone_handler.validate_timezone(v):
            raise ValueError('Invalid timezone')
        return v

class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    """Schema for updating a user"""
    model_config = ConfigDict(from_attributes=True)
    
    full_name: Optional[str] = None
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
    timezone: Optional[str] = None
    locale: Optional[str] = None
    is_helper: Optional[bool] = None
    helper_credentials: Optional[str] = None
    helper_specialties: Optional[str] = None
    seeker_preferences: Optional[Dict[str, Any]] = None
    
    @validator('timezone')
    def validate_timezone(cls, v):
        if v and not timezone_handler.validate_timezone(v):
            raise ValueError('Invalid timezone')
        return v
    
    @validator('bio')
    def validate_bio_length(cls, v):
        if v and len(v) > 1000:
            raise ValueError('Bio must be less than 1000 characters')
        return v

class UserProfileUpdate(BaseModel):
    """Schema for updating user profile specifically"""
    model_config = ConfigDict(from_attributes=True)
    
    full_name: Optional[str] = None
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
    timezone: Optional[str] = None
    locale: Optional[str] = None
    
    @validator('timezone')
    def validate_timezone(cls, v):
        if v and not timezone_handler.validate_timezone(v):
            raise ValueError('Invalid timezone')
        return v

class HelperApplication(BaseModel):
    """Schema for applying to be a helper"""
    credentials: str
    specialties: str
    bio: Optional[str] = None
    
    @validator('credentials')
    def validate_credentials(cls, v):
        if len(v) < 10:
            raise ValueError('Please provide detailed credentials')
        return v
    
    @validator('specialties')
    def validate_specialties(cls, v):
        if len(v) < 5:
            raise ValueError('Please specify your specialties')
        return v

class UserInDB(TimeStampedSchema):
    """User schema as stored in database"""
    model_config = ConfigDict(from_attributes=True)
    
    email: str
    username: str
    full_name: Optional[str] = None
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
    timezone: str
    locale: str
    role: str = "seeker"
    is_active: bool = True
    is_verified: bool = False
    is_helper: bool = False
    helper_credentials: Optional[str] = None
    helper_specialties: Optional[str] = None
    helper_verification_status: str = "not_applied"
    seeker_preferences: Dict[str, Any] = {}
    last_login: Optional[datetime] = None

    @field_validator('seeker_preferences', mode='before')
    @classmethod
    def parse_seeker_preferences(cls, v):
        """Parse seeker_preferences from string to dict if needed"""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return {}
        return v or {}

class UserResponse(UserInDB):
    """User schema for API responses"""
    pass


class User(UserInDB):
    """Main User schema for dependencies and general use"""
    pass

class PublicUserProfile(BaseModel):
    """Public user profile for safe sharing"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    username: str
    full_name: Optional[str] = None
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
    is_helper: bool
    helper_specialties: Optional[str] = None
    created_at: datetime

class UserSearchResult(BaseModel):
    """Schema for user search results"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    full_name: Optional[str] = None
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
    is_helper: bool
    helper_specialties: Optional[str] = None
    is_verified: bool  # ADD THIS
    is_active: bool  # ADD THIS FIELD
    created_at: datetime

class UserSearchResults(BaseModel):
    """Schema for paginated user search results"""
    users: List[UserSearchResult]
    total: int
    has_more: bool
