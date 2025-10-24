-- AI Personalization Schema for Phase 4, Item 1
-- Following EXACT same patterns as professional_directory_schema_fixed.sql

-- AI Content Analysis Table
CREATE TABLE IF NOT EXISTS ai_content_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_type VARCHAR(50) NOT NULL, -- 'post', 'comment', 'journal'
    content_id UUID NOT NULL,
    
    -- Sentiment Analysis
    sentiment_score DECIMAL(3,2), -- -1.0 to 1.0
    sentiment_label VARCHAR(20), -- 'positive', 'negative', 'neutral'
    emotion_tags TEXT[], -- ['anxiety', 'depression', 'hope', 'gratitude']
    
    -- Content Classification
    content_categories TEXT[], -- ['support_request', 'achievement', 'reflection']
    risk_level VARCHAR(20), -- 'low', 'medium', 'high', 'crisis'
    toxicity_score DECIMAL(3,2), -- 0.0 to 1.0
    
    -- AI Metadata
    analysis_model VARCHAR(100),
    confidence_score DECIMAL(3,2),
    analysis_timestamp TIMESTAMPTZ DEFAULT NOW(),
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Unique constraint per content
    UNIQUE(content_type, content_id)
);

-- User Behavior Patterns Table
CREATE TABLE IF NOT EXISTS user_behavior_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Mood Patterns
    avg_mood_score DECIMAL(3,2),
    mood_volatility DECIMAL(3,2),
    common_mood_patterns TEXT[], -- ['morning_low', 'evening_high']
    weekly_rhythm JSONB, -- Day-of-week patterns
    
    -- Activity Patterns
    posting_frequency_daily DECIMAL(5,2),
    active_hours TEXT[], -- ['morning', 'afternoon', 'evening']
    engagement_level VARCHAR(20), -- 'low', 'medium', 'high'
    
    -- Content Preferences
    preferred_content_types TEXT[], -- ['text', 'audio', 'video']
    interested_topics TEXT[], -- ['anxiety', 'relationships', 'work']
    
    -- Pattern Metadata
    pattern_confidence DECIMAL(3,2),
    last_analysis_date DATE DEFAULT CURRENT_DATE,
    analysis_period_days INTEGER DEFAULT 30,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- One pattern analysis per user
    UNIQUE(user_id)
);

-- Personalized Recommendations Table
CREATE TABLE IF NOT EXISTS personalized_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Recommendation Details
    recommendation_type VARCHAR(50) NOT NULL, -- 'content', 'wellness', 'community', 'professional'
    title VARCHAR(200) NOT NULL,
    description TEXT,
    reasoning TEXT, -- AI explanation for the recommendation
    
    -- Content Reference (if applicable)
    content_type VARCHAR(50), -- 'post', 'resource', 'professional'
    content_id UUID,
    
    -- Recommendation Metrics
    relevance_score DECIMAL(3,2),
    confidence_score DECIMAL(3,2),
    priority_level VARCHAR(20) DEFAULT 'medium', -- 'low', 'medium', 'high', 'urgent'
    
    -- User Interaction
    is_dismissed BOOLEAN DEFAULT false,
    is_completed BOOLEAN DEFAULT false,
    user_feedback VARCHAR(20), -- 'helpful', 'not_helpful', 'neutral'
    feedback_notes TEXT,
    
    -- Timing and Expiration
    recommended_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    optimal_viewing_time TIME, -- Personalized timing
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Coping Strategies Table
CREATE TABLE IF NOT EXISTS coping_strategies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Strategy Details
    strategy_name VARCHAR(200) NOT NULL,
    strategy_type VARCHAR(50) NOT NULL, -- 'breathing', 'mindfulness', 'physical', 'social', 'cognitive'
    description TEXT NOT NULL,
    instructions TEXT,
    duration_minutes INTEGER,
    
    -- Target Conditions
    target_emotions TEXT[], -- ['anxiety', 'sadness', 'anger', 'stress']
    target_intensity VARCHAR(20), -- 'low', 'medium', 'high'
    effectiveness_score DECIMAL(3,2),
    
    -- Accessibility
    difficulty_level VARCHAR(20) DEFAULT 'beginner', -- 'beginner', 'intermediate', 'advanced'
    requires_resources BOOLEAN DEFAULT false,
    resources_description TEXT,
    
    -- Metadata
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- User Coping Strategy Preferences Table
CREATE TABLE IF NOT EXISTS user_coping_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    strategy_id UUID NOT NULL REFERENCES coping_strategies(id) ON DELETE CASCADE,
    
    -- User Preferences
    preference_score DECIMAL(3,2) DEFAULT 0.5, -- 0.0 to 1.0
    effectiveness_rating INTEGER CHECK (effectiveness_rating BETWEEN 1 AND 5),
    last_used_at TIMESTAMPTZ,
    usage_count INTEGER DEFAULT 0,
    
    -- AI Learning
    ai_recommendation_score DECIMAL(3,2),
    context_tags TEXT[], -- ['morning', 'work', 'home', 'social']
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- One preference record per user-strategy combination
    UNIQUE(user_id, strategy_id)
);

