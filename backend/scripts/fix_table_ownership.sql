-- Fix RLS by changing table ownership to a dedicated owner
-- Table owners automatically bypass RLS, so we need a different owner

-- Create a dedicated owner user (if not exists)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'safe_zone_owner') THEN
        CREATE USER safe_zone_owner WITH PASSWORD 'secure_owner_password_123';
    END IF;
END $$;

-- Grant necessary privileges
GRANT CONNECT ON DATABASE safe_zone TO safe_zone_owner;
GRANT USAGE ON SCHEMA public TO safe_zone_owner;

-- Change table ownership to break RLS bypass
ALTER TABLE conversations OWNER TO safe_zone_owner;
ALTER TABLE conversation_participants OWNER TO safe_zone_owner;
ALTER TABLE messages OWNER TO safe_zone_owner;
ALTER TABLE websocket_sessions OWNER TO safe_zone_owner;

-- Grant permissions back to safe_zone_user (but not ownership)
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO safe_zone_user;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO safe_zone_user;

-- Verify ownership changed
SELECT 
    tablename,
    tableowner
FROM pg_tables 
WHERE tablename IN ('conversations', 'conversation_participants', 'messages', 'websocket_sessions');
