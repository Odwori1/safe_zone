-- Advanced Safety Systems Schema for Phase 4, Item 2
-- Building upon existing crisis_resources, emergency_contacts, and user_crisis_preferences
-- Following EXACT same patterns as ai_personalization_schema.sql

-- Crisis Detection Alerts Table
CREATE TABLE IF NOT EXISTS crisis_detection_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Detection Source
    detection_source VARCHAR(50) NOT NULL, -- 'ai_content', 'behavior_pattern', 'manual_report', 'wellness_check'
    source_content_type VARCHAR(50), -- 'post', 'comment', 'mood_entry', 'message'
    source_content_id UUID,
    
    -- Risk Assessment
    risk_level VARCHAR(20) NOT NULL, -- 'low', 'medium', 'high', 'severe', 'critical'
    risk_score DECIMAL(3,2) NOT NULL, -- 0.0 to 1.0
    risk_factors TEXT[], -- ['suicidal_ideation', 'self_harm', 'isolation', 'substance_abuse']
    confidence_score DECIMAL(3,2), -- AI confidence in detection
    
    -- Alert Details
    alert_message TEXT,
    detected_patterns JSONB, -- Specific patterns detected
    context_data JSONB, -- Additional context for moderators
    
    -- Response Status
    status VARCHAR(20) DEFAULT 'new', -- 'new', 'reviewing', 'escalated', 'resolved', 'false_positive'
    assigned_moderator_id UUID REFERENCES users(id),
    escalation_level INTEGER DEFAULT 1, -- 1-5, higher = more urgent
    
    -- Response Actions
    automated_actions_taken TEXT[], -- ['wellness_check', 'resource_suggestion', 'moderator_notified']
    moderator_notes TEXT,
    resolution_notes TEXT,
    
    -- Timestamps
    detected_at TIMESTAMPTZ DEFAULT NOW(),
    reviewed_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Safety Plans Table
CREATE TABLE IF NOT EXISTS safety_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Plan Details
    plan_name VARCHAR(200) NOT NULL,
    plan_version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    
    -- Warning Signs
    personal_warning_signs TEXT[], -- User's identified warning signs
    early_warning_triggers TEXT[], -- Specific triggers to watch for
    
    -- Coping Strategies
    internal_coping_strategies TEXT[], -- Things user can do themselves
    social_coping_strategies TEXT[], -- People to contact
    professional_coping_strategies TEXT[], -- Professional resources
    
    -- Emergency Contacts
    emergency_contact_instructions TEXT,
    crisis_line_preferences TEXT[], -- Preferred crisis lines
    
    -- Environment Safety
    means_restriction_plan TEXT, -- How to make environment safer
    safe_locations TEXT[], -- Places to go when feeling unsafe
    
    -- Plan Metadata
    last_reviewed_date DATE,
    next_review_date DATE,
    created_from_template_id UUID, -- Reference to safety_plan_templates
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- One active plan per user
    UNIQUE(user_id) WHERE is_active = true
);

-- Safety Plan Templates Table
CREATE TABLE IF NOT EXISTS safety_plan_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Template Details
    template_name VARCHAR(200) NOT NULL,
    template_description TEXT,
    target_audience VARCHAR(100), -- 'general', 'depression', 'anxiety', 'ptsd', 'substance_use'
    difficulty_level VARCHAR(20) DEFAULT 'beginner', -- 'beginner', 'intermediate', 'advanced'
    
    -- Template Content
    default_warning_signs TEXT[],
    default_coping_strategies TEXT[],
    default_emergency_instructions TEXT,
    default_environment_safety TEXT,
    
    -- Professional Guidance
    professional_notes TEXT,
    recommended_review_frequency_days INTEGER DEFAULT 30,
    
    -- Accessibility
    is_public BOOLEAN DEFAULT true,
    available_languages TEXT[] DEFAULT '{"en"}',
    
    -- Metadata
    created_by UUID REFERENCES users(id),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Wellness Check-ins Table
