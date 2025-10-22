-- Fix infinite recursion in live audio rooms RLS policies

-- First drop the problematic policies
DROP POLICY IF EXISTS live_audio_room_participants_select_policy ON live_audio_room_participants;
DROP POLICY IF EXISTS live_audio_rooms_select_policy ON live_audio_rooms;

-- Fixed RLS Policies for live_audio_rooms
CREATE POLICY live_audio_rooms_select_policy ON live_audio_rooms
    FOR SELECT USING (
        is_active = true AND (
            is_public = true 
            OR created_by = current_setting('app.current_user_id')::UUID
        )
    );

-- Fixed RLS Policies for live_audio_room_participants
CREATE POLICY live_audio_room_participants_select_policy ON live_audio_room_participants
    FOR SELECT USING (
        user_id = current_setting('app.current_user_id')::UUID
        OR EXISTS (
            SELECT 1 FROM live_audio_rooms r
            WHERE r.id = live_audio_room_participants.room_id
            AND r.is_active = true
            AND r.is_public = true
        )
        OR EXISTS (
            SELECT 1 FROM live_audio_rooms r
            WHERE r.id = live_audio_room_participants.room_id
            AND r.is_active = true
            AND r.created_by = current_setting('app.current_user_id')::UUID
        )
    );
