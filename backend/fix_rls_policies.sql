-- Fix RLS policies for the recreated table
-- The current policies are too restrictive

-- Drop existing policies
DROP POLICY IF EXISTS live_audio_room_participants_select_policy ON live_audio_room_participants;
DROP POLICY IF EXISTS live_audio_room_participants_insert_policy ON live_audio_room_participants;
DROP POLICY IF EXISTS live_audio_room_participants_update_policy ON live_audio_room_participants;

-- Recreate policies following the working pattern from fix_live_audio_rls_final.sql
-- Users can see their own participation
CREATE POLICY live_audio_room_participants_select_policy ON live_audio_room_participants
    FOR SELECT USING (user_id = current_setting('app.current_user_id')::UUID);

-- Users can join rooms they have access to
CREATE POLICY live_audio_room_participants_insert_policy ON live_audio_room_participants
    FOR INSERT WITH CHECK (
        user_id = current_setting('app.current_user_id')::UUID
        AND EXISTS (
            SELECT 1 FROM live_audio_rooms r
            WHERE r.id = live_audio_room_participants.room_id
            AND r.is_active = true
        )
    );

-- Users can update their own participation
CREATE POLICY live_audio_room_participants_update_policy ON live_audio_room_participants
    FOR UPDATE USING (user_id = current_setting('app.current_user_id')::UUID);

-- Verify policies
SELECT policyname, cmd, qual, with_check 
FROM pg_policies 
WHERE tablename = 'live_audio_room_participants';
