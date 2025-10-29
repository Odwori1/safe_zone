-- Create post_likes table for like functionality
-- This follows the same pattern as other table creations in the system

CREATE TABLE IF NOT EXISTS post_likes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(post_id, user_id)
);

-- Enable RLS (following existing pattern)
ALTER TABLE post_likes ENABLE ROW LEVEL SECURITY;

-- Create RLS policies following the same pattern as other tables

-- Policy: Users can see all likes (same visibility as posts)
CREATE POLICY "Users can view all likes" ON post_likes
    FOR SELECT USING (true);

-- Policy: Users can only insert their own likes  
CREATE POLICY "Users can insert their own likes" ON post_likes
    FOR INSERT WITH CHECK (user_id = current_setting('app.current_user_id')::uuid);

-- Policy: Users can only delete their own likes
CREATE POLICY "Users can delete their own likes" ON post_likes
    FOR DELETE USING (user_id = current_setting('app.current_user_id')::uuid);

-- Add index for better performance on common queries
CREATE INDEX IF NOT EXISTS idx_post_likes_post_id ON post_likes(post_id);
CREATE INDEX IF NOT EXISTS idx_post_likes_user_id ON post_likes(user_id);
CREATE INDEX IF NOT EXISTS idx_post_likes_created_at ON post_likes(created_at);

-- Verify table creation
COMMENT ON TABLE post_likes IS 'Stores post likes for social interactions';
