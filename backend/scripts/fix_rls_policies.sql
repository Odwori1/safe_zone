-- CRITICAL SECURITY FIX: Add WITH CHECK conditions to INSERT policies
-- This prevents unauthorized data insertion

-- Fix conversation_participants INSERT policy
DROP POLICY IF EXISTS conversation_participants_insert_policy ON conversation_participants;
CREATE POLICY conversation_participants_insert_policy ON conversation_participants
    FOR INSERT WITH CHECK (
        user_id = current_setting('app.current_user_id')::UUID
        AND EXISTS (
            SELECT 1 FROM conversation_participants cp
            WHERE cp.conversation_id = conversation_participants.conversation_id
            AND cp.user_id = current_setting('app.current_user_id')::UUID
        )
    );

-- Fix messages INSERT policy  
DROP POLICY IF EXISTS messages_insert_policy ON messages;
CREATE POLICY messages_insert_policy ON messages
    FOR INSERT WITH CHECK (
        sender_id = current_setting('app.current_user_id')::UUID
        AND EXISTS (
            SELECT 1 FROM conversation_participants cp
            WHERE cp.conversation_id = messages.conversation_id
            AND cp.user_id = current_setting('app.current_user_id')::UUID
        )
        AND length(trim(content)) > 0
        AND length(content) <= 5000
    );

-- Add INSERT policy for conversations (prevent direct inserts)
DROP POLICY IF EXISTS conversations_insert_policy ON conversations;
CREATE POLICY conversations_insert_policy ON conversations
    FOR INSERT WITH CHECK (false); -- No direct inserts, must use CRUD function

-- Verify the fixes
SELECT tablename, policyname, cmd, has_with_check 
FROM pg_policies 
WHERE tablename IN ('conversations', 'conversation_participants', 'messages')
ORDER BY tablename, policyname;
