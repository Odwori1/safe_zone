-- Final Phase Schema: Phase 5 & 6 - Scale & Global Features + Advanced Innovation
-- Following EXACT same security patterns as previous phases

-- ===== MULTI-LANGUAGE SUPPORT (Phase 5) =====
CREATE TABLE language_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    preferred_language VARCHAR(10) DEFAULT 'en',
    interface_language VARCHAR(10) DEFAULT 'en',
    content_language VARCHAR(10) DEFAULT 'en',
    auto_translate BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id)
);

CREATE TABLE translated_content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_type VARCHAR(50) NOT NULL,
    content_id UUID NOT NULL,
    language_code VARCHAR(10) NOT NULL,
    translated_text TEXT NOT NULL,
    translation_quality VARCHAR(20) DEFAULT 'machine', -- 'machine', 'human', 'verified'
    translator_id UUID REFERENCES users(id),
    last_verified_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(content_type, content_id, language_code)
);

CREATE TABLE regional_resources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    country_code VARCHAR(5) NOT NULL,
    language_code VARCHAR(10) NOT NULL,
    resource_type VARCHAR(50) NOT NULL, -- 'crisis_line', 'hotline', 'support_group', 'professional'
    resource_name VARCHAR(200) NOT NULL,
    contact_info TEXT NOT NULL,
    operating_hours TEXT,
    services_offered TEXT[],
    is_active BOOLEAN DEFAULT true,
    verification_status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===== ACCESSIBILITY ENHANCEMENTS (Phase 5) =====
CREATE TABLE accessibility_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Visual
    high_contrast_mode BOOLEAN DEFAULT false,
    font_size_multiplier DECIMAL(3,2) DEFAULT 1.0,
    color_blind_mode VARCHAR(20) DEFAULT 'none',
    reduce_animations BOOLEAN DEFAULT false,
    seizure_safe_mode BOOLEAN DEFAULT false,
    
    -- Audio
    screen_reader_optimized BOOLEAN DEFAULT false,
    audio_descriptions BOOLEAN DEFAULT true,
    mono_audio BOOLEAN DEFAULT false,
    
    -- Interaction
    keyboard_only_navigation BOOLEAN DEFAULT false,
    voice_control_enabled BOOLEAN DEFAULT false,
    simplified_ui BOOLEAN DEFAULT false,
    cognitive_load_reduction BOOLEAN DEFAULT false,
    
    -- Content
    alt_text_required BOOLEAN DEFAULT true,
    transcript_required BOOLEAN DEFAULT true,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id)
);

-- ===== ENTERPRISE FEATURES (Phase 5) =====
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    organization_type VARCHAR(50) NOT NULL, -- 'school', 'company', 'nonprofit', 'healthcare'
    size_range VARCHAR(50), -- '1-50', '51-200', '201-1000', '1000+'
    industry VARCHAR(100),
    contact_email VARCHAR(200),
    website_url VARCHAR(500),
    is_verified BOOLEAN DEFAULT false,
    subscription_tier VARCHAR(50) DEFAULT 'basic',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE organization_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'member', -- 'admin', 'manager', 'member'
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true,
    UNIQUE(organization_id, user_id)
);

CREATE TABLE wellness_challenges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    challenge_type VARCHAR(50) NOT NULL, -- 'mindfulness', 'fitness', 'social', 'learning'
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    participation_goal INTEGER,
    is_public BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE challenge_participants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    challenge_id UUID NOT NULL REFERENCES wellness_challenges(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    progress_data JSONB,
    UNIQUE(challenge_id, user_id)
);

-- ===== ADVANCED AI FEATURES (Phase 6) =====
CREATE TABLE ai_chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_type VARCHAR(50) NOT NULL, -- 'support', 'crisis', 'wellness', 'general'
    context_data JSONB,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    session_duration_seconds INTEGER,
    satisfaction_rating INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE ai_chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES ai_chat_sessions(id) ON DELETE CASCADE,
    message_type VARCHAR(20) NOT NULL, -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    sentiment_score DECIMAL(3,2),
    urgency_level VARCHAR(20),
    response_time_ms INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE voice_mood_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    audio_file_url TEXT,
    analysis_result JSONB NOT NULL,
    mood_score DECIMAL(3,2),
    confidence_score DECIMAL(3,2),
    detected_emotions VARCHAR(50)[],
    analysis_timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE predictive_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    insight_type VARCHAR(50) NOT NULL,
    prediction_data JSONB NOT NULL,
    confidence_score DECIMAL(3,2),
    time_horizon VARCHAR(20), -- 'short_term', 'medium_term', 'long_term'
    generated_at TIMESTAMPTZ DEFAULT NOW(),
    is_actionable BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===== INTEGRATION ECOSYSTEM (Phase 6) =====
