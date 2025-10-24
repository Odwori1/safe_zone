-- Advanced Safety Systems Schema for Phase 4, Item 2 - FIXED VERSION
-- Building upon existing crisis_resources, emergency_contacts, and user_crisis_preferences

-- First, create the safety_plans table with corrected syntax
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
    updated_at TIMESTAMPTZ DEFAULT NOW()

    -- Note: Removed problematic UNIQUE constraint for simplicity
    -- Application logic will handle one active plan per user
);

-- Create partial unique index instead of constraint
CREATE UNIQUE INDEX IF NOT EXISTS idx_safety_plans_one_active 
ON safety_plans (user_id) 
WHERE is_active = true;

-- Enable RLS on safety_plans
ALTER TABLE safety_plans ENABLE ROW LEVEL SECURITY;

-- Safety Plans Policies
-- Users can only see and manage their own safety plans
CREATE POLICY safety_plans_select_policy ON safety_plans
    FOR SELECT USING (user_id = current_setting('app.current_user_id')::UUID);

CREATE POLICY safety_plans_insert_policy ON safety_plans
    FOR INSERT WITH CHECK (user_id = current_setting('app.current_user_id')::UUID);

CREATE POLICY safety_plans_update_policy ON safety_plans
    FOR UPDATE USING (user_id = current_setting('app.current_user_id')::UUID);

-- Create updated_at trigger for safety_plans
CREATE TRIGGER update_safety_plans_updated_at
    BEFORE UPDATE ON safety_plans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions for safety_plans
GRANT SELECT, INSERT, UPDATE ON safety_plans TO safe_zone_app_user;

-- Insert default safety plan templates if not already inserted
INSERT INTO safety_plan_templates (template_name, template_description, target_audience, default_warning_signs, default_coping_strategies, default_emergency_instructions, created_by) VALUES
('Basic Safety Plan', 'A general safety plan for managing difficult moments', 'general', 
 '{"Feeling overwhelmed", "Increased anxiety", "Difficulty sleeping", "Withdrawing from others"}',
 '{"Practice deep breathing", "Go for a walk", "Listen to calming music", "Reach out to a friend"}',
 'If you feel unsafe, contact a crisis line or trusted person immediately. Remove yourself from harmful situations.',
 (SELECT id FROM users WHERE role = 'admin' LIMIT 1))
ON CONFLICT DO NOTHING;

-- Verify all tables are properly set up
SELECT 
    tablename, 
    rowsecurity,
    (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_name = tablename) as exists
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN (
    'crisis_detection_alerts',
    'safety_plans', 
    'safety_plan_templates',
    'wellness_check_ins',
    'escalation_protocols',
    'crisis_intervention_queue'
);
