-- Rollback RLS policies to original working state
DROP POLICY IF EXISTS live_audio_room_participants_insert_policy ON live_audio_room_participants;
DROP POLICY IF EXISTS live_audio_room_participants_select_policy ON live_audio_room_participants;
DROP POLICY IF EXISTS live_audio_room_participants_update_policy ON live_audio_room_participants;

-- Restore the original policies from create_live_audio_rooms.sql
-- Participants: Users can see participants in rooms they have access to
CREATE POLICY live_audio_room_participants_select_policy ON live_audio_room_participants
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM live_audio_rooms r
            WHERE r.id = live_audio_room_participants.room_id
            AND r.is_active = true
            AND (
                r.is_public = true
                OR r.created_by = current_setting('app.current_user_id')::UUID
                OR EXISTS (
                    SELECT 1 FROM live_audio_room_participants p2
                    WHERE p2.room_id = r.id
                    AND p2.user_id = current_setting('app.current_user_id')::UUID
                    AND p2.left_at IS NULL
                )
            )
        )
    );

-- Users can only insert themselves as participants
CREATE POLICY live_audio_room_participants_insert_policy ON live_audio_room_participants
    FOR INSERT WITH CHECK (user_id = current_setting('app.current_user_id')::UUID);

-- Users can only update their own participation records  
CREATE POLICY live_audio_room_participants_update_policy ON live_audio_room_participants
    FOR UPDATE USING (user_id = current_setting('app.current_user_id')::UUID);

-- Verify the policies are restored
SELECT policyname, cmd, qual IS NOT NULL as has_qual, with_check IS NOT NULL as has_with_check
FROM pg_policies 
WHERE tablename = 'live_audio_room_participants'
ORDER BY policyname;
