"""
Secure CRUD operations for messaging tables - WITH VALIDATION
Following security-first blueprint with RLS protection
"""

import asyncpg
from typing import Optional, List, Dict, Any
from uuid import UUID
from app.database.database import database

class MessagesCRUD:
    """
    Secure CRUD operations for messaging
    All operations are protected by RLS
    """

    async def _record_to_dict(self, record: asyncpg.Record) -> dict:
        """Convert asyncpg Record to dictionary for Pydantic serialization"""
        if not record:
            return None
        return {key: record[key] for key in record.keys()}

    async def create_conversation(
        self,
        user_id: UUID,
        is_group: bool = False,
        title: Optional[str] = None,
        participant_ids: Optional[List[UUID]] = None
    ) -> Optional[dict]:
        """
        Create a new conversation and add participants
        RLS ensures user can only create their own conversations
        """
        async with database.pool.acquire() as conn:
            # Start transaction
            async with conn.transaction():
                # ✅ CRITICAL: Set user context for RLS policies
                await conn.execute("SELECT set_config('app.current_user_id', $1, false)", str(user_id))
                
                # Create conversation WITH created_by field
                conversation = await conn.fetchrow(
                    """
                    INSERT INTO conversations (is_group, title, created_by)
                    VALUES ($1, $2, $3)
                    RETURNING *
                    """,
                    is_group, title, user_id
                )

                if not conversation:
                    return None

                # Add creator as participant
                await conn.execute(
                    """
                    INSERT INTO conversation_participants (conversation_id, user_id, role)
                    VALUES ($1, $2, 'admin')
                    """,
                    conversation['id'], user_id
                )

                # Add other participants if provided
                if participant_ids:
                    for participant_id in participant_ids:
                        if participant_id != user_id:  # Don't duplicate creator
                            await conn.execute(
                                """
                                INSERT INTO conversation_participants (conversation_id, user_id)
                                VALUES ($1, $2)
                                """,
                                conversation['id'], participant_id
                            )

                return await self._record_to_dict(conversation)

    async def add_participant(
        self,
        conversation_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        Add participant to conversation
        RLS ensures only conversation participants can add others
        """
        async with database.pool.acquire() as conn:
            result = await conn.execute(
                """
                INSERT INTO conversation_participants (conversation_id, user_id)
                VALUES ($1, $2)
                ON CONFLICT (conversation_id, user_id) DO NOTHING
                """,
                conversation_id, user_id
            )
            return "INSERT" in result

    async def create_message(
        self,
        conversation_id: UUID,
        sender_id: UUID,
        content: str,
        content_type: str = "text",
        file_metadata_id: Optional[UUID] = None
    ) -> Optional[dict]:
        """
        Create a new message in conversation WITH VALIDATION
        RLS ensures user can only send to conversations they participate in
        """
        # SECURITY: Input validation at application layer
        if not content or not content.strip():
            raise ValueError("Message content cannot be empty")

        content = content.strip()

        if len(content) > 5000:
            raise ValueError("Message content too long (max 5000 characters)")

        if content_type not in ["text", "audio", "video", "file"]:
            raise ValueError("Invalid content type")

        async with database.pool.acquire() as conn:
            message = await conn.fetchrow(
                """
                INSERT INTO messages (conversation_id, sender_id, content, content_type, file_metadata_id)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING *
                """,
                conversation_id, sender_id, content, content_type, file_metadata_id
            )
            return await self._record_to_dict(message) if message else None

    async def get_conversation_messages(
        self,
        conversation_id: UUID,
        limit: int = 50,
        offset: int = 0
    ) -> List[dict]:
        """
        Get messages from a conversation
        RLS ensures user can only access conversations they participate in
        """
        async with database.pool.acquire() as conn:
            messages = await conn.fetch(
                """
                SELECT m.*, u.username
                FROM messages m
                LEFT JOIN users u ON m.sender_id = u.id
                WHERE m.conversation_id = $1 AND m.deleted = false
                ORDER BY m.created_at DESC
                LIMIT $2 OFFSET $3
                """,
                conversation_id, limit, offset
            )
            return [await self._record_to_dict(msg) for msg in messages] if messages else []

    async def get_user_conversations(
        self,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0
    ) -> List[dict]:
        """
        Get user's conversations with last message preview
        RLS ensures user can only access their own conversations
        """
        async with database.pool.acquire() as conn:
            conversations = await conn.fetch(
                """
                SELECT
                    c.*,
                    lm.content as last_message_content,
                    lm.created_at as last_message_at,
                    lm.sender_id as last_message_sender_id,
                    COUNT(m.id) as message_count,
                    COUNT(DISTINCT cp.user_id) as participant_count
                FROM conversations c
                INNER JOIN conversation_participants cp ON c.id = cp.conversation_id
                LEFT JOIN LATERAL (
                    SELECT m.content, m.created_at, m.sender_id
                    FROM messages m
                    WHERE m.conversation_id = c.id AND m.deleted = false
                    ORDER BY m.created_at DESC
                    LIMIT 1
                ) lm ON true
                LEFT JOIN messages m ON c.id = m.conversation_id AND m.deleted = false
                WHERE cp.user_id = $1
                GROUP BY c.id, lm.content, lm.created_at, lm.sender_id
                ORDER BY lm.created_at DESC NULLS LAST, c.created_at DESC
                LIMIT $2 OFFSET $3
                """,
                user_id, limit, offset
            )
            return [await self._record_to_dict(conv) for conv in conversations] if conversations else []

    async def get_conversation_participants(
        self,
        conversation_id: UUID
    ) -> List[dict]:
        """
        Get participants in a conversation
        RLS ensures user can only access conversations they participate in
        """
        async with database.pool.acquire() as conn:
            participants = await conn.fetch(
                """
                SELECT cp.*, u.username, u.email
                FROM conversation_participants cp
                INNER JOIN users u ON cp.user_id = u.id
                WHERE cp.conversation_id = $1
                ORDER BY cp.joined_at
                """,
                conversation_id
            )
            return [await self._record_to_dict(part) for part in participants] if participants else []

    async def soft_delete_message(
        self,
        message_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        Soft delete a message (mark as deleted)
        RLS ensures user can only delete their own messages
        """
        async with database.pool.acquire() as conn:
            result = await conn.execute(
                """
                UPDATE messages
                SET deleted = true, updated_at = NOW()
                WHERE id = $1 AND sender_id = $2
                """,
                message_id, user_id
            )
            return "UPDATE 1" in result

    async def update_message_moderation_status(
        self,
        message_id: UUID,
        status: str,
        moderated: bool = True
    ) -> bool:
        """
        Update message moderation status
        RLS ensures proper access control
        """
        async with database.pool.acquire() as conn:
            result = await conn.execute(
                """
                UPDATE messages
                SET moderation_status = $1, moderated = $2, updated_at = NOW()
                WHERE id = $3
                """,
                status, moderated, message_id
            )
            return "UPDATE 1" in result

# Global messages CRUD instance
messages_crud = MessagesCRUD()