CREATE TABLE IF NOT EXISTS wellness_check_ins (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Check-in Details
    check_in_type VARCHAR(50) NOT NULL, -- 'scheduled', 'triggered', 'manual', 'follow_up'
    trigger_source VARCHAR(100), -- 'crisis_alert', 'behavior_pattern', 'safety_plan'
    trigger_alert_id UUID REFERENCES crisis_detection_alerts(id),
    
    -- Check-in Content
    check_in_message TEXT NOT NULL,
    response_options JSONB, -- Multiple choice options for quick response
    custom_response_prompt TEXT,
    
    -- User Response
    user_response TEXT,
    selected_options TEXT[],
    response_mood VARCHAR(50), -- User's reported mood
    response_urgency INTEGER CHECK (response_urgency BETWEEN 1 AND 10),
    
    -- Follow-up Actions
    requires_follow_up BOOLEAN DEFAULT false,
    follow_up_actions TEXT[], -- ['moderator_review', 'resource_suggestion', 'safety_plan_update']
    follow_up_notes TEXT,
    
    -- Status and Timing
    status VARCHAR(20) DEFAULT 'sent', -- 'sent', 'responded', 'follow_up_required', 'completed'
    sent_at TIMESTAMPTZ DEFAULT NOW(),
    responded_at TIMESTAMPTZ,
    follow_up_completed_at TIMESTAMPTZ,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Escalation Protocols Table
CREATE TABLE IF NOT EXISTS escalation_protocols (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Protocol Definition
    protocol_name VARCHAR(200) NOT NULL,
    trigger_risk_level VARCHAR(20) NOT NULL, -- 'medium', 'high', 'severe', 'critical'
    trigger_conditions JSONB, -- Specific conditions that trigger this protocol
    
    -- Response Steps
    immediate_actions TEXT[] NOT NULL, -- First actions to take
    follow_up_actions TEXT[], -- Subsequent actions
    time_sensitive_actions JSONB, -- Actions with specific timeframes
    
    -- Communication
    internal_communication_template TEXT, -- How to communicate with team
    user_communication_template TEXT, -- How to communicate with user
    emergency_contact_communication_template TEXT, -- How to communicate with contacts
    
    -- Resource Coordination
    required_resources TEXT[], -- Resources needed for this protocol
    professional_involvement_required BOOLEAN DEFAULT false,
    external_services_involvement TEXT[], -- External services to involve
    
    -- Protocol Metadata
    is_active BOOLEAN DEFAULT true,
    version INTEGER DEFAULT 1,
    last_reviewed_date DATE,
    
    -- Metadata
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Crisis Intervention Queue Table
CREATE TABLE IF NOT EXISTS crisis_intervention_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_id UUID NOT NULL REFERENCES crisis_detection_alerts(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Queue Management
    queue_priority INTEGER NOT NULL CHECK (queue_priority BETWEEN 1 AND 10), -- 1 = highest priority
    queue_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'assigned', 'in_progress', 'completed', 'escalated'
    
    -- Assignment
    assigned_professional_id UUID REFERENCES users(id), -- Professional helper
    assigned_at TIMESTAMPTZ,
    estimated_response_time_minutes INTEGER,
    
    -- Intervention Details
    required_expertise TEXT[], -- ['suicide_prevention', 'substance_abuse', 'trauma']
    intervention_protocol_id UUID REFERENCES escalation_protocols(id),
    custom_intervention_plan TEXT,
    
    -- Progress Tracking
    contact_attempts INTEGER DEFAULT 0,
    last_contact_attempt TIMESTAMPTZ,
    next_follow_up TIMESTAMPTZ,
    
    -- Outcome
    intervention_outcome VARCHAR(50), -- 'successful', 'partial', 'unsuccessful', 'referred'
    outcome_notes TEXT,
    follow_up_required BOOLEAN DEFAULT false,
    
    -- Timestamps
    entered_queue_at TIMESTAMPTZ DEFAULT NOW(),
    intervention_started_at TIMESTAMPTZ,
    intervention_completed_at TIMESTAMPTZ,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_crisis_alerts_user ON crisis_detection_alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_crisis_alerts_risk_level ON crisis_detection_alerts(risk_level);
CREATE INDEX IF NOT EXISTS idx_crisis_alerts_status ON crisis_detection_alerts(status);
CREATE INDEX IF NOT EXISTS idx_crisis_alerts_detected_at ON crisis_detection_alerts(detected_at);
CREATE INDEX IF NOT EXISTS idx_safety_plans_user ON safety_plans(user_id);
CREATE INDEX IF NOT EXISTS idx_safety_plans_active ON safety_plans(is_active);
CREATE INDEX IF NOT EXISTS idx_wellness_check_ins_user ON wellness_check_ins(user_id);
CREATE INDEX IF NOT EXISTS idx_wellness_check_ins_status ON wellness_check_ins(status);
CREATE INDEX IF NOT EXISTS idx_wellness_check_ins_sent_at ON wellness_check_ins(sent_at);
CREATE INDEX IF NOT EXISTS idx_escalation_protocols_risk ON escalation_protocols(trigger_risk_level);
CREATE INDEX IF NOT EXISTS idx_intervention_queue_priority ON crisis_intervention_queue(queue_priority);
CREATE INDEX IF NOT EXISTS idx_intervention_queue_status ON crisis_intervention_queue(queue_status);
CREATE INDEX IF NOT EXISTS idx_intervention_queue_user ON crisis_intervention_queue(user_id);

-- Enable RLS on all tables
ALTER TABLE crisis_detection_alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE safety_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE safety_plan_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE wellness_check_ins ENABLE ROW LEVEL SECURITY;
ALTER TABLE escalation_protocols ENABLE ROW LEVEL SECURITY;
ALTER TABLE crisis_intervention_queue ENABLE ROW LEVEL SECURITY;

-- RLS Policies - FOLLOWING EXACT SAME SECURITY PATTERN

-- Crisis Detection Alerts Policies
-- Users can only see alerts about themselves
CREATE POLICY crisis_alerts_select_policy ON crisis_detection_alerts
    FOR SELECT USING (user_id = current_setting('app.current_user_id')::UUID);

-- Only AI system and moderators can create alerts
CREATE POLICY crisis_alerts_insert_policy ON crisis_detection_alerts
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id = current_setting('app.current_user_id')::UUID 
            AND role IN ('admin', 'moderator', 'helper')
        )
    );

-- Moderators can update alerts
CREATE POLICY crisis_alerts_update_policy ON crisis_detection_alerts
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id = current_setting('app.current_user_id')::UUID 
            AND role IN ('admin', 'moderator', 'helper')
        )
    );

