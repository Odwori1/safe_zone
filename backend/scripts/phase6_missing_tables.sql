-- ===== PHASE 6 MISSING TABLES IMPLEMENTATION =====
-- Following EXACT same security patterns as existing tables

-- 1. Telehealth Sessions Table
CREATE TABLE IF NOT EXISTS telehealth_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    professional_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    scheduled_time TIMESTAMPTZ NOT NULL,
    duration_minutes INTEGER NOT NULL DEFAULT 60,
    session_status VARCHAR(50) NOT NULL DEFAULT 'scheduled',
    meeting_url TEXT,
    recording_url TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. EMR Connections Table (HIPAA Compliant)
CREATE TABLE IF NOT EXISTS emr_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    emr_system VARCHAR(100) NOT NULL,
    connection_status VARCHAR(50) NOT NULL DEFAULT 'pending',
    last_sync TIMESTAMPTZ,
    consent_given_at TIMESTAMPTZ NOT NULL,
    consent_expires_at TIMESTAMPTZ NOT NULL,
    access_token_encrypted TEXT,
    refresh_token_encrypted TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Community Milestones Table
CREATE TABLE IF NOT EXISTS community_milestones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    milestone_type VARCHAR(100) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    achieved_at TIMESTAMPTZ NOT NULL,
    community_impact_metric JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Success Stories Table (with explicit consent)
CREATE TABLE IF NOT EXISTS success_stories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    story_content TEXT NOT NULL,
    consent_given BOOLEAN NOT NULL DEFAULT FALSE,
    consent_given_at TIMESTAMPTZ,
    anonymized BOOLEAN NOT NULL DEFAULT TRUE,
    featured BOOLEAN NOT NULL DEFAULT FALSE,
    featured_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. User Sessions Table (for timeout management)
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    device_id VARCHAR(100) NOT NULL,
    last_activity TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Device Sync Table
CREATE TABLE IF NOT EXISTS device_sync (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    device_type VARCHAR(50) NOT NULL,
    device_id VARCHAR(100) NOT NULL,
    last_sync TIMESTAMPTZ DEFAULT NOW(),
    sync_token VARCHAR(200),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. Tutorial Progress Table
CREATE TABLE IF NOT EXISTS tutorial_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tutorial_module VARCHAR(100) NOT NULL,
    progress_percentage INTEGER NOT NULL DEFAULT 0,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===== ENABLE ROW LEVEL SECURITY =====
ALTER TABLE telehealth_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE emr_connections ENABLE ROW LEVEL SECURITY;
ALTER TABLE community_milestones ENABLE ROW LEVEL SECURITY;
ALTER TABLE success_stories ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE device_sync ENABLE ROW LEVEL SECURITY;
ALTER TABLE tutorial_progress ENABLE ROW LEVEL SECURITY;

-- ===== CREATE RLS POLICIES =====

-- Telehealth Sessions: Users can only see their own sessions
CREATE POLICY telehealth_sessions_user_policy ON telehealth_sessions
    FOR ALL USING (user_id = current_setting('app.current_user_id')::UUID OR 
                  professional_id = current_setting('app.current_user_id')::UUID);

-- EMR Connections: Users can only see their own connections
CREATE POLICY emr_connections_user_policy ON emr_connections
    FOR ALL USING (user_id = current_setting('app.current_user_id')::UUID);

-- Community Milestones: Public read, admin write
CREATE POLICY community_milestones_read_policy ON community_milestones
    FOR SELECT USING (true);
CREATE POLICY community_milestones_write_policy ON community_milestones
    FOR ALL USING (EXISTS (SELECT 1 FROM users WHERE id = current_setting('app.current_user_id')::UUID AND role IN ('admin', 'moderator')));

-- Success Stories: Users see only their own or featured public stories
CREATE POLICY success_stories_user_policy ON success_stories
    FOR ALL USING (user_id = current_setting('app.current_user_id')::UUID OR 
                  (featured = true AND consent_given = true));

-- User Sessions: Users can only see their own sessions
CREATE POLICY user_sessions_user_policy ON user_sessions
    FOR ALL USING (user_id = current_setting('app.current_user_id')::UUID);

-- Device Sync: Users can only see their own devices
CREATE POLICY device_sync_user_policy ON device_sync
    FOR ALL USING (user_id = current_setting('app.current_user_id')::UUID);

-- Tutorial Progress: Users can only see their own progress
CREATE POLICY tutorial_progress_user_policy ON tutorial_progress
    FOR ALL USING (user_id = current_setting('app.current_user_id')::UUID);

-- ===== ADD MISSING COLUMNS TO EXISTING TABLE =====
ALTER TABLE ai_content_analysis 
ADD COLUMN IF NOT EXISTS content_summary TEXT,
ADD COLUMN IF NOT EXISTS summary_confidence DECIMAL(3,2);

-- ===== CREATE INDEXES FOR PERFORMANCE =====
CREATE INDEX IF NOT EXISTS idx_telehealth_sessions_user_id ON telehealth_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_telehealth_sessions_professional_id ON telehealth_sessions(professional_id);
CREATE INDEX IF NOT EXISTS idx_telehealth_sessions_scheduled_time ON telehealth_sessions(scheduled_time);

CREATE INDEX IF NOT EXISTS idx_emr_connections_user_id ON emr_connections(user_id);
CREATE INDEX IF NOT EXISTS idx_emr_connections_status ON emr_connections(connection_status);

CREATE INDEX IF NOT EXISTS idx_success_stories_user_id ON success_stories(user_id);
CREATE INDEX IF NOT EXISTS idx_success_stories_featured ON success_stories(featured) WHERE featured = true;

CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at);

CREATE INDEX IF NOT EXISTS idx_device_sync_user_id ON device_sync(user_id);
CREATE INDEX IF NOT EXISTS idx_device_sync_device_id ON device_sync(device_id);

CREATE INDEX IF NOT EXISTS idx_tutorial_progress_user_id ON tutorial_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_tutorial_progress_module ON tutorial_progress(tutorial_module);

