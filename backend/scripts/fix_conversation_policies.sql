-- Fix circular dependency in conversation_participants INSERT policy
-- Run this as postgres user

\c safe_zone;

-- Drop the problematic INSERT policy
DROP POLICY IF EXISTS conversation_participants_insert_policy ON conversation_participants;

-- Create a new INSERT policy that allows users to insert themselves as participants
-- This allows the conversation creator to add themselves as the first participant
CREATE POLICY conversation_participants_insert_policy ON conversation_participants
    FOR INSERT WITH CHECK (user_id = current_setting('app.current_user_id')::UUID);

-- Also need to fix the SELECT policy to be consistent
DROP POLICY IF EXISTS conversation_participants_select_policy ON conversation_participants;

-- Create SELECT policy for conversation participants
CREATE POLICY conversation_participants_select_policy ON conversation_participants
    FOR SELECT USING (user_id = current_setting('app.current_user_id')::UUID);

-- Add UPDATE and DELETE policies for completeness
CREATE POLICY conversation_participants_update_policy ON conversation_participants
    FOR UPDATE USING (user_id = current_setting('app.current_user_id')::UUID);

CREATE POLICY conversation_participants_delete_policy ON conversation_participants
    FOR DELETE USING (user_id = current_setting('app.current_user_id')::UUID);

\echo 'Fixed conversation participants policies!'
