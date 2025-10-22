-- FIX RLS OWNERSHIP ISSUE
-- This script creates a dedicated application user without table ownership

-- 1. Create a new dedicated application user
CREATE USER safe_zone_app_user WITH PASSWORD 'secure_app_password_2024';
GRANT CONNECT ON DATABASE safe_zone TO safe_zone_app_user;

-- 2. Grant usage on schema
GRANT USAGE ON SCHEMA public TO safe_zone_app_user;

-- 3. Grant permissions on all tables (but NOT ownership)
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO safe_zone_app_user;

-- 4. Grant usage on sequences
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO safe_zone_app_user;

-- 5. Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO safe_zone_app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE ON SEQUENCES TO safe_zone_app_user;

-- 6. Update application configuration to use new user
--    Change in .env: DB_USER=safe_zone_app_user
--    Change password accordingly

-- 7. Verify the new user cannot bypass RLS
--    Run: psql -h 127.0.0.1 -p 5433 -d safe_zone -U safe_zone_app_user -c "SELECT current_user;"

-- Note: This is the PROPER way to set up RLS - application user should not own tables
