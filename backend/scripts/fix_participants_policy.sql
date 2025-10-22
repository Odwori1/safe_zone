-- Fix conversation_participants SELECT policy to be more restrictive
DROP POLICY IF EXISTS conversation_participants_select_policy ON conversation_participants;

-- Users can only see participants in conversations they are actually in
CREATE POLICY conversation_participants_select_policy ON conversation_participants
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM conversation_participants cp
            WHERE cp.conversation_id = conversation_participants.conversation_id
            AND cp.user_id = current_setting('app.current_user_id')::UUID
        )
    );