CREATE TABLE user_integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    integration_type VARCHAR(50) NOT NULL, -- 'wearable', 'calendar', 'health_app', 'telehealth'
    service_name VARCHAR(100) NOT NULL,
    connection_status VARCHAR(20) DEFAULT 'connected', -- 'connected', 'disconnected', 'error'
    last_sync_at TIMESTAMPTZ,
    sync_frequency VARCHAR(20) DEFAULT 'daily',
    config_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, integration_type, service_name)
);

CREATE TABLE wearable_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    integration_id UUID REFERENCES user_integrations(id) ON DELETE CASCADE,
    data_type VARCHAR(50) NOT NULL, -- 'heart_rate', 'sleep', 'steps', 'stress'
    value DECIMAL(10,4),
    unit VARCHAR(20),
    measured_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE emergency_coordination (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    contact_name VARCHAR(200) NOT NULL,
    contact_relationship VARCHAR(100),
    contact_methods JSONB NOT NULL, -- {phone: '', email: '', etc}
    notification_preferences JSONB,
    last_contacted TIMESTAMPTZ,
    is_primary BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===== COMMUNITY BUILDING (Phase 6) =====
CREATE TABLE peer_support_matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    matched_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    match_reason TEXT,
    compatibility_score DECIMAL(3,2),
    match_type VARCHAR(50) DEFAULT 'wellness', -- 'crisis', 'wellness', 'interest'
    status VARCHAR(20) DEFAULT 'active',
    matched_at TIMESTAMPTZ DEFAULT NOW(),
    last_interaction TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE group_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    facilitator_id UUID REFERENCES users(id),
    session_type VARCHAR(50) NOT NULL, -- 'therapy', 'support', 'workshop'
    title VARCHAR(200) NOT NULL,
    description TEXT,
    max_participants INTEGER,
    scheduled_time TIMESTAMPTZ NOT NULL,
    duration_minutes INTEGER DEFAULT 60,
    platform VARCHAR(50), -- 'audio_room', 'video', 'text'
    is_recurring BOOLEAN DEFAULT false,
    recurrence_pattern VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE session_participants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES group_sessions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) DEFAULT 'participant', -- 'facilitator', 'co_facilitator', 'participant'
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    left_at TIMESTAMPTZ,
    participation_level VARCHAR(20), -- 'active', 'passive', 'listener'
    UNIQUE(session_id, user_id)
);

-- ===== MAINTENANCE & MONITORING (Phase 6) =====
CREATE TABLE system_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_type VARCHAR(50) NOT NULL,
    metric_value DECIMAL(12,4),
    unit VARCHAR(20),
    recorded_at TIMESTAMPTZ DEFAULT NOW(),
    tags JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE user_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    feedback_type VARCHAR(50) NOT NULL, -- 'bug', 'feature', 'improvement', 'compliment'
    category VARCHAR(100),
    description TEXT NOT NULL,
    urgency VARCHAR(20) DEFAULT 'medium',
    status VARCHAR(20) DEFAULT 'new',
    assigned_to UUID REFERENCES users(id),
    resolved_at TIMESTAMPTZ,
    resolution_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE compliance_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    action_type VARCHAR(100) NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    compliance_type VARCHAR(50), -- 'gdpr', 'hipaa', 'ccpa'
    action_timestamp TIMESTAMPTZ DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT,
    additional_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===== INDEXES =====
CREATE INDEX idx_language_preferences_user_id ON language_preferences(user_id);
CREATE INDEX idx_translated_content_language ON translated_content(language_code);
CREATE INDEX idx_regional_resources_country ON regional_resources(country_code, language_code);
CREATE INDEX idx_accessibility_preferences_user_id ON accessibility_preferences(user_id);
CREATE INDEX idx_organization_members_user_id ON organization_members(user_id);
CREATE INDEX idx_organization_members_org_id ON organization_members(organization_id);
CREATE INDEX idx_wellness_challenges_org_id ON wellness_challenges(organization_id);
CREATE INDEX idx_challenge_participants_user_id ON challenge_participants(user_id);
CREATE INDEX idx_ai_chat_sessions_user_id ON ai_chat_sessions(user_id);
CREATE INDEX idx_ai_chat_messages_session_id ON ai_chat_messages(session_id);
CREATE INDEX idx_voice_mood_analysis_user_id ON voice_mood_analysis(user_id);
CREATE INDEX idx_predictive_insights_user_id ON predictive_insights(user_id);
CREATE INDEX idx_user_integrations_user_id ON user_integrations(user_id);
CREATE INDEX idx_wearable_data_user_time ON wearable_data(user_id, measured_at);
CREATE INDEX idx_emergency_coordination_user_id ON emergency_coordination(user_id);
CREATE INDEX idx_peer_support_matches_user_id ON peer_support_matches(user_id);
CREATE INDEX idx_group_sessions_time ON group_sessions(scheduled_time);
CREATE INDEX idx_session_participants_session_id ON session_participants(session_id);
CREATE INDEX idx_system_metrics_time ON system_metrics(recorded_at);
CREATE INDEX idx_user_feedback_status ON user_feedback(status);
CREATE INDEX idx_compliance_logs_timestamp ON compliance_logs(action_timestamp);

