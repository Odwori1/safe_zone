-- Secure Live Audio Rooms Schema for Phase 3, Item 5
-- Following exact same security patterns as messaging schema

-- Live audio rooms table
CREATE TABLE IF NOT EXISTS live_audio_rooms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT true,
    is_public BOOLEAN DEFAULT true,
    max_participants INTEGER DEFAULT 50,
    current_participants INTEGER DEFAULT 0,
    room_type VARCHAR(50) DEFAULT 'support', -- 'support', 'discussion', 'social'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Security constraints
    CONSTRAINT valid_max_participants CHECK (max_participants BETWEEN 1 AND 100),
    CONSTRAINT valid_current_participants CHECK (current_participants BETWEEN 0 AND max_participants)
);

-- Room participants table (real-time tracking)
CREATE TABLE IF NOT EXISTS live_audio_room_participants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    room_id UUID NOT NULL REFERENCES live_audio_rooms(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'participant', -- 'participant', 'speaker', 'moderator', 'host'
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    left_at TIMESTAMPTZ NULL,
    last_active_at TIMESTAMPTZ DEFAULT NOW()

    -- Note: We'll handle unique active participation via application logic
    -- since partial unique indexes with WHERE clauses are complex
);

-- Room moderation actions table
CREATE TABLE IF NOT EXISTS live_audio_room_moderations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    room_id UUID NOT NULL REFERENCES live_audio_rooms(id) ON DELETE CASCADE,
    moderator_id UUID NOT NULL REFERENCES users(id),
    target_user_id UUID NOT NULL REFERENCES users(id),
    action_type VARCHAR(50) NOT NULL, -- 'mute', 'remove', 'ban', 'warning'
    reason TEXT,
    duration_minutes INTEGER, -- NULL for permanent actions
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_live_audio_rooms_created_by ON live_audio_rooms(created_by);
CREATE INDEX IF NOT EXISTS idx_live_audio_rooms_is_active ON live_audio_rooms(is_active);
CREATE INDEX IF NOT EXISTS idx_live_audio_rooms_created_at ON live_audio_rooms(created_at);
CREATE INDEX IF NOT EXISTS idx_live_audio_room_participants_room_id ON live_audio_room_participants(room_id);
CREATE INDEX IF NOT EXISTS idx_live_audio_room_participants_user_id ON live_audio_room_participants(user_id);
CREATE INDEX IF NOT EXISTS idx_live_audio_room_participants_active ON live_audio_room_participants(room_id, user_id, left_at);
CREATE INDEX IF NOT EXISTS idx_live_audio_room_moderations_room_id ON live_audio_room_moderations(room_id);
CREATE INDEX IF NOT EXISTS idx_live_audio_room_moderations_target_user ON live_audio_room_moderations(target_user_id);

-- CRITICAL: Enable Row Level Security (RLS) on all tables - EXACT SAME PATTERN
ALTER TABLE live_audio_rooms ENABLE ROW LEVEL SECURITY;
ALTER TABLE live_audio_room_participants ENABLE ROW LEVEL SECURITY;
ALTER TABLE live_audio_room_moderations ENABLE ROW LEVEL SECURITY;

-- CRITICAL: RLS Policies for live_audio_rooms - FOLLOWING MESSAGING PATTERN
-- Users can see active public rooms OR rooms they created OR rooms they participate in
CREATE POLICY live_audio_rooms_select_policy ON live_audio_rooms
    FOR SELECT USING (
        is_active = true AND (
            is_public = true 
            OR created_by = current_setting('app.current_user_id')::UUID
            OR EXISTS (
                SELECT 1 FROM live_audio_room_participants p
                WHERE p.room_id = live_audio_rooms.id 
                AND p.user_id = current_setting('app.current_user_id')::UUID
                AND p.left_at IS NULL
            )
        )
    );

-- Users can only insert rooms they create
CREATE POLICY live_audio_rooms_insert_policy ON live_audio_rooms
    FOR INSERT WITH CHECK (created_by = current_setting('app.current_user_id')::UUID);

-- Users can only update rooms they created
CREATE POLICY live_audio_rooms_update_policy ON live_audio_rooms
    FOR UPDATE USING (created_by = current_setting('app.current_user_id')::UUID);

-- CRITICAL: RLS Policies for live_audio_room_participants - FOLLOWING MESSAGING PATTERN
-- Users can see participants in rooms they have access to
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

-- CRITICAL: RLS Policies for live_audio_room_moderations
-- Users can see moderation actions in rooms they moderate or where they were target
CREATE POLICY live_audio_room_moderations_select_policy ON live_audio_room_moderations
    FOR SELECT USING (
        moderator_id = current_setting('app.current_user_id')::UUID
        OR target_user_id = current_setting('app.current_user_id')::UUID
        OR EXISTS (
            SELECT 1 FROM live_audio_room_participants p
            WHERE p.room_id = live_audio_room_moderations.room_id
            AND p.user_id = current_setting('app.current_user_id')::UUID
            AND p.role IN ('moderator', 'host')
            AND p.left_at IS NULL
        )
    );

-- Only moderators/hosts can insert moderation actions
CREATE POLICY live_audio_room_moderations_insert_policy ON live_audio_room_moderations
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM live_audio_room_participants p
            WHERE p.room_id = live_audio_room_moderations.room_id
            AND p.user_id = current_setting('app.current_user_id')::UUID
            AND p.role IN ('moderator', 'host')
            AND p.left_at IS NULL
        )
    );

-- Create updated_at triggers (consistent with existing patterns)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_live_audio_rooms_updated_at
    BEFORE UPDATE ON live_audio_rooms
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to update participant count automatically
CREATE OR REPLACE FUNCTION update_room_participant_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' AND NEW.left_at IS NULL THEN
        UPDATE live_audio_rooms 
        SET current_participants = current_participants + 1
        WHERE id = NEW.room_id;
    ELSIF TG_OP = 'UPDATE' AND NEW.left_at IS NOT NULL AND OLD.left_at IS NULL THEN
        UPDATE live_audio_rooms 
        SET current_participants = GREATEST(0, current_participants - 1)
        WHERE id = NEW.room_id;
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_participant_count_on_join
    AFTER INSERT ON live_audio_room_participants
    FOR EACH ROW EXECUTE FUNCTION update_room_participant_count();

CREATE TRIGGER update_participant_count_on_leave
    AFTER UPDATE ON live_audio_room_participants
    FOR EACH ROW EXECUTE FUNCTION update_room_participant_count();
