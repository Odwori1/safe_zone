from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID

class BaseSchema(BaseModel):
    """Base schema with common fields"""
    class Config:
        from_attributes = True  # Updated from orm_mode

class TimeStampedSchema(BaseSchema):
    """Schema with timestamp fields"""
    id: UUID
    created_at: datetime
    updated_at: datetime

class PaginatedResponse(BaseSchema):
    """Base schema for paginated responses"""
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool
