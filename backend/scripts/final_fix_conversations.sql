-- Final fix for conversations RLS policies
-- Run this as postgres user

\c safe_zone;

-- First, let's check if created_by column was added correctly
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'conversations' AND column_name = 'created_by';

-- Now let's completely reset and fix the RLS policies
-- Drop ALL existing policies on conversations
DROP POLICY IF EXISTS conversations_select_policy ON conversations;
DROP POLICY IF EXISTS conversations_insert_policy ON conversations;
DROP POLICY IF EXISTS conversations_update_policy ON conversations;
DROP POLICY IF EXISTS conversations_delete_policy ON conversations;

-- Create proper policies with created_by
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

-- UPDATE policy: only creator or admin participants can update
CREATE POLICY conversations_update_policy ON conversations
    FOR UPDATE USING (
        created_by = current_setting('app.current_user_id')::UUID
        OR EXISTS (
            SELECT 1 FROM conversation_participants 
            WHERE conversation_id = conversations.id 
            AND user_id = current_setting('app.current_user_id')::UUID
            AND role IN ('admin', 'moderator')
        )
    );

-- DELETE policy: only creator can delete
CREATE POLICY conversations_delete_policy ON conversations
    FOR DELETE USING (created_by = current_setting('app.current_user_id')::UUID);

\echo 'Final conversations policies applied!'