-- ===== RLS POLICIES =====
ALTER TABLE language_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE translated_content ENABLE ROW LEVEL SECURITY;
ALTER TABLE regional_resources ENABLE ROW LEVEL SECURITY;
ALTER TABLE accessibility_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE organization_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE wellness_challenges ENABLE ROW LEVEL SECURITY;
ALTER TABLE challenge_participants ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE voice_mood_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE predictive_insights ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_integrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE wearable_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE emergency_coordination ENABLE ROW LEVEL SECURITY;
ALTER TABLE peer_support_matches ENABLE ROW LEVEL SECURITY;
ALTER TABLE group_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE session_participants ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE compliance_logs ENABLE ROW LEVEL SECURITY;

-- Language Preferences: Users can only access their own
CREATE POLICY language_preferences_isolation ON language_preferences
    FOR ALL USING (user_id = current_setting('app.current_user_id')::UUID);

-- Translated Content: Public read access
CREATE POLICY translated_content_read ON translated_content
    FOR SELECT USING (true);

-- Regional Resources: Public read access to active resources
CREATE POLICY regional_resources_read ON regional_resources
    FOR SELECT USING (is_active = true);

-- Accessibility Preferences: Users can only access their own
CREATE POLICY accessibility_preferences_isolation ON accessibility_preferences
    FOR ALL USING (user_id = current_setting('app.current_user_id')::UUID);

-- Organizations: Public read, restricted write
CREATE POLICY organizations_read ON organizations
    FOR SELECT USING (true);

CREATE POLICY organizations_mod_write ON organizations
    FOR ALL USING (EXISTS (
        SELECT 1 FROM users WHERE id = current_setting('app.current_user_id')::UUID 
        AND (role = 'admin' OR role = 'moderator')
    ));

-- Organization Members: Users can see their own memberships
CREATE POLICY organization_members_isolation ON organization_members
    FOR ALL USING (user_id = current_setting('app.current_user_id')::UUID 
        OR EXISTS (
            SELECT 1 FROM organization_members om 
            WHERE om.organization_id = organization_members.organization_id 
            AND om.user_id = current_setting('app.current_user_id')::UUID 
            AND om.role IN ('admin', 'manager')
        ));

-- Wellness Challenges: Public read for public challenges
CREATE POLICY wellness_challenges_read ON wellness_challenges
    FOR SELECT USING (is_public = true OR organization_id IN (
        SELECT organization_id FROM organization_members 
        WHERE user_id = current_setting('app.current_user_id')::UUID
    ));

-- Challenge Participants: Users can only see their own participation
CREATE POLICY challenge_participants_isolation ON challenge_participants
    FOR ALL USING (user_id = current_setting('app.current_user_id')::UUID 
        OR EXISTS (
            SELECT 1 FROM wellness_challenges wc 
            JOIN organization_members om ON wc.organization_id = om.organization_id
            WHERE wc.id = challenge_participants.challenge_id 
            AND om.user_id = current_setting('app.current_user_id')::UUID 
            AND om.role IN ('admin', 'manager')
        ));

-- AI Chat Sessions: Users can only access their own
CREATE POLICY ai_chat_sessions_isolation ON ai_chat_sessions
    FOR ALL USING (user_id = current_setting('app.current_user_id')::UUID);

-- AI Chat Messages: Users can only access their own session messages
CREATE POLICY ai_chat_messages_isolation ON ai_chat_messages
    FOR ALL USING (session_id IN (
        SELECT id FROM ai_chat_sessions 
        WHERE user_id = current_setting('app.current_user_id')::UUID
    ));

-- Voice Mood Analysis: Users can only access their own
CREATE POLICY voice_mood_analysis_isolation ON voice_mood_analysis
    FOR ALL USING (user_id = current_setting('app.current_user_id')::UUID);

