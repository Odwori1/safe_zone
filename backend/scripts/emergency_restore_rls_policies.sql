-- EMERGENCY RESTORATION: Fix broken RLS policies
-- Connect as postgres to safe_zone database

-- Drop the broken INSERT policy
DROP POLICY IF EXISTS live_audio_room_participants_insert_policy ON live_audio_room_participants;

-- Recreate the INSERT policy with proper conditions
-- This follows the original working pattern from create_live_audio_rooms.sql
CREATE POLICY live_audio_room_participants_insert_policy ON live_audio_room_participants
    FOR INSERT WITH CHECK (user_id = current_setting('app.current_user_id')::UUID);

-- Verify the policy was created correctly
SELECT schemaname, tablename, policyname, cmd, qual 
FROM pg_policies 
WHERE tablename = 'live_audio_room_participants' AND cmd = 'INSERT';
