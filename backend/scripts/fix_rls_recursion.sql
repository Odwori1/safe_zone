-- FIX RLS INFINITE RECURSION
-- Connect as postgres to safe_zone database first

-- Drop the problematic policies
DROP POLICY IF EXISTS conversation_participants_isolation_policy ON conversation_participants;
DROP POLICY IF EXISTS conversation_participants_select_policy ON conversation_participants;

-- Create fixed policies without recursion
CREATE POLICY conversation_participants_select_policy ON conversation_participants
    FOR SELECT USING (
        user_id = current_setting('app.current_user_id')::UUID
    );

CREATE POLICY conversation_participants_insert_policy ON conversation_participants
    FOR INSERT WITH CHECK (
        user_id = current_setting('app.current_user_id')::UUID
    );

-- Verify the fix
SELECT tablename, policyname, cmd, qual 
FROM pg_policies 
WHERE tablename = 'conversation_participants';
