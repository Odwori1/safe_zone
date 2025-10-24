-- Enhanced Moderation Schema Updates for Phase 3, Item 6 - FIXED VERSION
-- Following EXACT same patterns as create_live_audio_rooms.sql

-- Add is_locked column to live_audio_rooms table
ALTER TABLE live_audio_rooms
ADD COLUMN IF NOT EXISTS is_locked BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS locked_by UUID REFERENCES users(id),
ADD COLUMN IF NOT EXISTS lock_reason TEXT,
ADD COLUMN IF NOT EXISTS locked_at TIMESTAMPTZ;

-- Create content reports table for reporting inappropriate content
CREATE TABLE IF NOT EXISTS content_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reporter_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content_type VARCHAR(50) NOT NULL, -- 'message', 'post', 'comment', 'room'
    content_id UUID NOT NULL,
    reason VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'reviewed', 'resolved', 'dismissed'
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMPTZ,
    resolution_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Ensure unique reports per user-content combination
    UNIQUE(reporter_id, content_type, content_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_content_reports_reporter_id ON content_reports(reporter_id);
CREATE INDEX IF NOT EXISTS idx_content_reports_content ON content_reports(content_type, content_id);
CREATE INDEX IF NOT EXISTS idx_content_reports_status ON content_reports(status);
CREATE INDEX IF NOT EXISTS idx_content_reports_created_at ON content_reports(created_at);

-- Enable RLS on content_reports table
ALTER TABLE content_reports ENABLE ROW LEVEL SECURITY;

-- RLS Policies for content_reports - FOLLOWING EXACT SAME SECURITY PATTERN
-- Users can see their own reports
CREATE POLICY content_reports_select_policy ON content_reports
    FOR SELECT USING (reporter_id = current_setting('app.current_user_id')::UUID);

-- Users can only insert their own reports
CREATE POLICY content_reports_insert_policy ON content_reports
    FOR INSERT WITH CHECK (reporter_id = current_setting('app.current_user_id')::UUID);

-- Only moderators/admins can update reports (for status changes)
CREATE POLICY content_reports_update_policy ON content_reports
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE id = current_setting('app.current_user_id')::UUID
            AND role IN ('moderator', 'admin')
        )
    );

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_content_reports_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_content_reports_updated_at
    BEFORE UPDATE ON content_reports
    FOR EACH ROW EXECUTE FUNCTION update_content_reports_updated_at();

-- Update the existing live_audio_rooms RLS policies to include lock checks
-- Note: We'll keep existing policies and add lock awareness to insert policy

-- Update the participants insert policy to respect room locks
DROP POLICY IF EXISTS live_audio_room_participants_insert_policy ON live_audio_room_participants;

CREATE POLICY live_audio_room_participants_insert_policy ON live_audio_room_participants
    FOR INSERT WITH CHECK (
        user_id = current_setting('app.current_user_id')::UUID
        AND NOT EXISTS (
            SELECT 1 FROM live_audio_rooms
            WHERE id = live_audio_room_participants.room_id
            AND is_locked = true
        )
    );

-- Create a simplified view for moderation dashboard (without current_participants column)
CREATE OR REPLACE VIEW moderation_dashboard AS
SELECT
    r.id as room_id,
    r.title as room_title,
    r.created_by as room_owner_id,
    u.username as room_owner_username,
    r.is_locked,
    r.locked_by,
    r.locked_at,
    COUNT(DISTINCT p.user_id) as active_participants,
    COUNT(DISTINCT m.id) as recent_mod_actions,
    MAX(m.created_at) as last_mod_action
FROM live_audio_rooms r
JOIN users u ON r.created_by = u.id
LEFT JOIN live_audio_room_participants p ON r.id = p.room_id AND p.left_at IS NULL
LEFT JOIN live_audio_room_moderations m ON r.id = m.room_id AND m.created_at > NOW() - INTERVAL '1 hour'
WHERE r.is_active = true
GROUP BY r.id, r.title, r.created_by, u.username, r.is_locked, r.locked_by, r.locked_at;

-- Grant permissions (following existing pattern)
GRANT SELECT ON moderation_dashboard TO safe_zone_app_user;
