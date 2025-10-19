from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from uuid import UUID
from app.schemas.comment import CommentCreate, CommentResponse, CommentUpdate, CommentFeedResponse
from app.schemas.user import User
from app.core.security import get_current_user
from app.crud.comment import comment_crud

router = APIRouter()

@router.post("/", response_model=CommentResponse)
async def create_new_comment(
    comment: CommentCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new comment
    """
    try:
        result = await comment_crud.create(current_user.id, comment)
        if result:
            # Convert asyncpg.Record to dict and handle anonymous comments
            comment_data = dict(result)
            if comment_data.get('is_anonymous'):
                comment_data['username'] = None
                comment_data['user_avatar'] = None
            return CommentResponse(**comment_data)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create comment"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating comment: {str(e)}"
        )

@router.get("/post/{post_id}", response_model=CommentFeedResponse)
async def read_post_comments(
    post_id: str,
    page: int = 1,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve comments for a specific post
    """
    try:
        skip = (page - 1) * limit
        comments = await comment_crud.get_by_post(UUID(post_id), limit, skip)
        
        # Get replies for each comment
        comments_with_replies = []
        for comment in comments:
            comment_dict = dict(comment)
            replies = await comment_crud.get_replies(comment_dict['id'])
            comment_dict['replies'] = [CommentResponse(**dict(reply)) for reply in replies]
            comments_with_replies.append(CommentResponse(**comment_dict))
        
        total = await comment_crud.count_post_comments(UUID(post_id))
        
        return CommentFeedResponse(
            comments=comments_with_replies,
            total=total,
            page=page,
            has_next=(skip + len(comments_with_replies)) < total
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving comments: {str(e)}"
        )

@router.get("/{comment_id}", response_model=CommentResponse)
async def read_comment(
    comment_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific comment by ID
    """
    try:
        comment = await comment_crud.get(UUID(comment_id))
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        # Get replies for this comment
        comment_dict = dict(comment)
        replies = await comment_crud.get_replies(comment_dict['id'])
        comment_dict['replies'] = [CommentResponse(**dict(reply)) for reply in replies]
        
        return CommentResponse(**comment_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving comment: {str(e)}"
        )

@router.put("/{comment_id}", response_model=CommentResponse)
async def update_existing_comment(
    comment_id: str,
    comment_update: CommentUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update a comment
    """
    try:
        # First check if comment exists and user owns it
        existing_comment = await comment_crud.get(UUID(comment_id))
        if not existing_comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        # RLS will prevent updating if user doesn't own the comment
        updated_comment = await comment_crud.update(UUID(comment_id), current_user.id, comment_update)
        if updated_comment:
            comment_dict = dict(updated_comment)
            if comment_dict.get('is_anonymous'):
                comment_dict['username'] = None
                comment_dict['user_avatar'] = None
            return CommentResponse(**comment_dict)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update comment"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating comment: {str(e)}"
        )

@router.delete("/{comment_id}")
async def delete_existing_comment(
    comment_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a comment
    """
    try:
        # First check if comment exists
        existing_comment = await comment_crud.get(UUID(comment_id))
        if not existing_comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        # RLS will prevent deletion if user doesn't own the comment
        success = await comment_crud.delete(UUID(comment_id), current_user.id)
        if success:
            return {"message": "Comment deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete comment"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting comment: {str(e)}"
        )
