-- FINAL FIX: Live Audio Rooms RLS Policies
-- Following EXACT same patterns as working messaging system

-- 1. Drop all existing policies
DROP POLICY IF EXISTS live_audio_rooms_select_policy ON live_audio_rooms;
DROP POLICY IF EXISTS live_audio_rooms_insert_policy ON live_audio_rooms;
DROP POLICY IF EXISTS live_audio_rooms_update_policy ON live_audio_rooms;

DROP POLICY IF EXISTS live_audio_room_participants_select_policy ON live_audio_room_participants;
DROP POLICY IF EXISTS live_audio_room_participants_insert_policy ON live_audio_room_participants;
DROP POLICY IF EXISTS live_audio_room_participants_update_policy ON live_audio_room_participants;

-- 2. Add missing 'visibility' column to match our test patterns
ALTER TABLE live_audio_rooms ADD COLUMN IF NOT EXISTS visibility VARCHAR(20) DEFAULT 'public' CHECK (visibility IN ('public', 'private'));

-- 3. EXACT SAME PATTERNS AS MESSAGING SYSTEM
-- Rooms: Anyone can create (like conversations)
CREATE POLICY live_audio_rooms_insert_policy ON live_audio_rooms
    FOR INSERT WITH CHECK (true);

-- Rooms: Users can see rooms they participate in (like conversations)
CREATE POLICY live_audio_rooms_select_policy ON live_audio_rooms
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM live_audio_room_participants p
            WHERE p.room_id = live_audio_rooms.id
            AND p.user_id = current_setting('app.current_user_id')::UUID
            AND p.left_at IS NULL
        )
    );

-- Rooms: Only creator can update
CREATE POLICY live_audio_rooms_update_policy ON live_audio_rooms
    FOR UPDATE USING (created_by = current_setting('app.current_user_id')::UUID);

-- Participants: Users can see their own participation (like conversation_participants)
CREATE POLICY live_audio_room_participants_select_policy ON live_audio_room_participants
    FOR SELECT USING (user_id = current_setting('app.current_user_id')::UUID);

-- Participants: Users can join rooms they have access to (like conversation_participants)
CREATE POLICY live_audio_room_participants_insert_policy ON live_audio_room_participants
    FOR INSERT WITH CHECK (
        user_id = current_setting('app.current_user_id')::UUID
        AND EXISTS (
            SELECT 1 FROM live_audio_rooms r
            WHERE r.id = live_audio_room_participants.room_id
            AND r.is_active = true
            AND (
                -- Can join public rooms
                r.visibility = 'public'
                -- Or is the room creator (auto-join)
                OR r.created_by = current_setting('app.current_user_id')::UUID
            )
        )
    );

-- Participants: Users can update their own participation
CREATE POLICY live_audio_room_participants_update_policy ON live_audio_room_participants
    FOR UPDATE USING (user_id = current_setting('app.current_user_id')::UUID);
