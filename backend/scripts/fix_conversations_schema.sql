-- Fix conversations schema by adding created_by column and updating RLS policies
-- Run this as postgres user

\c safe_zone;

-- Add created_by column to conversations table
ALTER TABLE conversations ADD COLUMN created_by UUID REFERENCES users(id);

-- Update existing conversations to have a default created_by (if any exist)
-- This is just for data consistency, we can use a default user if needed
UPDATE conversations SET created_by = (
    SELECT user_id FROM conversation_participants 
    WHERE conversation_id = conversations.id 
    ORDER BY joined_at 
    LIMIT 1
) WHERE created_by IS NULL;

-- Now disable RLS and drop all existing policies
ALTER TABLE conversations NO ROW LEVEL SECURITY;

DROP POLICY IF EXISTS conversations_select_policy ON conversations;
DROP POLICY IF EXISTS conversations_insert_policy ON conversations;
DROP POLICY IF EXISTS conversations_update_policy ON conversations;
DROP POLICY IF EXISTS conversations_delete_policy ON conversations;

-- Re-enable RLS with proper policies
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;

-- INSERT policy: users can only create conversations where they are the creator
CREATE POLICY conversations_insert_policy ON conversations
    FOR INSERT WITH CHECK (created_by = current_setting('app.current_user_id')::UUID);

-- SELECT policy: users can see conversations they created OR participate in
CREATE POLICY conversations_select_policy ON conversations
    FOR SELECT USING (
        created_by = current_setting('app.current_user_id')::UUID
        OR EXISTS (
            SELECT 1 FROM conversation_participants 
            WHERE conversation_id = conversations.id 
            AND user_id = current_setting('app.current_user_id')::UUID
        )
    );

-- UPDATE policy: only creator or participants can update
CREATE POLICY conversations_update_policy ON conversations
    FOR UPDATE USING (
        created_by = current_setting('app.current_user_id')::UUID
        OR EXISTS (
            SELECT 1 FROM conversation_participants 
            WHERE conversation_id = conversations.id 
            AND user_id = current_setting('app.current_user_id')::UUID
        )
    );

-- DELETE policy: only creator can delete
CREATE POLICY conversations_delete_policy ON conversations
    FOR DELETE USING (created_by = current_setting('app.current_user_id')::UUID);

\echo 'Fixed conversations schema and policies!'
