from typing import List, Optional, Dict, Any
from uuid import UUID
from app.database.database import database

class UserRelationshipsCRUD:
    async def create_relationship(self, follower_id: UUID, following_id: UUID, relationship_type: str) -> Dict[str, Any]:
        """
        Create a follow or block relationship
        """
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_current_user_id($1);", str(follower_id))
            
            result = await conn.fetchrow("""
                INSERT INTO user_relationships (follower_id, following_id, relationship_type)
                VALUES ($1, $2, $3)
                RETURNING id, follower_id, following_id, relationship_type, created_at
            """, follower_id, following_id, relationship_type)
            
            return dict(result) if result else None

    async def delete_relationship(self, follower_id: UUID, following_id: UUID, relationship_type: str) -> bool:
        """
        Delete a follow or block relationship
        """
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_current_user_id($1);", str(follower_id))
            
            result = await conn.execute("""
                DELETE FROM user_relationships 
                WHERE follower_id = $1 AND following_id = $2 AND relationship_type = $3
            """, follower_id, following_id, relationship_type)
            
            return "DELETE 1" in result

    async def get_relationship(self, follower_id: UUID, following_id: UUID, relationship_type: str) -> Dict[str, Any]:
        """
        Get a specific relationship
        """
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_current_user_id($1);", str(follower_id))
            
            result = await conn.fetchrow("""
                SELECT id, follower_id, following_id, relationship_type, created_at
                FROM user_relationships
                WHERE follower_id = $1 AND following_id = $2 AND relationship_type = $3
            """, follower_id, following_id, relationship_type)
            
            return dict(result) if result else None

    async def get_relationship_status(self, current_user_id: UUID, target_user_id: UUID) -> Dict[str, bool]:
        """
        Get comprehensive relationship status between two users
        """
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_current_user_id($1);", str(current_user_id))
            
            # Check if current user is following target
            following = await conn.fetchrow("""
                SELECT 1 FROM user_relationships 
                WHERE follower_id = $1 AND following_id = $2 AND relationship_type = 'follow'
            """, current_user_id, target_user_id)
            
            # Check if current user has blocked target
            blocked = await conn.fetchrow("""
                SELECT 1 FROM user_relationships 
                WHERE follower_id = $1 AND following_id = $2 AND relationship_type = 'block'
            """, current_user_id, target_user_id)
            
            # Check if current user is blocked by target
            blocked_by = await conn.fetchrow("""
                SELECT 1 FROM user_relationships 
                WHERE follower_id = $2 AND following_id = $1 AND relationship_type = 'block'
            """, current_user_id, target_user_id)
            
            return {
                "is_following": following is not None,
                "is_blocked": blocked is not None,
                "is_blocked_by": blocked_by is not None
            }

    async def get_followers(self, user_id: UUID, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get users who follow the specified user
        """
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            
            results = await conn.fetch("""
                SELECT ur.follower_id as user_id, u.username, u.full_name, u.profile_picture, u.is_helper
                FROM user_relationships ur
                JOIN users u ON ur.follower_id = u.id
                WHERE ur.following_id = $1 AND ur.relationship_type = 'follow'
                ORDER BY ur.created_at DESC
                LIMIT $2 OFFSET $3
            """, user_id, limit, offset)
            
            return [dict(row) for row in results]

    async def get_following(self, user_id: UUID, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get users that the specified user is following
        """
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            
            results = await conn.fetch("""
                SELECT ur.following_id as user_id, u.username, u.full_name, u.profile_picture, u.is_helper
                FROM user_relationships ur
                JOIN users u ON ur.following_id = u.id
                WHERE ur.follower_id = $1 AND ur.relationship_type = 'follow'
                ORDER BY ur.created_at DESC
                LIMIT $2 OFFSET $3
            """, user_id, limit, offset)
            
            return [dict(row) for row in results]

    async def create_user_report(self, reporter_id: UUID, reported_user_id: UUID, 
                               report_reason: str, report_details: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a user report
        """
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_current_user_id($1);", str(reporter_id))
            
            result = await conn.fetchrow("""
                INSERT INTO user_reports (reporter_id, reported_user_id, report_reason, report_details)
                VALUES ($1, $2, $3, $4)
                RETURNING id, reporter_id, reported_user_id, report_reason, report_details, report_status, created_at
            """, reporter_id, reported_user_id, report_reason, report_details)
            
            return dict(result) if result else None

# Create global instance
user_relationships_crud = UserRelationshipsCRUD()
