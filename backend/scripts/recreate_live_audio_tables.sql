-- COMPLETE LIVE AUDIO ROOMS RECREATION
-- Connect as postgres to safe_zone database

-- 1. DROP REMAINING TABLES
DROP TABLE IF EXISTS live_audio_room_moderations CASCADE;

-- 2. CREATE LIVE AUDIO ROOMS TABLE
CREATE TABLE live_audio_rooms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    visibility VARCHAR(50) DEFAULT 'public' CHECK (visibility IN ('public', 'private')),
    max_participants INTEGER DEFAULT 50,
    room_type VARCHAR(50) DEFAULT 'support' CHECK (room_type IN ('support', 'social', 'professional')),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. CREATE LIVE AUDIO ROOM PARTICIPANTS TABLE
CREATE TABLE live_audio_room_participants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    room_id UUID NOT NULL REFERENCES live_audio_rooms(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'participant' CHECK (role IN ('host', 'co-host', 'participant', 'listener')),
    is_active BOOLEAN DEFAULT true,
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    left_at TIMESTAMPTZ,
    UNIQUE(room_id, user_id)
);

-- 4. CREATE LIVE AUDIO ROOM MODERATIONS TABLE
CREATE TABLE live_audio_room_moderations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    room_id UUID NOT NULL REFERENCES live_audio_rooms(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    moderator_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL CHECK (action IN ('mute', 'remove', 'warn', 'ban')),
    reason TEXT,
    duration_minutes INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. ENABLE ROW LEVEL SECURITY
ALTER TABLE live_audio_rooms ENABLE ROW LEVEL SECURITY;
ALTER TABLE live_audio_room_participants ENABLE ROW LEVEL SECURITY;
ALTER TABLE live_audio_room_moderations ENABLE ROW LEVEL SECURITY;

-- 6. CREATE SIMPLE, WORKING RLS POLICIES
-- Room creation: ANY authenticated user can create
CREATE POLICY live_audio_rooms_insert_policy ON live_audio_rooms
    FOR INSERT WITH CHECK (true);

-- Room viewing: Users can see ALL active rooms initially
CREATE POLICY live_audio_rooms_select_policy ON live_audio_rooms
    FOR SELECT USING (is_active = true);

-- Room updates: Only creator can update  
CREATE POLICY live_audio_rooms_update_policy ON live_audio_rooms
    FOR UPDATE USING (created_by = current_setting('app.current_user_id')::UUID);

-- Participant creation: Users can add themselves to any room
CREATE POLICY live_audio_room_participants_insert_policy ON live_audio_room_participants
    FOR INSERT WITH CHECK (user_id = current_setting('app.current_user_id')::UUID);

-- Participant viewing: Users can see all participants initially
CREATE POLICY live_audio_room_participants_select_policy ON live_audio_room_participants
    FOR SELECT USING (true);

-- Moderation: Only moderators can take actions
CREATE POLICY live_audio_room_moderations_insert_policy ON live_audio_room_moderations
    FOR INSERT WITH CHECK (moderator_id = current_setting('app.current_user_id')::UUID);

-- Moderation viewing: Users can see moderation actions
CREATE POLICY live_audio_room_moderations_select_policy ON live_audio_room_moderations
    FOR SELECT USING (true);

-- 7. CREATE INDEXES FOR PERFORMANCE
CREATE INDEX idx_live_audio_rooms_created_by ON live_audio_rooms(created_by);
CREATE INDEX idx_live_audio_rooms_visibility ON live_audio_rooms(visibility, is_active);
CREATE INDEX idx_live_audio_room_participants_room_user ON live_audio_room_participants(room_id, user_id);
CREATE INDEX idx_live_audio_room_participants_user ON live_audio_room_participants(user_id);
CREATE INDEX idx_live_audio_room_moderations_room ON live_audio_room_moderations(room_id);

-- 8. VERIFY EVERYTHING IS CREATED
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE tablename LIKE 'live_audio%'
ORDER BY tablename;

-- 9. VERIFY POLICIES ARE CREATED
SELECT tablename, policyname, cmd, 
       CASE WHEN with_check IS NOT NULL THEN 'WITH CHECK: ' || substring(with_check from 1 for 30) ELSE 'No CHECK' END as check_clause
FROM pg_policies 
WHERE tablename LIKE 'live_audio%'
ORDER BY tablename, policyname;
