-- Fix Live Audio Rooms RLS to EXACTLY match working messaging patterns

-- Drop all existing policies
DROP POLICY IF EXISTS live_audio_rooms_select_policy ON live_audio_rooms;
DROP POLICY IF EXISTS live_audio_rooms_insert_policy ON live_audio_rooms;
DROP POLICY IF EXISTS live_audio_rooms_update_policy ON live_audio_rooms;

DROP POLICY IF EXISTS live_audio_room_participants_select_policy ON live_audio_room_participants;
DROP POLICY IF EXISTS live_audio_room_participants_insert_policy ON live_audio_room_participants;
DROP POLICY IF EXISTS live_audio_room_participants_update_policy ON live_audio_room_participants;

DROP POLICY IF EXISTS live_audio_room_moderations_select_policy ON live_audio_room_moderations;
DROP POLICY IF EXISTS live_audio_room_moderations_insert_policy ON live_audio_room_moderations;

-- EXACT SAME PATTERN AS CONVERSATIONS TABLE
-- Users can see rooms they participate in (like conversations)
CREATE POLICY live_audio_rooms_select_policy ON live_audio_rooms
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM live_audio_room_participants p
            WHERE p.room_id = live_audio_rooms.id
            AND p.user_id = current_setting('app.current_user_id')::UUID
            AND p.left_at IS NULL
        )
    );

-- Users can insert any room (like conversations_insert_policy WITH CHECK true)
CREATE POLICY live_audio_rooms_insert_policy ON live_audio_rooms
    FOR INSERT WITH CHECK (true);

-- Users can update rooms they created
CREATE POLICY live_audio_rooms_update_policy ON live_audio_rooms
    FOR UPDATE USING (created_by = current_setting('app.current_user_id')::UUID);

-- EXACT SAME PATTERN AS CONVERSATION_PARTICIPANTS TABLE
-- Users can see their own participation records
CREATE POLICY live_audio_room_participants_select_policy ON live_audio_room_participants
    FOR SELECT USING (user_id = current_setting('app.current_user_id')::UUID);

-- Users can insert themselves as participants with validation
CREATE POLICY live_audio_room_participants_insert_policy ON live_audio_room_participants
    FOR INSERT WITH CHECK (
        user_id = current_setting('app.current_user_id')::UUID
        AND EXISTS (
            SELECT 1 FROM live_audio_room_participants cp
            WHERE cp.room_id = live_audio_room_participants.room_id
            AND cp.user_id = current_setting('app.current_user_id')::UUID
        )
    );

-- Users can update their own participation records
CREATE POLICY live_audio_room_participants_update_policy ON live_audio_room_participants
    FOR UPDATE USING (user_id = current_setting('app.current_user_id')::UUID);

-- SIMPLIFIED moderation policies (like messages pattern)
CREATE POLICY live_audio_room_moderations_select_policy ON live_audio_room_moderations
    FOR SELECT USING (
        moderator_id = current_setting('app.current_user_id')::UUID
        OR target_user_id = current_setting('app.current_user_id')::UUID
    );

CREATE POLICY live_audio_room_moderations_insert_policy ON live_audio_room_moderations
    FOR INSERT WITH CHECK (moderator_id = current_setting('app.current_user_id')::UUID);
