-- COMPLETE RLS POLICY FIX
-- Fixes missing WITH CHECK conditions for INSERT policies

-- 1. Drop existing incomplete policies
DROP POLICY IF EXISTS conversation_participants_insert_policy ON conversation_participants;
DROP POLICY IF EXISTS conversations_insert_policy ON conversations;
DROP POLICY IF EXISTS messages_insert_policy ON messages;

-- 2. Create complete policies with WITH CHECK conditions
-- Conversation participants: User can only add themselves to conversations they can see
CREATE POLICY conversation_participants_insert_policy ON conversation_participants
    FOR INSERT WITH CHECK (
        user_id = current_setting('app.current_user_id')::UUID
        AND EXISTS (
            SELECT 1 FROM conversation_participants cp
            WHERE cp.conversation_id = conversation_participants.conversation_id
            AND cp.user_id = current_setting('app.current_user_id')::UUID
        )
    );

-- Conversations: User must be a participant to insert (for group conversations)
CREATE POLICY conversations_insert_policy ON conversations
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM conversation_participants cp
            WHERE cp.conversation_id = conversations.id
            AND cp.user_id = current_setting('app.current_user_id')::UUID
        )
    );

-- Messages: User must be sender and participant in conversation
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

-- 3. Verify all policies are complete
SELECT 
    tablename, 
    policyname, 
    cmd,
    CASE 
        WHEN qual IS NOT NULL THEN 'USING: ' || substring(qual from 1 for 50) || '...'
        ELSE 'No USING'
    END as using_clause,
    CASE 
        WHEN with_check IS NOT NULL THEN 'WITH CHECK: ' || substring(with_check from 1 for 50) || '...' 
        ELSE 'No WITH CHECK'
    END as check_clause
FROM pg_policies 
WHERE tablename IN ('conversations', 'messages', 'conversation_participants')
ORDER BY tablename, policyname;
