-- Secure File Metadata Table Migration for Phase 3, Item 3
-- Following security-first blueprint with RLS and user isolation

-- Create the secure file_metadata table
CREATE TABLE IF NOT EXISTS file_metadata (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
    s3_key TEXT NOT NULL,
    file_type VARCHAR(20) NOT NULL CHECK (file_type IN ('video', 'audio', 'image')),
    original_filename TEXT NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    duration INTEGER,
    upload_status VARCHAR(20) DEFAULT 'pending' CHECK (upload_status IN ('pending', 'completed', 'failed')),
    moderation_status VARCHAR(20) DEFAULT 'pending' CHECK (moderation_status IN ('pending', 'approved', 'rejected', 'flagged')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Security constraints
    CONSTRAINT valid_s3_key CHECK (s3_key LIKE 'users/%'),
    CONSTRAINT max_file_size CHECK (file_size <= 500 * 1024 * 1024),  -- 500MB limit
    CONSTRAINT positive_file_size CHECK (file_size > 0)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_file_metadata_user_id ON file_metadata(user_id);
CREATE INDEX IF NOT EXISTS idx_file_metadata_post_id ON file_metadata(post_id);
CREATE INDEX IF NOT EXISTS idx_file_metadata_upload_status ON file_metadata(upload_status);
CREATE INDEX IF NOT EXISTS idx_file_metadata_s3_key ON file_metadata(s3_key);

-- CRITICAL: Enable Row Level Security (RLS) like Phase 1
ALTER TABLE file_metadata ENABLE ROW LEVEL SECURITY;

-- CRITICAL: Create RLS policies for user isolation
CREATE POLICY file_metadata_isolation_policy ON file_metadata
    FOR ALL USING (user_id = current_setting('app.current_user_id')::uuid);

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_file_metadata_updated_at 
    BEFORE UPDATE ON file_metadata 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Migration: Copy existing file_uploads data to file_metadata (if needed)
-- Note: This is a placeholder for future migration if required
