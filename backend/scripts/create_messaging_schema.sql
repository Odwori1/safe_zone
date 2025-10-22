-- Secure Messaging Schema for Phase 3, Item 4
-- Following security-first blueprint with RLS protection

-- Conversations table (participants list)
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    is_group BOOLEAN NOT NULL DEFAULT false,
    title TEXT,  -- Optional group chat title
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Conversation participants table
CREATE TABLE IF NOT EXISTS conversation_participants (
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    role TEXT DEFAULT 'member',
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (conversation_id, user_id)
);

-- Messages table
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    sender_id UUID NOT NULL,
    content TEXT,
    content_type TEXT NOT NULL DEFAULT 'text', -- 'text','audio','video','file'
    file_metadata_id UUID REFERENCES file_metadata(id), -- Reference to uploaded files
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted BOOLEAN DEFAULT false,
    moderated BOOLEAN DEFAULT false,
    moderation_status TEXT DEFAULT 'pending' -- 'pending', 'approved', 'rejected'
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_conversation_participants_user_id ON conversation_participants(user_id);
CREATE INDEX IF NOT EXISTS idx_conversation_participants_conversation_id ON conversation_participants(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_sender_id ON messages(sender_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);
CREATE INDEX IF NOT EXISTS idx_messages_moderation_status ON messages(moderation_status);

-- CRITICAL: Enable Row Level Security (RLS) on all tables
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_participants ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- CRITICAL: RLS Policies for conversations
-- Users can only see conversations they are participants in
CREATE POLICY conversations_select_policy ON conversations
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM conversation_participants cp
            WHERE cp.conversation_id = conversations.id
            AND cp.user_id = current_setting('app.current_user_id')::UUID
        )
    );

-- CRITICAL: RLS Policies for conversation_participants  
-- Users can only see participants in conversations they belong to
CREATE POLICY conversation_participants_select_policy ON conversation_participants
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM conversation_participants cp
            WHERE cp.conversation_id = conversation_participants.conversation_id
            AND cp.user_id = current_setting('app.current_user_id')::UUID
        )
    );

-- Users can only insert themselves into conversations (with proper validation)
CREATE POLICY conversation_participants_insert_policy ON conversation_participants
    FOR INSERT WITH CHECK (user_id = current_setting('app.current_user_id')::UUID);

-- CRITICAL: RLS Policies for messages
-- Users can only see messages from conversations they are participants in
CREATE POLICY messages_select_policy ON messages
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM conversation_participants cp
            WHERE cp.conversation_id = messages.conversation_id
            AND cp.user_id = current_setting('app.current_user_id')::UUID
        )
    );

-- Users can only insert messages where they are the sender AND participants
CREATE POLICY messages_insert_policy ON messages
    FOR INSERT WITH CHECK (
        sender_id = current_setting('app.current_user_id')::UUID
        AND EXISTS (
            SELECT 1 FROM conversation_participants cp
            WHERE cp.conversation_id = messages.conversation_id
            AND cp.user_id = current_setting('app.current_user_id')::UUID
        )
    );

-- Users can only update their own messages (for soft delete)
CREATE POLICY messages_update_policy ON messages
    FOR UPDATE USING (sender_id = current_setting('app.current_user_id')::UUID);

-- Create updated_at triggers (consistent with existing patterns)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_conversations_updated_at
    BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_messages_updated_at
    BEFORE UPDATE ON messages
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
