from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import Optional
from enum import Enum

class RelationshipType(str, Enum):
    FOLLOW = "follow"
    BLOCK = "block"

class ReportStatus(str, Enum):
    PENDING = "pending"
    REVIEWED = "reviewed"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"

class FollowRequest(BaseModel):
    following_id: UUID4

class BlockRequest(BaseModel):
    blocked_user_id: UUID4

class ReportRequest(BaseModel):
    reported_user_id: UUID4
    report_reason: str
    report_details: Optional[str] = None

class UserRelationshipStatus(BaseModel):
    is_following: bool
    is_blocked: bool
    is_blocked_by: bool

class UserRelationship(BaseModel):
    id: UUID4
    follower_id: UUID4
    following_id: UUID4
    relationship_type: RelationshipType
    created_at: datetime

class UserReport(BaseModel):
    id: UUID4
    reporter_id: UUID4
    reported_user_id: UUID4
    report_reason: str
    report_details: Optional[str]
    report_status: ReportStatus
    created_at: datetime
    updated_at: datetime

class FollowerInfo(BaseModel):
    user_id: UUID4
    username: str
    full_name: Optional[str]
    profile_picture: Optional[str]
    is_helper: bool

class FollowingInfo(BaseModel):
    user_id: UUID4
    username: str
    full_name: Optional[str]
    profile_picture: Optional[str]
    is_helper: bool