-- Safety Plans Policies
-- Users can only see and manage their own safety plans
CREATE POLICY safety_plans_select_policy ON safety_plans
    FOR SELECT USING (user_id = current_setting('app.current_user_id')::UUID);

CREATE POLICY safety_plans_insert_policy ON safety_plans
    FOR INSERT WITH CHECK (user_id = current_setting('app.current_user_id')::UUID);

CREATE POLICY safety_plans_update_policy ON safety_plans
    FOR UPDATE USING (user_id = current_setting('app.current_user_id')::UUID);

-- Safety Plan Templates Policies (public read, admin write)
CREATE POLICY safety_templates_select_policy ON safety_plan_templates
    FOR SELECT USING (is_public = true OR is_active = true);

CREATE POLICY safety_templates_insert_policy ON safety_plan_templates
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id = current_setting('app.current_user_id')::UUID 
            AND role IN ('admin', 'moderator', 'helper')
        )
    );

-- Wellness Check-ins Policies
-- Users can only see their own check-ins
CREATE POLICY wellness_check_ins_select_policy ON wellness_check_ins
    FOR SELECT USING (user_id = current_setting('app.current_user_id')::UUID);

-- Only system and moderators can create check-ins
CREATE POLICY wellness_check_ins_insert_policy ON wellness_check_ins
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id = current_setting('app.current_user_id')::UUID 
            AND role IN ('admin', 'moderator', 'helper')
        )
    );

-- Users can update their responses to check-ins
CREATE POLICY wellness_check_ins_update_policy ON wellness_check_ins
    FOR UPDATE USING (
        user_id = current_setting('app.current_user_id')::UUID 
        OR EXISTS (
            SELECT 1 FROM users 
            WHERE id = current_setting('app.current_user_id')::UUID 
            AND role IN ('admin', 'moderator', 'helper')
        )
    );

-- Escalation Protocols Policies (admin/moderator only)
CREATE POLICY escalation_protocols_select_policy ON escalation_protocols
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id = current_setting('app.current_user_id')::UUID 
            AND role IN ('admin', 'moderator', 'helper')
        )
    );

CREATE POLICY escalation_protocols_insert_policy ON escalation_protocols
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id = current_setting('app.current_user_id')::UUID 
            AND role IN ('admin', 'moderator')
        )
    );

-- Crisis Intervention Queue Policies (professionals and admins only)
CREATE POLICY intervention_queue_select_policy ON crisis_intervention_queue
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id = current_setting('app.current_user_id')::UUID 
            AND role IN ('admin', 'moderator', 'helper')
        )
    );

