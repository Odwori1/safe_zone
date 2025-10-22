-- FIX MISSING app.current_user_id CONFIGURATION
-- This is the root cause of UUID parsing errors

-- 1. Set the configuration parameter with proper default
ALTER DATABASE safe_zone SET app.current_user_id = '00000000-0000-0000-0000-000000000000';

-- 2. Verify it exists now
SELECT name, setting, context 
FROM pg_settings 
WHERE name = 'app.current_user_id';

-- 3. Test that it works
SELECT current_setting('app.current_user_id', true) as current_value;

-- 4. Test RLS with the configuration
SET app.current_user_id TO '00000000-0000-0000-0000-000000000000';
SELECT current_setting('app.current_user_id', true) as test_value;
