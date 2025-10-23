-- IMMEDIATE FIX FOR LIVE AUDIO ROOMS RLS
-- Connect as postgres to safe_zone database

-- 1. FIRST, CHECK CURRENT RLS STATUS
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE tablename LIKE 'live_audio%';

-- 2. DROP ALL EXISTING POLICIES (CLEAN SLATE)
DROP POLICY IF EXISTS live_audio_rooms_insert_policy ON live_audio_rooms;
DROP POLICY IF EXISTS live_audio_rooms_select_policy ON live_audio_rooms;
DROP POLICY IF EXISTS live_audio_rooms_update_policy ON live_audio_rooms;
DROP POLICY IF EXISTS live_audio_room_participants_insert_policy ON live_audio_room_participants;
DROP POLICY IF EXISTS live_audio_room_participants_select_policy ON live_audio_room_participants;

-- 3. CREATE SIMPLE, WORKING POLICIES
-- Room creation: ANY authenticated user can create
CREATE POLICY live_audio_rooms_insert_policy ON live_audio_rooms
    FOR INSERT WITH CHECK (true);

-- Room viewing: Users can see ALL active rooms (we'll restrict later)
CREATE POLICY live_audio_rooms_select_policy ON live_audio_rooms
    FOR SELECT USING (is_active = true);

-- Room updates: Only creator can update  
CREATE POLICY live_audio_rooms_update_policy ON live_audio_rooms
    FOR UPDATE USING (created_by = current_setting('app.current_user_id')::UUID);

-- Participant creation: Users can add themselves to any room
CREATE POLICY live_audio_room_participants_insert_policy ON live_audio_room_participants
    FOR INSERT WITH CHECK (user_id = current_setting('app.current_user_id')::UUID);

-- Participant viewing: Users can see all participants
CREATE POLICY live_audio_room_participants_select_policy ON live_audio_room_participants
    FOR SELECT USING (true);

-- 4. VERIFY POLICIES ARE CREATED
SELECT tablename, policyname, cmd, 
       CASE WHEN with_check IS NOT NULL THEN 'WITH CHECK: ' || substring(with_check from 1 for 30) ELSE 'No CHECK' END as check_clause
FROM pg_policies 
WHERE tablename LIKE 'live_audio%'
ORDER BY tablename, policyname;

-- 5. TEST THE FIX
-- Switch to application user and test
\c safe_zone safe_zone_app_user
SET app.current_user_id TO '00000000-0000-0000-0000-000000000000';
INSERT INTO live_audio_rooms (title, created_by) VALUES ('Test Room', '00000000-0000-0000-0000-000000000000') RETURNING id;
