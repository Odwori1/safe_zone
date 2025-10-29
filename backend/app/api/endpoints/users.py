from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from uuid import UUID
from app.core.security import get_current_user
from app.crud.user import user_crud
from app.schemas.user import User, UserSearchResults, UserSearchResult
from app.database.database import database
from app.schemas.user_relationships import FollowRequest, BlockRequest, ReportRequest, UserRelationshipStatus
from app.crud.user_relationships import user_relationships_crud

router = APIRouter()

@router.get("/search", response_model=UserSearchResults)
async def search_users(
    query: Optional[str] = Query(None, description="Search by username, email, or full name"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    include_unverified: bool = Query(False, description="Include unverified users (debug)"),
    current_user: User = Depends(get_current_user)
):
    """
    Search for users with proper privacy controls and RLS
    """
    try:
        print(f"🔍 USER SEARCH: current_user_id={current_user.id}, query='{query}', include_unverified={include_unverified}")

        users = await user_crud.search_users(
            current_user_id=current_user.id,
            search_query=query,
            limit=limit,
            offset=offset,
            include_unverified=include_unverified
        )

        print(f"✅ USER SEARCH: Found {len(users)} users")
        for user in users:
            print(f"   - {user['username']} (active: {user['is_active']}, verified: {user.get('is_verified', 'N/A')})")

        # Convert to response format - FIXED: Include is_active
        user_results = []
        for user in users:
            user_results.append(UserSearchResult(
                id=user['id'],
                username=user['username'],
                full_name=user['full_name'],
                bio=user['bio'],
                profile_picture=user['profile_picture'],
                is_helper=user['is_helper'],
                helper_specialties=user['helper_specialties'],
                is_verified=user['is_verified'],
                is_active=user['is_active'],  # ADD THIS LINE
                created_at=user['created_at']
            ))

        return UserSearchResults(
            users=user_results,
            total=len(user_results),
            has_more=len(user_results) == limit
        )

    except Exception as e:
        print(f"❌ USER SEARCH ERROR: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/suggestions", response_model=UserSearchResults)
async def get_user_suggestions(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user)
):
    """
    Get user discovery suggestions
    """
    try:
        print(f"🔍 Getting user suggestions, limit: {limit}")

        users = await user_crud.get_user_suggestions(
            current_user_id=current_user.id,
            limit=limit
        )

        print(f"✅ Found {len(users)} suggestions")

        user_results = []
        for user in users:
            user_results.append(UserSearchResult(
                id=user['id'],
                username=user['username'],
                full_name=user['full_name'],
                bio=user['bio'],
                profile_picture=user['profile_picture'],
                is_helper=user['is_helper'],
                helper_specialties=user['helper_specialties'],
                is_verified=user['is_verified'],
                is_active=user['is_active'],  # ADD THIS LINE
                created_at=user['created_at']
            ))

        return UserSearchResults(
            users=user_results,
            total=len(user_results),
            has_more=len(user_results) == limit
        )

    except Exception as e:
        print(f"❌ Suggestions error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get suggestions: {str(e)}")

