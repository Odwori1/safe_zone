"""
Secure Messaging Endpoints for Phase 3, Item 4
Following EXACT same patterns as other endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from uuid import UUID
import logging

from app.schemas.messages import (
    ConversationCreate, Conversation, MessageCreate, Message,
    ConversationParticipant, ConversationWithDetails
)
from app.crud.messages import messages_crud
from app.core.security import get_current_user
from app.schemas.user import User

router = APIRouter()
logger = logging.getLogger(__name__)

# REST API Endpoints - FOLLOWING EXACT SAME PATTERNS AS OTHER ENDPOINTS

@router.post("/conversations", response_model=Conversation)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new conversation
    SECURITY: RLS ensures user can only create their own conversations
    """
    try:
        conversation = await messages_crud.create_conversation(
            current_user.id,
            conversation_data.is_group,
            conversation_data.title,
            conversation_data.participant_ids
        )
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create conversation"
            )
        return conversation
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating conversation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation"
        )

@router.get("/conversations", response_model=List[ConversationWithDetails])
async def get_user_conversations(
    current_user: User = Depends(get_current_user),
    limit: int = 20,
    offset: int = 0
):
    """
    Get user's conversations
    SECURITY: RLS ensures user can only access their own conversations
    """
    try:
        conversations = await messages_crud.get_user_conversations(
            current_user.id, limit, offset
        )
        return conversations
    except Exception as e:
        logger.error(f"Error fetching conversations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch conversations"
        )

@router.post("/conversations/{conversation_id}/messages", response_model=Message)
async def create_message(
    conversation_id: UUID,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new message in conversation
    SECURITY: RLS ensures user can only send to conversations they participate in
    """
    try:
        message = await messages_crud.create_message(
            conversation_id,
            current_user.id,
            message_data.content,
            message_data.content_type,
            message_data.file_metadata_id
        )
        if not message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot send message to this conversation"
            )
        return message
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create message"
        )

@router.get("/conversations/{conversation_id}/messages", response_model=List[Message])
async def get_conversation_messages(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0
):
    """
    Get messages from a conversation
    SECURITY: RLS ensures user can only access conversations they participate in
    """
    try:
        messages = await messages_crud.get_conversation_messages(
            conversation_id, limit, offset
        )
        return messages
    except Exception as e:
        logger.error(f"Error fetching messages: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch messages"
        )

@router.get("/conversations/{conversation_id}/participants", response_model=List[ConversationParticipant])
async def get_conversation_participants(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Get participants in a conversation
    SECURITY: RLS ensures user can only access conversations they participate in
    """
    try:
        participants = await messages_crud.get_conversation_participants(conversation_id)
        return participants
    except Exception as e:
        logger.error(f"Error fetching participants: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch participants"
        )

@router.post("/conversations/{conversation_id}/participants")
async def add_participant(
    conversation_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Add participant to conversation
    SECURITY: RLS ensures only conversation participants can add others
    """
    try:
        success = await messages_crud.add_participant(conversation_id, user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot add participant to conversation"
            )
        return {"message": "Participant added successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding participant: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add participant"
        )

@router.delete("/messages/{message_id}")
async def delete_message(
    message_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Soft delete a message
    SECURITY: RLS ensures user can only delete their own messages
    """
    try:
        success = await messages_crud.soft_delete_message(message_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found or access denied"
            )
        return {"message": "Message deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete message"
        )