-- Notification Preferences Table
CREATE TABLE IF NOT EXISTS notification_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Timing Preferences
    optimal_morning_time TIME DEFAULT '09:00',
    optimal_afternoon_time TIME DEFAULT '14:00', 
    optimal_evening_time TIME DEFAULT '19:00',
    quiet_hours_start TIME DEFAULT '22:00',
    quiet_hours_end TIME DEFAULT '07:00',
    timezone VARCHAR(50) DEFAULT 'UTC',
    
    -- Content Preferences
    receive_mood_insights BOOLEAN DEFAULT true,
    receive_wellness_tips BOOLEAN DEFAULT true,
    receive_community_updates BOOLEAN DEFAULT true,
    receive_professional_suggestions BOOLEAN DEFAULT true,
    
    -- Delivery Preferences
    preferred_notification_types TEXT[] DEFAULT '{"push", "in_app"}',
    max_daily_notifications INTEGER DEFAULT 5,
    
    -- AI Personalization
    mood_based_timing BOOLEAN DEFAULT true,
    engagement_based_frequency BOOLEAN DEFAULT true,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- One preference set per user
    UNIQUE(user_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_ai_content_analysis_content ON ai_content_analysis(content_type, content_id);
CREATE INDEX IF NOT EXISTS idx_ai_content_analysis_sentiment ON ai_content_analysis(sentiment_score);
CREATE INDEX IF NOT EXISTS idx_ai_content_analysis_risk ON ai_content_analysis(risk_level);
CREATE INDEX IF NOT EXISTS idx_user_behavior_patterns_user ON user_behavior_patterns(user_id);
CREATE INDEX IF NOT EXISTS idx_personalized_recommendations_user ON personalized_recommendations(user_id);
CREATE INDEX IF NOT EXISTS idx_personalized_recommendations_type ON personalized_recommendations(recommendation_type);
CREATE INDEX IF NOT EXISTS idx_personalized_recommendations_priority ON personalized_recommendations(priority_level);
CREATE INDEX IF NOT EXISTS idx_coping_strategies_type ON coping_strategies(strategy_type);
CREATE INDEX IF NOT EXISTS idx_coping_strategies_emotions ON coping_strategies(target_emotions);
CREATE INDEX IF NOT EXISTS idx_user_coping_preferences_user ON user_coping_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_user_coping_preferences_score ON user_coping_preferences(preference_score);
CREATE INDEX IF NOT EXISTS idx_notification_preferences_user ON notification_preferences(user_id);

-- Enable RLS on all tables
ALTER TABLE ai_content_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_behavior_patterns ENABLE ROW LEVEL SECURITY;
ALTER TABLE personalized_recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE coping_strategies ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_coping_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE notification_preferences ENABLE ROW LEVEL SECURITY;

-- RLS Policies - FOLLOWING EXACT SAME SECURITY PATTERN

-- AI Content Analysis Policies
-- Users can see analysis of content they have access to
CREATE POLICY ai_content_analysis_select_policy ON ai_content_analysis
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM posts p 
            WHERE p.id = content_id AND content_type = 'post'
            AND (p.user_id = current_setting('app.current_user_id')::UUID OR p.visibility = 'public')
        )
        OR EXISTS (
            SELECT 1 FROM comments c 
            WHERE c.id = content_id AND content_type = 'comment'  
            AND c.user_id = current_setting('app.current_user_id')::UUID
        )
        OR EXISTS (
            SELECT 1 FROM users 
            WHERE id = current_setting('app.current_user_id')::UUID 
            AND role IN ('admin', 'moderator')
        )
    );

-- Only AI system and admins can insert/update analysis
CREATE POLICY ai_content_analysis_insert_policy ON ai_content_analysis
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id = current_setting('app.current_user_id')::UUID 
            AND role IN ('admin', 'moderator')
        )
    );

-- User Behavior Patterns Policies
-- Users can only see their own patterns
CREATE POLICY user_behavior_patterns_select_policy ON user_behavior_patterns
    FOR SELECT USING (user_id = current_setting('app.current_user_id')::UUID);

-- Only AI system can insert/update patterns
CREATE POLICY user_behavior_patterns_insert_policy ON user_behavior_patterns
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id = current_setting('app.current_user_id')::UUID 
            AND role IN ('admin', 'moderator')
        )
    );

-- Personalized Recommendations Policies  
-- Users can only see their own recommendations
CREATE POLICY personalized_recommendations_select_policy ON personalized_recommendations
    FOR SELECT USING (user_id = current_setting('app.current_user_id')::UUID);