CREATE POLICY intervention_queue_insert_policy ON crisis_intervention_queue
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id = current_setting('app.current_user_id')::UUID 
            AND role IN ('admin', 'moderator', 'helper')
        )
    );

-- Create updated_at triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_crisis_alerts_updated_at
    BEFORE UPDATE ON crisis_detection_alerts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_safety_plans_updated_at
    BEFORE UPDATE ON safety_plans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_safety_templates_updated_at
    BEFORE UPDATE ON safety_plan_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_wellness_check_ins_updated_at
    BEFORE UPDATE ON wellness_check_ins
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_escalation_protocols_updated_at
    BEFORE UPDATE ON escalation_protocols
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_intervention_queue_updated_at
    BEFORE UPDATE ON crisis_intervention_queue
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions (following existing pattern)
GRANT SELECT, INSERT, UPDATE ON crisis_detection_alerts TO safe_zone_app_user;
GRANT SELECT, INSERT, UPDATE ON safety_plans TO safe_zone_app_user;
GRANT SELECT, INSERT, UPDATE ON safety_plan_templates TO safe_zone_app_user;
GRANT SELECT, INSERT, UPDATE ON wellness_check_ins TO safe_zone_app_user;
GRANT SELECT, INSERT, UPDATE ON escalation_protocols TO safe_zone_app_user;
GRANT SELECT, INSERT, UPDATE ON crisis_intervention_queue TO safe_zone_app_user;

GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO safe_zone_app_user;

-- Insert default safety plan templates
INSERT INTO safety_plan_templates (template_name, template_description, target_audience, default_warning_signs, default_coping_strategies, default_emergency_instructions, created_by) VALUES
('Basic Safety Plan', 'A general safety plan for managing difficult moments', 'general', 
 '{"Feeling overwhelmed", "Increased anxiety", "Difficulty sleeping", "Withdrawing from others"}',
 '{"Practice deep breathing", "Go for a walk", "Listen to calming music", "Reach out to a friend"}',
 'If you feel unsafe, contact a crisis line or trusted person immediately. Remove yourself from harmful situations.',
 (SELECT id FROM users WHERE role = 'admin' LIMIT 1)),
('Depression Management Plan', 'Safety plan specifically for managing depressive episodes', 'depression',
 '{"Loss of interest in activities", "Feeling hopeless", "Changes in sleep patterns", "Negative self-talk"}',
 '{"Engage in pleasant activities", "Challenge negative thoughts", "Practice self-compassion", "Connect with support system"}',
 'Reach out to your therapist or crisis support. Use your emergency contacts if needed.',
 (SELECT id FROM users WHERE role = 'admin' LIMIT 1)),
('Anxiety Coping Plan', 'Plan for managing anxiety and panic symptoms', 'anxiety',
 '{"Racing thoughts", "Physical tension", "Avoiding situations", "Difficulty breathing"}',
 '{"Grounding techniques", "Progressive muscle relaxation", "Mindful breathing", "Use coping statements"}',
 'If experiencing panic, focus on breathing. Contact support if symptoms persist.',
 (SELECT id FROM users WHERE role = 'admin' LIMIT 1))
ON CONFLICT DO NOTHING;

-- Insert default escalation protocols
INSERT INTO escalation_protocols (protocol_name, trigger_risk_level, trigger_conditions, immediate_actions, follow_up_actions, professional_involvement_required) VALUES
('Moderate Risk Protocol', 'medium', '{"risk_score": 0.4, "risk_factors": ["isolation", "mood_changes"]}',
 '{"Send wellness check-in", "Suggest coping strategies", "Monitor user activity"}',
 '{"Follow up in 24 hours", "Review safety plan", "Check resource utilization"}', false),
('High Risk Protocol', 'high', '{"risk_score": 0.7, "risk_factors": ["suicidal_ideation", "self_harm_risk"]}',
 '{"Immediate moderator review", "Send crisis resources", "Check emergency contacts"}',
 '{"Assign to intervention queue", "Contact within 2 hours", "Safety plan review"}', true),
('Critical Risk Protocol', 'critical', '{"risk_score": 0.9, "risk_factors": ["imminent_risk", "active_crisis"]}',
 '{"Immediate professional intervention", "Emergency contact notification", "Crisis line referral"}',
 '{"Continuous monitoring", "Professional follow-up", "Safety plan implementation"}', true)
ON CONFLICT DO NOTHING;

