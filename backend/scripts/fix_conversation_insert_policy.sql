-- FIX CONVERSATION INSERT POLICY
-- The current policy has WITH CHECK: false which blocks all conversation creation

-- Drop the problematic policy
DROP POLICY IF EXISTS conversations_insert_policy ON conversations;

-- Create a proper insert policy for conversations
-- Users should be able to create conversations (they'll be added as participants separately)
CREATE POLICY conversations_insert_policy ON conversations
    FOR INSERT WITH CHECK (true); -- Allow conversation creation, participant management happens separately

-- Verify the fix
SELECT tablename, policyname, cmd, with_check
FROM pg_policies 
WHERE tablename = 'conversations' AND cmd = 'INSERT';
