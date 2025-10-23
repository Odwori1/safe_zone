-- MINIMAL RLS POLICIES - BREAK ALL CIRCULAR DEPENDENCIES
-- Connect as postgres to safe_zone database

-- 1. COMPLETELY DISABLE RLS TEMPORARILY to test
ALTER TABLE live_audio_rooms DISABLE ROW LEVEL SECURITY;
ALTER TABLE live_audio_room_participants DISABLE ROW LEVEL SECURITY;

-- 2. DROP ALL POLICIES
DROP POLICY IF EXISTS live_audio_rooms_select_policy ON live_audio_rooms;
DROP POLICY IF EXISTS live_audio_rooms_insert_policy ON live_audio_rooms;
DROP POLICY IF EXISTS live_audio_rooms_update_policy ON live_audio_rooms;

DROP POLICY IF EXISTS live_audio_room_participants_select_policy ON live_audio_room_participants;
DROP POLICY IF EXISTS live_audio_room_participants_insert_policy ON live_audio_room_participants;
DROP POLICY IF EXISTS live_audio_room_participants_update_policy ON live_audio_room_participants;

-- 3. RE-ENABLE RLS
ALTER TABLE live_audio_rooms ENABLE ROW LEVEL SECURITY;
ALTER TABLE live_audio_room_participants ENABLE ROW LEVEL SECURITY;

-- 4. CREATE ABSOLUTELY MINIMAL POLICIES - NO CIRCULARITY

-- Rooms: ANYONE can insert (like conversations)
CREATE POLICY live_audio_rooms_insert_policy ON live_audio_rooms
    FOR INSERT WITH CHECK (true);

-- Rooms: Users can see ALL active rooms initially (we'll filter in application)
CREATE POLICY live_audio_rooms_select_policy ON live_audio_rooms
    FOR SELECT USING (is_active = true);

-- Rooms: Only creator can update
CREATE POLICY live_audio_rooms_update_policy ON live_audio_rooms
    FOR UPDATE USING (created_by = current_setting('app.current_user_id')::UUID);

-- Participants: Users can see their own participation ONLY
CREATE POLICY live_audio_room_participants_select_policy ON live_audio_room_participants
    FOR SELECT USING (user_id = current_setting('app.current_user_id')::UUID);

-- Participants: Users can insert themselves into ANY room
CREATE POLICY live_audio_room_participants_insert_policy ON live_audio_room_participants
    FOR INSERT WITH CHECK (user_id = current_setting('app.current_user_id')::UUID);

-- Participants: Users can update their own participation
CREATE POLICY live_audio_room_participants_update_policy ON live_audio_room_participants
    FOR UPDATE USING (user_id = current_setting('app.current_user_id')::UUID);