-- Predictive Insights: Users can only access their own
CREATE POLICY predictive_insights_isolation ON predictive_insights
    FOR ALL USING (user_id = current_setting('app.current_user_id')::UUID);

-- User Integrations: Users can only access their own
CREATE POLICY user_integrations_isolation ON user_integrations
    FOR ALL USING (user_id = current_setting('app.current_user_id')::UUID);

-- Wearable Data: Users can only access their own
CREATE POLICY wearable_data_isolation ON wearable_data
    FOR ALL USING (user_id = current_setting('app.current_user_id')::UUID);

-- Emergency Coordination: Users can only access their own
CREATE POLICY emergency_coordination_isolation ON emergency_coordination
    FOR ALL USING (user_id = current_setting('app.current_user_id')::UUID);

-- Peer Support Matches: Users can only access their own matches
CREATE POLICY peer_support_matches_isolation ON peer_support_matches
    FOR ALL USING (user_id = current_setting('app.current_user_id')::UUID 
        OR matched_user_id = current_setting('app.current_user_id')::UUID);

-- Group Sessions: Public read for upcoming sessions
CREATE POLICY group_sessions_read ON group_sessions
    FOR SELECT USING (scheduled_time > NOW() OR facilitator_id = current_setting('app.current_user_id')::UUID);

-- Session Participants: Users can see sessions they're in
CREATE POLICY session_participants_isolation ON session_participants
    FOR ALL USING (user_id = current_setting('app.current_user_id')::UUID 
        OR session_id IN (
            SELECT id FROM group_sessions 
            WHERE facilitator_id = current_setting('app.current_user_id')::UUID
        ));

-- System Metrics: Admin only
CREATE POLICY system_metrics_admin_only ON system_metrics
    FOR ALL USING (EXISTS (
        SELECT 1 FROM users WHERE id = current_setting('app.current_user_id')::UUID 
        AND role = 'admin'
    ));

-- User Feedback: Users can access their own, admins can access all
CREATE POLICY user_feedback_isolation ON user_feedback
    FOR ALL USING (user_id = current_setting('app.current_user_id')::UUID 
        OR EXISTS (
            SELECT 1 FROM users WHERE id = current_setting('app.current_user_id')::UUID 
            AND role IN ('admin', 'moderator')
        ));

-- Compliance Logs: Admin only
CREATE POLICY compliance_logs_admin_only ON compliance_logs
    FOR ALL USING (EXISTS (
        SELECT 1 FROM users WHERE id = current_setting('app.current_user_id')::UUID 
        AND role = 'admin'
    ));

-- ===== TRIGGERS FOR UPDATED_AT =====
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_language_preferences_updated_at BEFORE UPDATE ON language_preferences FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_translated_content_updated_at BEFORE UPDATE ON translated_content FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_regional_resources_updated_at BEFORE UPDATE ON regional_resources FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_accessibility_preferences_updated_at BEFORE UPDATE ON accessibility_preferences FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_wellness_challenges_updated_at BEFORE UPDATE ON wellness_challenges FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_integrations_updated_at BEFORE UPDATE ON user_integrations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_emergency_coordination_updated_at BEFORE UPDATE ON emergency_coordination FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_group_sessions_updated_at BEFORE UPDATE ON group_sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_feedback_updated_at BEFORE UPDATE ON user_feedback FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ===== SAMPLE DATA =====
INSERT INTO regional_resources (country_code, language_code, resource_type, resource_name, contact_info, services_offered) VALUES
('US', 'en', 'crisis_line', 'National Suicide Prevention Lifeline', '1-800-273-8255', '{"crisis_support", "suicide_prevention"}'),
('US', 'es', 'crisis_line', 'Línea Nacional de Prevención del Suicidio', '1-888-628-9454', '{"crisis_support", "suicide_prevention"}'),
('CA', 'en', 'crisis_line', 'Crisis Services Canada', '1-833-456-4566', '{"crisis_support", "mental_health"}'),
('CA', 'fr', 'crisis_line', 'Services de crise Canada', '1-866-277-3553', '{"crisis_support", "mental_health"}'),
('GB', 'en', 'crisis_line', 'Samaritans', '116 123', '{"emotional_support", "crisis_listening"}');

INSERT INTO organizations (name, organization_type, size_range, industry, is_verified) VALUES
('Safe Zone Enterprise', 'company', '201-1000', 'Technology', true),
('University Wellness Program', 'school', '1000+', 'Education', true),
('Community Mental Health Nonprofit', 'nonprofit', '51-200', 'Healthcare', true);

