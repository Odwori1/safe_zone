from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    """JWT token response schema"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    """Data stored in JWT token"""
    user_id: Optional[str] = None
    email: Optional[str] = None

class PasswordResetRequest(BaseModel):
    """Schema for password reset request"""
    email: str

class PasswordReset(BaseModel):
    """Schema for password reset"""
    token: str
    new_password: str
