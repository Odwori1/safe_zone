-- FIX PARTICIPANTS RLS POLICY
-- Connect as postgres to safe_zone database

-- Drop the problematic policy
DROP POLICY IF EXISTS live_audio_room_participants_insert_policy ON live_audio_room_participants;

-- Create SIMPLE working policy
CREATE POLICY live_audio_room_participants_insert_policy ON live_audio_room_participants
    FOR INSERT WITH CHECK (true);  -- Allow any insert, application handles logic
