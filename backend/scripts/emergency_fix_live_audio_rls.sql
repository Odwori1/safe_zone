-- EMERGENCY FIX: Reset Live Audio Rooms RLS Policies
-- Connect as postgres to safe_zone database

-- 1. DISABLE RLS TEMPORARILY
ALTER TABLE live_audio_rooms DISABLE ROW LEVEL SECURITY;
ALTER TABLE live_audio_room_participants DISABLE ROW LEVEL SECURITY;
ALTER TABLE live_audio_room_moderations DISABLE ROW LEVEL SECURITY;

-- 2. DROP ALL PROBLEMATIC POLICIES
DROP POLICY IF EXISTS live_audio_rooms_select_policy ON live_audio_rooms;
DROP POLICY IF EXISTS live_audio_rooms_insert_policy ON live_audio_rooms;
DROP POLICY IF EXISTS live_audio_rooms_update_policy ON live_audio_rooms;

DROP POLICY IF EXISTS live_audio_room_participants_select_policy ON live_audio_room_participants;
DROP POLICY IF EXISTS live_audio_room_participants_insert_policy ON live_audio_room_participants;
DROP POLICY IF EXISTS live_audio_room_participants_update_policy ON live_audio_room_participants;

DROP POLICY IF EXISTS live_audio_room_moderations_select_policy ON live_audio_room_moderations;
DROP POLICY IF EXISTS live_audio_room_moderations_insert_policy ON live_audio_room_moderations;

-- 3. RE-ENABLE RLS
ALTER TABLE live_audio_rooms ENABLE ROW LEVEL SECURITY;
ALTER TABLE live_audio_room_participants ENABLE ROW LEVEL SECURITY;
ALTER TABLE live_audio_room_moderations ENABLE ROW LEVEL SECURITY;

-- 4. CREATE SIMPLE, WORKING POLICIES
-- Rooms: Anyone can create and see active rooms
CREATE POLICY live_audio_rooms_insert_policy ON live_audio_rooms
    FOR INSERT WITH CHECK (true);

CREATE POLICY live_audio_rooms_select_policy ON live_audio_rooms
    FOR SELECT USING (is_active = true);

CREATE POLICY live_audio_rooms_update_policy ON live_audio_rooms
    FOR UPDATE USING (created_by = current_setting('app.current_user_id')::UUID);

-- Participants: Anyone can join and see participants
CREATE POLICY live_audio_room_participants_insert_policy ON live_audio_room_participants
    FOR INSERT WITH CHECK (true);

CREATE POLICY live_audio_room_participants_select_policy ON live_audio_room_participants
    FOR SELECT USING (true);

CREATE POLICY live_audio_room_participants_update_policy ON live_audio_room_participants
    FOR UPDATE USING (user_id = current_setting('app.current_user_id')::UUID);

-- Moderation: Basic policies
CREATE POLICY live_audio_room_moderations_insert_policy ON live_audio_room_moderations
    FOR INSERT WITH CHECK (true);

CREATE POLICY live_audio_room_moderations_select_policy ON live_audio_room_moderations
    FOR SELECT USING (true);

-- 5. VERIFY FIX
SELECT tablename, policyname, cmd 
FROM pg_policies 
WHERE tablename LIKE 'live_audio%'
ORDER BY tablename, policyname;
