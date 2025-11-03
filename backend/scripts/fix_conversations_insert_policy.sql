-- Fix conversations INSERT policy to allow conversation creation
-- Run this as postgres user

\c safe_zone;

-- Check current policies on conversations
\dp conversations;

-- Drop the current INSERT policy if it exists
DROP POLICY IF EXISTS conversations_insert_policy ON conversations;

-- Create a new INSERT policy that allows conversation creation
-- Since conversations don't have a user_id column, we need a different approach
CREATE POLICY conversations_insert_policy ON conversations
    FOR INSERT WITH CHECK (true);

-- Also verify the SELECT policy is correct
DROP POLICY IF EXISTS conversations_select_policy ON conversations;

-- SELECT policy: users can only see conversations they participate in
CREATE POLICY conversations_select_policy ON conversations
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM conversation_participants 
            WHERE conversation_id = conversations.id 
            AND user_id = current_setting('app.current_user_id')::UUID
        )
    );

-- Add UPDATE and DELETE policies for completeness
CREATE POLICY conversations_update_policy ON conversations
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM conversation_participants 
            WHERE conversation_id = conversations.id 
            AND user_id = current_setting('app.current_user_id')::UUID
            AND role IN ('admin', 'moderator')
        )
    );

CREATE POLICY conversations_delete_policy ON conversations
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM conversation_participants 
            WHERE conversation_id = conversations.id 
            AND user_id = current_setting('app.current_user_id')::UUID
            AND role = 'admin'
        )
    );

\echo 'Fixed conversations policies!'