-- Users can update their interaction with recommendations
CREATE POLICY personalized_recommendations_update_policy ON personalized_recommendations
    FOR UPDATE USING (user_id = current_setting('app.current_user_id')::UUID);

-- Only AI system can insert recommendations
CREATE POLICY personalized_recommendations_insert_policy ON personalized_recommendations
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id = current_setting('app.current_user_id')::UUID 
            AND role IN ('admin', 'moderator')
        )
    );

-- Coping Strategies Policies (public read, admin write)
CREATE POLICY coping_strategies_select_policy ON coping_strategies
    FOR SELECT USING (is_active = true);

CREATE POLICY coping_strategies_insert_policy ON coping_strategies
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id = current_setting('app.current_user_id')::UUID 
            AND role IN ('admin', 'moderator')
        )
    );

-- User Coping Preferences Policies
-- Users can only see and manage their own preferences
CREATE POLICY user_coping_preferences_select_policy ON user_coping_preferences
    FOR SELECT USING (user_id = current_setting('app.current_user_id')::UUID);

CREATE POLICY user_coping_preferences_insert_policy ON user_coping_preferences
    FOR INSERT WITH CHECK (user_id = current_setting('app.current_user_id')::UUID);

CREATE POLICY user_coping_preferences_update_policy ON user_coping_preferences
    FOR UPDATE USING (user_id = current_setting('app.current_user_id')::UUID);

-- Notification Preferences Policies
-- Users can only see and manage their own preferences
CREATE POLICY notification_preferences_select_policy ON notification_preferences
    FOR SELECT USING (user_id = current_setting('app.current_user_id')::UUID);

CREATE POLICY notification_preferences_insert_policy ON notification_preferences
    FOR INSERT WITH CHECK (user_id = current_setting('app.current_user_id')::UUID);

CREATE POLICY notification_preferences_update_policy ON notification_preferences
    FOR UPDATE USING (user_id = current_setting('app.current_user_id')::UUID);

-- Create updated_at triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_ai_content_analysis_updated_at
    BEFORE UPDATE ON ai_content_analysis
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_behavior_patterns_updated_at
    BEFORE UPDATE ON user_behavior_patterns
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_personalized_recommendations_updated_at
    BEFORE UPDATE ON personalized_recommendations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_coping_strategies_updated_at
    BEFORE UPDATE ON coping_strategies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_coping_preferences_updated_at
    BEFORE UPDATE ON user_coping_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_notification_preferences_updated_at
    BEFORE UPDATE ON notification_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions (following existing pattern)
GRANT SELECT, INSERT, UPDATE ON ai_content_analysis TO safe_zone_app_user;
GRANT SELECT, INSERT, UPDATE ON user_behavior_patterns TO safe_zone_app_user;
GRANT SELECT, INSERT, UPDATE ON personalized_recommendations TO safe_zone_app_user;
GRANT SELECT, INSERT, UPDATE ON coping_strategies TO safe_zone_app_user;
GRANT SELECT, INSERT, UPDATE ON user_coping_preferences TO safe_zone_app_user;
GRANT SELECT, INSERT, UPDATE ON notification_preferences TO safe_zone_app_user;

GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO safe_zone_app_user;

-- Insert default coping strategies
INSERT INTO coping_strategies (strategy_name, strategy_type, description, instructions, duration_minutes, target_emotions, effectiveness_score, difficulty_level) VALUES
('Deep Breathing', 'breathing', 'Calm your nervous system with controlled breathing', 'Inhale for 4 seconds, hold for 4 seconds, exhale for 6 seconds. Repeat 5-10 times.', 5, '{"anxiety", "stress"}', 0.85, 'beginner'),
('5-4-3-2-1 Grounding', 'mindfulness', 'Use your senses to stay present in the moment', 'Name 5 things you can see, 4 things you can touch, 3 things you can hear, 2 things you can smell, 1 thing you can taste.', 3, '{"anxiety", "panic"}', 0.78, 'beginner'),
('Progressive Muscle Relaxation', 'physical', 'Release physical tension through systematic relaxation', 'Tense and then relax each muscle group from toes to head, holding tension for 5 seconds then releasing.', 10, '{"stress", "anxiety", "anger"}', 0.82, 'beginner'),
('Gratitude Journaling', 'cognitive', 'Shift focus to positive aspects of life', 'Write down 3 things you are grateful for today and why they matter to you.', 5, '{"sadness", "depression"}', 0.76, 'beginner'),
('Mindful Walking', 'physical', 'Combine movement with mindfulness practice', 'Walk slowly while paying attention to each step, your breathing, and the sensations in your body.', 10, '{"anxiety", "stress", "sadness"}', 0.71, 'beginner')
ON CONFLICT DO NOTHING;

