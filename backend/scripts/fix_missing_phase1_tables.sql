-- =============================================
-- FIX MISSING PHASE 1 & 2 TABLES
-- =============================================

-- ===== PHASE 1: Missing Tables =====

-- 1. Password Reset Tokens
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash TEXT NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Reactions Table (for post reactions)
CREATE TABLE IF NOT EXISTS reactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    reaction_type VARCHAR(20) NOT NULL CHECK (reaction_type IN ('heart', 'hug', 'star', 'lightbulb')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, post_id, reaction_type)
);

-- 3. Saved Posts Table
CREATE TABLE IF NOT EXISTS saved_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, post_id)
);

-- ===== PHASE 2: Circles System =====

-- 4. Circles Table (Themed communities)
CREATE TABLE IF NOT EXISTS circles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    topic VARCHAR(50) NOT NULL, -- Anxiety, Parenting, PTSD, etc.
    is_public BOOLEAN DEFAULT TRUE,
    allow_anonymous_posts BOOLEAN DEFAULT FALSE,
    moderator_id UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Circle Members Table
CREATE TABLE IF NOT EXISTS circle_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    circle_id UUID NOT NULL REFERENCES circles(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) DEFAULT 'member' CHECK (role IN ('member', 'moderator')),
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(circle_id, user_id)
);

-- 6. Circle Posts Table
CREATE TABLE IF NOT EXISTS circle_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    circle_id UUID NOT NULL REFERENCES circles(id) ON DELETE CASCADE,
    post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    is_anonymous BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(circle_id, post_id)
);

-- ===== ENABLE ROW LEVEL SECURITY =====
ALTER TABLE password_reset_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE reactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE saved_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE circles ENABLE ROW LEVEL SECURITY;
ALTER TABLE circle_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE circle_posts ENABLE ROW LEVEL SECURITY;

-- ===== CREATE RLS POLICIES =====

-- Password Reset Tokens: Users can only see their own tokens
CREATE POLICY password_reset_tokens_user_policy ON password_reset_tokens
    FOR ALL USING (user_id = current_setting('app.current_user_id')::UUID);

-- Reactions: Users can see all reactions but only modify their own
CREATE POLICY reactions_read_policy ON reactions
    FOR SELECT USING (true);
CREATE POLICY reactions_write_policy ON reactions
    FOR ALL USING (user_id = current_setting('app.current_user_id')::UUID);

-- Saved Posts: Users can only see their own saved posts
CREATE POLICY saved_posts_user_policy ON saved_posts
    FOR ALL USING (user_id = current_setting('app.current_user_id')::UUID);

-- Circles: Public read, members can post
CREATE POLICY circles_read_policy ON circles
    FOR SELECT USING (is_public = true OR 
                     EXISTS (SELECT 1 FROM circle_members 
                             WHERE circle_id = circles.id 
                             AND user_id = current_setting('app.current_user_id')::UUID));
CREATE POLICY circles_write_policy ON circles
    FOR ALL USING (EXISTS (SELECT 1 FROM users 
                          WHERE id = current_setting('app.current_user_id')::UUID 
                          AND role IN ('admin', 'moderator')));

-- Circle Members: Users can see members of circles they belong to
CREATE POLICY circle_members_read_policy ON circle_members
    FOR SELECT USING (EXISTS (SELECT 1 FROM circle_members cm2 
                             WHERE cm2.circle_id = circle_members.circle_id 
                             AND cm2.user_id = current_setting('app.current_user_id')::UUID));
CREATE POLICY circle_members_write_policy ON circle_members
    FOR ALL USING (user_id = current_setting('app.current_user_id')::UUID OR
                  EXISTS (SELECT 1 FROM circles 
                          WHERE id = circle_members.circle_id 
                          AND moderator_id = current_setting('app.current_user_id')::UUID));

-- Circle Posts: Users can see posts in circles they belong to
CREATE POLICY circle_posts_read_policy ON circle_posts
    FOR SELECT USING (EXISTS (SELECT 1 FROM circle_members 
                             WHERE circle_id = circle_posts.circle_id 
                             AND user_id = current_setting('app.current_user_id')::UUID));
CREATE POLICY circle_posts_write_policy ON circle_posts
    FOR ALL USING (EXISTS (SELECT 1 FROM circle_members 
                          WHERE circle_id = circle_posts.circle_id 
                          AND user_id = current_setting('app.current_user_id')::UUID));

-- ===== CREATE INDEXES FOR PERFORMANCE =====
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_user_id ON password_reset_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_token_hash ON password_reset_tokens(token_hash);
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_expires_at ON password_reset_tokens(expires_at);

CREATE INDEX IF NOT EXISTS idx_reactions_user_id ON reactions(user_id);
CREATE INDEX IF NOT EXISTS idx_reactions_post_id ON reactions(post_id);
CREATE INDEX IF NOT EXISTS idx_reactions_type ON reactions(reaction_type);

CREATE INDEX IF NOT EXISTS idx_saved_posts_user_id ON saved_posts(user_id);
CREATE INDEX IF NOT EXISTS idx_saved_posts_post_id ON saved_posts(post_id);

CREATE INDEX IF NOT EXISTS idx_circles_topic ON circles(topic);
CREATE INDEX IF NOT EXISTS idx_circles_moderator_id ON circles(moderator_id);
CREATE INDEX IF NOT EXISTS idx_circles_is_public ON circles(is_public);

CREATE INDEX IF NOT EXISTS idx_circle_members_circle_id ON circle_members(circle_id);
CREATE INDEX IF NOT EXISTS idx_circle_members_user_id ON circle_members(user_id);
CREATE INDEX IF NOT EXISTS idx_circle_members_role ON circle_members(role);

CREATE INDEX IF NOT EXISTS idx_circle_posts_circle_id ON circle_posts(circle_id);
CREATE INDEX IF NOT EXISTS idx_circle_posts_post_id ON circle_posts(post_id);

-- ===== INSERT SAMPLE CIRCLES =====
INSERT INTO circles (name, description, topic, is_public, allow_anonymous_posts) VALUES
('Anxiety Support', 'A safe space for those dealing with anxiety disorders', 'Anxiety', true, true),
('Depression Help', 'Support and resources for managing depression', 'Depression', true, true),
('PTSD Recovery', 'Community for PTSD survivors and their supporters', 'PTSD', true, false),
('Parenting Mental Health', 'Mental health support for parents and caregivers', 'Parenting', true, true),
('Workplace Wellness', 'Managing mental health in professional settings', 'Workplace', true, false),
('Student Mental Health', 'Support for students navigating academic pressures', 'Students', true, true)
ON CONFLICT DO NOTHING;