# ADDITIONAL DEBUG ROUTE FOR RLS TESTING
@router.get("/debug/rls-test")
async def debug_rls_test(current_user: User = Depends(get_current_user)):
    """
    Test RLS policies and user visibility
    """
    try:
        async with database.pool.acquire() as conn:
            # Test 1: Count all users without RLS
            total_no_rls = await conn.fetchval("SELECT COUNT(*) FROM users")

            # Test 2: Count with RLS
            await conn.execute("SELECT set_current_user_id($1);", str(current_user.id))
            total_with_rls = await conn.fetchval("SELECT COUNT(*) FROM users")

            # Test 3: Get all usernames with RLS
            users_with_rls = await conn.fetch("SELECT id, username, is_active, is_verified FROM users")

            return {
                "total_users_no_rls": total_no_rls,
                "total_users_with_rls": total_with_rls,
                "current_user_id": str(current_user.id),
                "visible_users": [
                    {
                        "id": str(user['id']),
                        "username": user['username'],
                        "is_active": user['is_active'],
                        "is_verified": user['is_verified']
                    } for user in users_with_rls
                ]
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RLS test failed: {str(e)}")


# ADDITIONAL DEBUG ROUTE FOR GETTING ALL USERS
@router.get("/debug/all-users")
async def debug_all_users(
    current_user: User = Depends(get_current_user),
    limit: int = 50
):
    """
    Get all users with their exact data for debugging
    """
    try:
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_current_user_id($1);", str(current_user.id))

            users = await conn.fetch("""
                SELECT id, username, email, full_name, is_active, is_verified, created_at
                FROM users
                ORDER BY created_at DESC
                LIMIT $1
            """, limit)

            user_list = []
            for user in users:
                user_list.append({
                    "id": str(user['id']),
                    "username": user['username'],
                    "email": user['email'],
                    "full_name": user['full_name'],
                    "is_active": user['is_active'],
                    "is_verified": user['is_verified'],
                    "is_current_user": str(user['id']) == str(current_user.id),
                    "created_at": user['created_at'].isoformat()
                })

            return {
                "total_users": len(users),
                "current_user_id": str(current_user.id),
                "users": user_list
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Debug failed: {str(e)}")

@router.post("/follow", response_model=dict)
async def follow_user(
    request: FollowRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Follow another user
    """
    try:
        # Check if not trying to follow self
        if current_user.id == request.following_id:
            raise HTTPException(status_code=400, detail="Cannot follow yourself")

        # Check if already following
        existing = await user_relationships_crud.get_relationship(
            current_user.id, request.following_id, "follow"
        )
        if existing:
            raise HTTPException(status_code=400, detail="Already following this user")

        # Check if blocked
        blocked = await user_relationships_crud.get_relationship(
            current_user.id, request.following_id, "block"
        )
        if blocked:
            raise HTTPException(status_code=400, detail="Cannot follow blocked user")

        # Create follow relationship
        relationship = await user_relationships_crud.create_relationship(
            current_user.id, request.following_id, "follow"
        )

        return {"message": "Successfully followed user", "following": True}

    except Exception as e:
        print(f"❌ Follow error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to follow user: {str(e)}")

@router.delete("/unfollow/{user_id}", response_model=dict)
async def unfollow_user(
    user_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Unfollow a user
    """
    try:
        success = await user_relationships_crud.delete_relationship(
            current_user.id, user_id, "follow"
        )

        if not success:
            raise HTTPException(status_code=404, detail="Not following this user")

        return {"message": "Successfully unfollowed user", "following": False}

    except Exception as e:
        print(f"❌ Unfollow error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to unfollow user: {str(e)}")

@router.get("/relationships/{user_id}", response_model=UserRelationshipStatus)
async def get_relationship_status(
    user_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Get relationship status with another user
    """
    try:
        status = await user_relationships_crud.get_relationship_status(current_user.id, user_id)
        return status
    except Exception as e:
        print(f"❌ Relationship status error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get relationship status: {str(e)}")

@router.post("/block", response_model=dict)
async def block_user(
    request: BlockRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Block another user
    """
    try:
        # Check if not trying to block self
        if current_user.id == request.blocked_user_id:
            raise HTTPException(status_code=400, detail="Cannot block yourself")

        # Check if already blocked
        existing = await user_relationships_crud.get_relationship(
            current_user.id, request.blocked_user_id, "block"
        )
        if existing:
            raise HTTPException(status_code=400, detail="Already blocking this user")

        # Create block relationship
        relationship = await user_relationships_crud.create_relationship(
            current_user.id, request.blocked_user_id, "block"
        )

        return {"message": "Successfully blocked user", "blocked": True}

    except Exception as e:
        print(f"❌ Block error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to block user: {str(e)}")

@router.delete("/unblock/{user_id}", response_model=dict)
async def unblock_user(
    user_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Unblock a user
    """
    try:
        success = await user_relationships_crud.delete_relationship(
            current_user.id, user_id, "block"
        )

        if not success:
            raise HTTPException(status_code=404, detail="Not blocking this user")

        return {"message": "Successfully unblocked user", "blocked": False}

    except Exception as e:
        print(f"❌ Unblock error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to unblock user: {str(e)}")

@router.post("/report", response_model=dict)
async def report_user(
    request: ReportRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Report a user
    """
    try:
        # Check if not trying to report self
        if current_user.id == request.reported_user_id:
            raise HTTPException(status_code=400, detail="Cannot report yourself")

        # Create user report
        report = await user_relationships_crud.create_user_report(
            current_user.id,
            request.reported_user_id,
            request.report_reason,
            request.report_details
        )

        return {"message": "Report submitted successfully", "report_id": report['id']}

    except Exception as e:
        print(f"❌ Report error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to submit report: {str(e)}")

@router.get("/reports/my", response_model=List[dict])
async def get_my_reports(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's reports
    """
    try:
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_current_user_id($1);", str(current_user.id))
            
            reports = await conn.fetch("""
                SELECT id, reported_user_id, report_reason, report_details, report_status, created_at
                FROM user_reports 
                WHERE reporter_id = $1
                ORDER BY created_at DESC
            """, current_user.id)
            
            return [dict(report) for report in reports]
            
    except Exception as e:
        print(f"❌ Get reports error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get reports: {str(e)}")
