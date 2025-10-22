-- Secure WebSocket Sessions Table for Phase 3, Item 4
-- Following security-first blueprint with RLS protection

CREATE TABLE IF NOT EXISTS websocket_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    connected_at TIMESTAMPTZ DEFAULT NOW(),
    disconnected_at TIMESTAMPTZ,
    last_activity TIMESTAMPTZ DEFAULT NOW(),
    client_info TEXT,  -- Optional: store client details for audit
    is_active BOOLEAN DEFAULT true
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_websocket_sessions_user_id ON websocket_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_websocket_sessions_active ON websocket_sessions(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_websocket_sessions_activity ON websocket_sessions(last_activity);

-- CRITICAL: Enable Row Level Security (RLS) like Phase 1
ALTER TABLE websocket_sessions ENABLE ROW LEVEL SECURITY;

-- CRITICAL: Create RLS policies for user isolation
CREATE POLICY websocket_sessions_isolation_policy ON websocket_sessions
    FOR ALL USING (user_id = current_setting('app.current_user_id')::uuid);

-- Create updated_at trigger (consistent with existing patterns)
CREATE OR REPLACE FUNCTION update_websocket_session_activity()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_activity = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_websocket_session_activity
    BEFORE UPDATE ON websocket_sessions
    FOR EACH ROW EXECUTE FUNCTION update_websocket_session_activity();
