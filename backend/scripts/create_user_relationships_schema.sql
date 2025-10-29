-- User Relationships Table for follows and blocks
CREATE TABLE IF NOT EXISTS user_relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    follower_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    following_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    relationship_type TEXT NOT NULL CHECK (relationship_type IN ('follow', 'block')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Prevent duplicate relationships
    UNIQUE(follower_id, following_id, relationship_type),
    
    -- Prevent self-follow/self-block
    CONSTRAINT no_self_relationship CHECK (follower_id != following_id)
);

-- Enable Row Level Security
ALTER TABLE user_relationships ENABLE ROW LEVEL SECURITY;

-- RLS Policies for user_relationships
-- Users can only see relationships they're involved in
CREATE POLICY user_relationships_select_policy ON user_relationships
    FOR SELECT USING (
        follower_id = current_setting('app.current_user_id', true)::UUID OR
        following_id = current_setting('app.current_user_id', true)::UUID
    );

-- Users can only create relationships where they are the follower
CREATE POLICY user_relationships_insert_policy ON user_relationships
    FOR INSERT WITH CHECK (
        follower_id = current_setting('app.current_user_id', true)::UUID
    );

-- Users can only delete relationships they created
CREATE POLICY user_relationships_delete_policy ON user_relationships
    FOR DELETE USING (
        follower_id = current_setting('app.current_user_id', true)::UUID
    );

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_relationships_follower ON user_relationships(follower_id, relationship_type);
CREATE INDEX IF NOT EXISTS idx_user_relationships_following ON user_relationships(following_id, relationship_type);
CREATE INDEX IF NOT EXISTS idx_user_relationships_bidirectional ON user_relationships(follower_id, following_id);

-- User Reports Table
CREATE TABLE IF NOT EXISTS user_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reporter_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reported_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    report_reason TEXT NOT NULL,
    report_details TEXT,
    report_status TEXT DEFAULT 'pending' CHECK (report_status IN ('pending', 'reviewed', 'resolved', 'dismissed')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add unique constraint separately to avoid syntax error
ALTER TABLE user_reports ADD CONSTRAINT unique_pending_report 
    UNIQUE (reporter_id, reported_user_id, report_status) 
    WHERE (report_status = 'pending');

-- Enable Row Level Security
ALTER TABLE user_reports ENABLE ROW LEVEL SECURITY;

-- RLS Policies for user_reports
-- Users can only see reports they created
CREATE POLICY user_reports_select_policy ON user_reports
    FOR SELECT USING (
        reporter_id = current_setting('app.current_user_id', true)::UUID
    );

-- Users can only create reports where they are the reporter
CREATE POLICY user_reports_insert_policy ON user_reports
    FOR INSERT WITH CHECK (
        reporter_id = current_setting('app.current_user_id', true)::UUID
    );

-- Update updated_at timestamp function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_user_reports_updated_at 
    BEFORE UPDATE ON user_reports 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
