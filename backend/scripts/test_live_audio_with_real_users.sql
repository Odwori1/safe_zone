-- TEST LIVE AUDIO ROOMS WITH REAL USERS
-- Using existing users from the system

-- 1. Get a real user ID from the users table
DO $$
DECLARE
    test_user_id UUID;
BEGIN
    -- Get first available user
    SELECT id INTO test_user_id FROM users LIMIT 1;
    
    IF test_user_id IS NOT NULL THEN
        -- Set user context
        PERFORM set_config('app.current_user_id', test_user_id::text, true);
        
        -- Create test room with real user
        INSERT INTO live_audio_rooms (title, created_by, is_active, is_public)
        VALUES ('Test Audio Room', test_user_id, true, true)
        RETURNING id, title, created_by;
        
        RAISE NOTICE 'Room created successfully with user: %', test_user_id;
    ELSE
        RAISE NOTICE 'No users found in the system';
    END IF;
END $$;
