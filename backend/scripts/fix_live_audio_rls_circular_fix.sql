-- FIX CIRCULAR RLS DEPENDENCY FOR LIVE AUDIO ROOMS
-- Following previous developer's exact diagnosis

-- 1. DROP ALL EXISTING POLICIES
DROP POLICY IF EXISTS live_audio_rooms_select_policy ON live_audio_rooms;
DROP POLICY IF EXISTS live_audio_rooms_insert_policy ON live_audio_rooms;
DROP POLICY IF EXISTS live_audio_rooms_update_policy ON live_audio_rooms;

DROP POLICY IF EXISTS live_audio_room_participants_select_policy ON live_audio_room_participants;
DROP POLICY IF EXISTS live_audio_room_participants_insert_policy ON live_audio_room_participants;
DROP POLICY IF EXISTS live_audio_room_participants_update_policy ON live_audio_room_participants;

-- 2. CREATE NON-CIRCULAR POLICIES - BREAK THE DEPENDENCY

-- ROOM CREATION: ANY authenticated user can create a room (NO participant check)
CREATE POLICY live_audio_rooms_insert_policy ON live_audio_rooms
    FOR INSERT WITH CHECK (true);

-- ROOM VIEWING: Users can see rooms they participate in
CREATE POLICY live_audio_rooms_select_policy ON live_audio_rooms
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM live_audio_room_participants p
            WHERE p.room_id = live_audio_rooms.id
            AND p.user_id = current_setting('app.current_user_id')::UUID
            AND p.left_at IS NULL
        )
    );

-- ROOM UPDATES: Only room creator can update
CREATE POLICY live_audio_rooms_update_policy ON live_audio_rooms
    FOR UPDATE USING (created_by = current_setting('app.current_user_id')::UUID);

-- PARTICIPANT VIEWING: Users can see their own participation
CREATE POLICY live_audio_room_participants_select_policy ON live_audio_room_participants
    FOR SELECT USING (user_id = current_setting('app.current_user_id')::UUID);

-- PARTICIPANT JOINING: Users can add themselves to ANY room initially
-- Application logic will handle proper access control
CREATE POLICY live_audio_room_participants_insert_policy ON live_audio_room_participants
    FOR INSERT WITH CHECK (user_id = current_setting('app.current_user_id')::UUID);

-- PARTICIPANT UPDATES: Users can update their own participation
CREATE POLICY live_audio_room_participants_update_policy ON live_audio_room_participants
    FOR UPDATE USING (user_id = current_setting('app.current_user_id')::UUID);
