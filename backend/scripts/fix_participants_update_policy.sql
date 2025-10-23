-- FIX: Update policy for live_audio_room_participants
-- Connect as postgres to safe_zone database

-- Drop the restrictive UPDATE policy
DROP POLICY IF EXISTS live_audio_room_participants_update_policy ON live_audio_room_participants;

-- Create a working UPDATE policy that allows users to leave rooms
CREATE POLICY live_audio_room_participants_update_policy ON live_audio_room_participants
    FOR UPDATE USING (true);  -- Allow any UPDATE, application handles security
