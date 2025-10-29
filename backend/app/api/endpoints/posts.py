from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from uuid import UUID
from app.schemas.post import PostCreate, PostResponse, PostUpdate
from app.schemas.user import User
from app.core.security import get_current_user
from app.crud.post import post_crud

router = APIRouter()

@router.post("/", response_model=PostResponse)
async def create_new_post(
    post: PostCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new post
    """
    try:
        result = await post_crud.create(current_user.id, post)
        if result:
            post_data = dict(result)
            if post_data.get('is_anonymous'):
                post_data['username'] = None
                post_data['user_avatar'] = None
            return PostResponse(**post_data)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create post"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating post: {str(e)}"
        )

@router.get("/", response_model=List[PostResponse])
async def read_posts(
    skip: int = 0,
    limit: int = 100,
    mood: Optional[str] = None,
    visibility: Optional[str] = None,
    user_id: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve posts with optional filters and search
    """
    try:
        # Convert user_id string to UUID if provided
        user_id_uuid = None
        if user_id:
            try:
                user_id_uuid = UUID(user_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid user ID format"
                )

        posts = await post_crud.get_feed(
            current_user.id, 
            limit=limit, 
            offset=skip,
            mood=mood,
            visibility=visibility,
            user_id_filter=user_id_uuid,
            search=search
        )
        
        response_posts = []
        for post in posts:
            post_data = dict(post)
            if post_data.get('is_anonymous'):
                post_data['username'] = None
                post_data['user_avatar'] = None
            response_posts.append(PostResponse(**post_data))
        return response_posts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving posts: {str(e)}"
        )

@router.get("/{post_id}", response_model=PostResponse)
async def read_post(
    post_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific post by ID
    """
    try:
        post = await post_crud.get(UUID(post_id))
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )

        post_data = dict(post)
        if post_data.get('is_anonymous'):
            post_data['username'] = None
            post_data['user_avatar'] = None

        return PostResponse(**post_data)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid post ID format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving post: {str(e)}"
        )

@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: str,
    post_update: PostUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update a post - only by owner
    """
    try:
        existing_post = await post_crud.get(UUID(post_id))
        if not existing_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )

        if existing_post['user_id'] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this post"
            )

        updated_post = await post_crud.update(UUID(post_id), current_user.id, post_update)
        if not updated_post:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update post"
            )

        post_data = dict(updated_post)
        if post_data.get('is_anonymous'):
            post_data['username'] = None
            post_data['user_avatar'] = None

        return PostResponse(**post_data)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid post ID format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating post: {str(e)}"
        )

@router.delete("/{post_id}")
async def delete_post(
    post_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a post - only by owner
    """
    try:
        existing_post = await post_crud.get(UUID(post_id))
        if not existing_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )

        if existing_post['user_id'] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this post"
            )

        success = await post_crud.delete(UUID(post_id), current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete post"
            )

        return {"message": "Post deleted successfully"}
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid post ID format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting post: {str(e)}"
        )

@router.post("/{post_id}/like")
async def like_post(
    post_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Like a post
    """
    try:
        # First check if post exists
        existing_post = await post_crud.get(UUID(post_id))
        if not existing_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )

        # Check if user already liked this post
        already_liked = await post_crud.has_user_liked(UUID(post_id), current_user.id)
        if already_liked:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already liked this post"
            )

        # Add like
        success = await post_crud.add_like(UUID(post_id), current_user.id)
        if success:
            return {"message": "Post liked successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to like post"
            )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid post ID format"
        )
    except Exception as e:
        # Include the full error details for debugging
        error_detail = f"Error liking post: {str(e)}"
        print(f"❌ LIKE ERROR: {error_detail}")  # Log to backend console
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )

@router.post("/{post_id}/unlike")
async def unlike_post(
    post_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Unlike a post
    """
    try:
        # First check if post exists
        existing_post = await post_crud.get(UUID(post_id))
        if not existing_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )

        # Check if user has liked this post
        already_liked = await post_crud.has_user_liked(UUID(post_id), current_user.id)
        if not already_liked:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have not liked this post"
            )

        # Remove like
        success = await post_crud.remove_like(UUID(post_id), current_user.id)
        if success:
            return {"message": "Post unliked successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to unlike post"
            )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid post ID format"
        )
    except Exception as e:
        # Include the full error details for debugging
        error_detail = f"Error unliking post: {str(e)}"
        print(f"❌ UNLIKE ERROR: {error_detail}")  # Log to backend console
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )
