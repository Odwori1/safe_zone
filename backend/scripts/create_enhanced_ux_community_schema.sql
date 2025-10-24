-- Enhanced User Experience & Community Management Schema
-- Phase 4, Items 3 & 4

-- ===== USER PREFERENCES (Item 3) =====
CREATE TABLE user_ui_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Theme & Appearance
    theme_preference VARCHAR(20) DEFAULT 'system', -- 'light', 'dark', 'system'
    font_size VARCHAR(20) DEFAULT 'medium', -- 'small', 'medium', 'large', 'x-large'
    high_contrast_mode BOOLEAN DEFAULT false,
    reduced_motion BOOLEAN DEFAULT false,
    
    -- Accessibility
    screen_reader_optimized BOOLEAN DEFAULT false,
    keyboard_navigation BOOLEAN DEFAULT true,
    focus_indicators BOOLEAN DEFAULT true,
    
    -- Content Preferences
    content_density VARCHAR(20) DEFAULT 'comfortable', -- 'compact', 'comfortable', 'spacious'
    image_descriptions BOOLEAN DEFAULT true,
    auto_play_media BOOLEAN DEFAULT false,
    
    -- Language & Regional
    language_preference VARCHAR(10) DEFAULT 'en',
    timezone VARCHAR(50) DEFAULT 'UTC',
    date_format VARCHAR(20) DEFAULT 'YYYY-MM-DD',
    
    -- Notifications & Privacy
    email_notifications BOOLEAN DEFAULT true,
    push_notifications BOOLEAN DEFAULT true,
    show_online_status BOOLEAN DEFAULT true,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(user_id)
);

-- ===== OFFLINE CONTENT (Item 3) =====
CREATE TABLE offline_content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    content_type VARCHAR(50) NOT NULL, -- 'journal', 'safety_plan', 'coping_strategy'
    content_id UUID NOT NULL,
    content_data JSONB NOT NULL,
    
    -- Sync management
    last_accessed TIMESTAMPTZ DEFAULT NOW(),
    access_count INTEGER DEFAULT 0,
    is_pinned BOOLEAN DEFAULT false,
    
    -- Metadata
    file_size_bytes INTEGER,
    expires_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===== DATA EXPORT JOBS (Item 3) =====
CREATE TABLE data_export_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Export configuration
    export_format VARCHAR(20) DEFAULT 'json', -- 'json', 'pdf', 'csv'
    data_categories TEXT[], -- ['journals', 'mood_data', 'safety_plans']
    date_range_start DATE,
    date_range_end DATE,
    
    -- Job status
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
    progress_percent INTEGER DEFAULT 0,
    
    -- Result
    file_url TEXT,
    file_size_bytes INTEGER,
    download_count INTEGER DEFAULT 0,
    
    -- Security
    access_token UUID DEFAULT gen_random_uuid(),
    expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '24 hours'),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    
    UNIQUE(access_token)
);

-- ===== COMMUNITY ANALYTICS (Item 4) =====
CREATE TABLE community_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Metrics
    date DATE NOT NULL,
    active_users INTEGER DEFAULT 0,
    new_registrations INTEGER DEFAULT 0,
    posts_created INTEGER DEFAULT 0,
    comments_created INTEGER DEFAULT 0,
    support_sessions INTEGER DEFAULT 0,
    
    -- Engagement metrics
    avg_session_duration_minutes DECIMAL(5,2),
    bounce_rate DECIMAL(5,4),
    
    -- Safety metrics
    crisis_interventions INTEGER DEFAULT 0,
    content_reports INTEGER DEFAULT 0,
    resolved_reports INTEGER DEFAULT 0,
    
    -- Performance
    response_time_ms DECIMAL(8,2),
    uptime_percent DECIMAL(5,2),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(date)
);

-- ===== USER REPUTATION SYSTEM (Item 4) =====
CREATE TABLE user_reputation_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Reputation metrics (private - only visible to user and moderators)
    helpfulness_score INTEGER DEFAULT 0,
    support_score INTEGER DEFAULT 0,
    engagement_score INTEGER DEFAULT 0,
    consistency_score INTEGER DEFAULT 0,
    
    -- Trust indicators
    account_age_days INTEGER DEFAULT 0,
    verified_contributor BOOLEAN DEFAULT false,
    trusted_member BOOLEAN DEFAULT false,
    
    -- Moderation
    warning_count INTEGER DEFAULT 0,
    last_warning_date DATE,
    
    calculated_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(user_id)
);

-- ===== CONFLICT RESOLUTION CASES (Item 4) =====
CREATE TABLE conflict_resolution_cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Case details
    case_type VARCHAR(50) NOT NULL, -- 'user_dispute', 'content_issue', 'behavior_concern'
    title VARCHAR(200) NOT NULL,
    description TEXT,
    priority VARCHAR(20) DEFAULT 'medium', -- 'low', 'medium', 'high', 'critical'
    
    -- Parties involved
    reporter_id UUID REFERENCES users(id),
    reported_user_id UUID REFERENCES users(id),
    content_reference_type VARCHAR(50),
    content_reference_id UUID,
    
    -- Resolution process
    assigned_moderator_id UUID REFERENCES users(id),
    status VARCHAR(20) DEFAULT 'open', -- 'open', 'investigating', 'resolved', 'closed'
    resolution_notes TEXT,
    resolution_type VARCHAR(50),
    
    -- Timelines
    reported_at TIMESTAMPTZ DEFAULT NOW(),
    assigned_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===== COMMUNITY EVENTS (Item 4) =====
CREATE TABLE community_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Event details
    title VARCHAR(200) NOT NULL,
    description TEXT,
    event_type VARCHAR(50) NOT NULL, -- 'support_group', 'workshop', 'qna', 'social'
    
    -- Scheduling
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL,
    timezone VARCHAR(50) DEFAULT 'UTC',
    is_recurring BOOLEAN DEFAULT false,
    recurrence_pattern VARCHAR(100),
    
    -- Access & Participation
    max_participants INTEGER,
    is_public BOOLEAN DEFAULT true,
    requires_rsvp BOOLEAN DEFAULT false,
    
    -- Hosting
    host_id UUID REFERENCES users(id),
    co_host_ids UUID[],
    
    -- Platform
    event_platform VARCHAR(50), -- 'audio_room', 'video_call', 'text_chat'
    platform_link TEXT,
    
    -- Analytics
    rsvp_count INTEGER DEFAULT 0,
    attendance_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===== VOLUNTEER MODERATOR TRAINING (Item 4) =====
CREATE TABLE moderator_training_modules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Module details
    title VARCHAR(200) NOT NULL,
    description TEXT,
    content_type VARCHAR(50) NOT NULL, -- 'video', 'article', 'interactive', 'assessment'
    content_url TEXT,
    estimated_duration_minutes INTEGER,
    
    -- Requirements
    required_for_role VARCHAR(50), -- 'junior_mod', 'senior_mod', 'crisis_specialist'
    difficulty_level VARCHAR(20) DEFAULT 'beginner',
    prerequisites UUID[], -- module_ids
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    version VARCHAR(20) DEFAULT '1.0',
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE moderator_training_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    module_id UUID NOT NULL REFERENCES moderator_training_modules(id),
    
    -- Progress tracking
    status VARCHAR(20) DEFAULT 'not_started', -- 'not_started', 'in_progress', 'completed', 'passed'
    progress_percent INTEGER DEFAULT 0,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    
    -- Assessment
    score DECIMAL(5,2),
    attempts INTEGER DEFAULT 0,
    feedback TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(user_id, module_id)
);

-- ===== INDEXES =====
CREATE INDEX idx_user_ui_preferences_user_id ON user_ui_preferences(user_id);
CREATE INDEX idx_offline_content_user_id ON offline_content(user_id);
CREATE INDEX idx_offline_content_type ON offline_content(content_type, content_id);
CREATE INDEX idx_data_export_jobs_user_id ON data_export_jobs(user_id);
CREATE INDEX idx_data_export_jobs_status ON data_export_jobs(status);
CREATE INDEX idx_data_export_jobs_token ON data_export_jobs(access_token);
CREATE INDEX idx_community_analytics_date ON community_analytics(date);
CREATE INDEX idx_user_reputation_user_id ON user_reputation_scores(user_id);
CREATE INDEX idx_conflict_cases_status ON conflict_resolution_cases(status);
CREATE INDEX idx_conflict_cases_reporter ON conflict_resolution_cases(reporter_id);
CREATE INDEX idx_conflict_cases_reported ON conflict_resolution_cases(reported_user_id);
CREATE INDEX idx_community_events_time ON community_events(start_time);
CREATE INDEX idx_community_events_host ON community_events(host_id);
CREATE INDEX idx_training_progress_user ON moderator_training_progress(user_id);
CREATE INDEX idx_training_progress_module ON moderator_training_progress(module_id);

-- ===== RLS POLICIES =====
ALTER TABLE user_ui_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE offline_content ENABLE ROW LEVEL SECURITY;
ALTER TABLE data_export_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE community_analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_reputation_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE conflict_resolution_cases ENABLE ROW LEVEL SECURITY;
ALTER TABLE community_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE moderator_training_modules ENABLE ROW LEVEL SECURITY;
ALTER TABLE moderator_training_progress ENABLE ROW LEVEL SECURITY;

-- User UI Preferences: Users can only access their own
CREATE POLICY user_ui_preferences_isolation ON user_ui_preferences
    FOR ALL USING (user_id = current_setting('app.current_user_id')::UUID);

-- Offline Content: Users can only access their own
CREATE POLICY offline_content_isolation ON offline_content
    FOR ALL USING (user_id = current_setting('app.current_user_id')::UUID);

-- Data Export Jobs: Users can only access their own
CREATE POLICY data_export_jobs_isolation ON data_export_jobs
    FOR ALL USING (user_id = current_setting('app.current_user_id')::UUID);

-- Community Analytics: Read-only for moderators/admins
CREATE POLICY community_analytics_mod_access ON community_analytics
    FOR SELECT USING (EXISTS (
        SELECT 1 FROM users WHERE id = current_setting('app.current_user_id')::UUID 
        AND (role = 'moderator' OR role = 'admin')
    ));

-- User Reputation: Users can see their own, moderators can see all
CREATE POLICY user_reputation_self_access ON user_reputation_scores
    FOR SELECT USING (user_id = current_setting('app.current_user_id')::UUID 
        OR EXISTS (
            SELECT 1 FROM users WHERE id = current_setting('app.current_user_id')::UUID 
            AND (role = 'moderator' OR role = 'admin')
        ));

-- Conflict Resolution: Moderators and involved parties can access
CREATE POLICY conflict_cases_access ON conflict_resolution_cases
    FOR ALL USING (
        reporter_id = current_setting('app.current_user_id')::UUID
        OR reported_user_id = current_setting('app.current_user_id')::UUID
        OR assigned_moderator_id = current_setting('app.current_user_id')::UUID
        OR EXISTS (
            SELECT 1 FROM users WHERE id = current_setting('app.current_user_id')::UUID 
            AND (role = 'moderator' OR role = 'admin')
        )
    );

-- Community Events: Public read, restricted write
CREATE POLICY community_events_read ON community_events
    FOR SELECT USING (is_public = true OR host_id = current_setting('app.current_user_id')::UUID);

CREATE POLICY community_events_mod_write ON community_events
    FOR ALL USING (EXISTS (
        SELECT 1 FROM users WHERE id = current_setting('app.current_user_id')::UUID 
        AND (role = 'moderator' OR role = 'admin')
    ));

-- Training Modules: Public read, restricted progress
CREATE POLICY training_modules_read ON moderator_training_modules
    FOR SELECT USING (is_active = true);

CREATE POLICY training_progress_isolation ON moderator_training_progress
    FOR ALL USING (user_id = current_setting('app.current_user_id')::UUID);

-- ===== TRIGGERS FOR UPDATED_AT =====
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_user_ui_preferences_updated_at BEFORE UPDATE ON user_ui_preferences FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_offline_content_updated_at BEFORE UPDATE ON offline_content FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_reputation_updated_at BEFORE UPDATE ON user_reputation_scores FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_conflict_cases_updated_at BEFORE UPDATE ON conflict_resolution_cases FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_community_events_updated_at BEFORE UPDATE ON community_events FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_training_progress_updated_at BEFORE UPDATE ON moderator_training_progress FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ===== SAMPLE DATA =====
INSERT INTO moderator_training_modules (title, description, content_type, estimated_duration_minutes, required_for_role, difficulty_level) VALUES
('Community Guidelines & Safety', 'Learn the core principles of our community guidelines and how to enforce them safely.', 'interactive', 45, 'junior_mod', 'beginner'),
('Crisis Recognition & Response', 'Training on identifying crisis situations and appropriate response protocols.', 'video', 60, 'junior_mod', 'intermediate'),
('De-escalation Techniques', 'Learn effective communication strategies for de-escalating conflicts.', 'interactive', 30, 'junior_mod', 'intermediate'),
('Advanced Moderation Tools', 'Comprehensive training on using advanced moderation features.', 'article', 25, 'senior_mod', 'advanced'),
('Privacy & Data Protection', 'Understanding user privacy rights and data protection responsibilities.', 'interactive', 40, 'senior_mod', 'intermediate');

