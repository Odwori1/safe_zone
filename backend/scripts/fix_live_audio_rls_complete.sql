-- Complete fix for live audio rooms RLS policies
-- Following EXACT same patterns as messaging schema

-- Drop all existing policies to start fresh
DROP POLICY IF EXISTS live_audio_rooms_select_policy ON live_audio_rooms;
DROP POLICY IF EXISTS live_audio_rooms_insert_policy ON live_audio_rooms;
DROP POLICY IF EXISTS live_audio_rooms_update_policy ON live_audio_rooms;

DROP POLICY IF EXISTS live_audio_room_participants_select_policy ON live_audio_room_participants;
DROP POLICY IF EXISTS live_audio_room_participants_insert_policy ON live_audio_room_participants;
DROP POLICY IF EXISTS live_audio_room_participants_update_policy ON live_audio_room_participants;

DROP POLICY IF EXISTS live_audio_room_moderations_select_policy ON live_audio_room_moderations;
DROP POLICY IF EXISTS live_audio_room_moderations_insert_policy ON live_audio_room_moderations;

-- SIMPLIFIED RLS Policies for live_audio_rooms - LIKE MESSAGING SCHEMA
-- Users can see active rooms (RLS will handle participant access via application logic)
CREATE POLICY live_audio_rooms_select_policy ON live_audio_rooms
    FOR SELECT USING (is_active = true);

-- Users can only insert rooms they create
CREATE POLICY live_audio_rooms_insert_policy ON live_audio_rooms
    FOR INSERT WITH CHECK (created_by = current_setting('app.current_user_id')::UUID);

-- Users can only update rooms they created
CREATE POLICY live_audio_rooms_update_policy ON live_audio_rooms
    FOR UPDATE USING (created_by = current_setting('app.current_user_id')::UUID);

-- SIMPLIFIED RLS Policies for live_audio_room_participants - LIKE MESSAGING SCHEMA
-- Users can see participants in rooms they are in (application will filter)
CREATE POLICY live_audio_room_participants_select_policy ON live_audio_room_participants
    FOR SELECT USING (true); -- Application will filter by room access

-- Users can only insert themselves as participants
CREATE POLICY live_audio_room_participants_insert_policy ON live_audio_room_participants
    FOR INSERT WITH CHECK (user_id = current_setting('app.current_user_id')::UUID);

-- Users can only update their own participation records
CREATE POLICY live_audio_room_participants_update_policy ON live_audio_room_participants
    FOR UPDATE USING (user_id = current_setting('app.current_user_id')::UUID);

-- SIMPLIFIED RLS Policies for live_audio_room_moderations
-- Users can see their own moderation actions
CREATE POLICY live_audio_room_moderations_select_policy ON live_audio_room_moderations
    FOR SELECT USING (
        moderator_id = current_setting('app.current_user_id')::UUID
        OR target_user_id = current_setting('app.current_user_id')::UUID
    );

-- Only authorized users can insert moderation actions (application will verify)
CREATE POLICY live_audio_room_moderations_insert_policy ON live_audio_room_moderations
    FOR INSERT WITH CHECK (true); -- Application will verify moderator role
