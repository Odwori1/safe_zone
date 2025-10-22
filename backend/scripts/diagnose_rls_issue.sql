-- Check if RLS is enabled and policies are working
SELECT 
    tablename, 
    rowsecurity as rls_enabled,
    (SELECT count(*) FROM pg_policies WHERE tablename = p.tablename) as policy_count
FROM pg_tables p
WHERE tablename IN ('conversations', 'conversation_participants', 'messages');

-- Test RLS with a simple query
\echo '=== Testing RLS Enforcement ==='

-- Create a test scenario
DO $$ 
DECLARE
    test_conv_id UUID;
    user1_id UUID := 'd31ce60e-e013-44a9-97e3-dda4ee30d6d2';
    user2_id UUID := '11111111-1111-1111-1111-111111111111';
BEGIN
    -- Set user1 context and create conversation
    PERFORM set_config('app.current_user_id', user1_id::text, true);
    
    INSERT INTO conversations (is_group, title) VALUES (false, 'RLS Test') 
    RETURNING id INTO test_conv_id;
    
    INSERT INTO conversation_participants (conversation_id, user_id) 
    VALUES (test_conv_id, user1_id);
    
    RAISE NOTICE 'Created conversation: %', test_conv_id;
    
    -- Switch to user2 context
    PERFORM set_config('app.current_user_id', user2_id::text, true);
    
    -- Test if user2 can see the conversation (should return 0 rows)
    IF EXISTS (SELECT 1 FROM conversations WHERE id = test_conv_id) THEN
        RAISE NOTICE '❌ RLS FAILED: User2 can see conversation';
    ELSE
        RAISE NOTICE '✅ RLS WORKING: User2 cannot see conversation';
    END IF;
    
    -- Test if user2 can insert into participants (should fail)
    BEGIN
        INSERT INTO conversation_participants (conversation_id, user_id) 
        VALUES (test_conv_id, user2_id);
        RAISE NOTICE '❌ RLS FAILED: User2 inserted into participants';
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE '✅ RLS WORKING: User2 cannot insert into participants';
    END;
    
    -- Cleanup
    PERFORM set_config('app.current_user_id', user1_id::text, true);
    DELETE FROM conversations WHERE id = test_conv_id;
END $$;
