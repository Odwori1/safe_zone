-- Verify RLS policies after fixes
SELECT 
    tablename, 
    policyname, 
    cmd,
    CASE 
        WHEN qual IS NOT NULL THEN 'HAS_QUAL'
        ELSE 'NO_QUAL'
    END as qual_status,
    CASE
        WHEN with_check IS NOT NULL THEN 'HAS_CHECK'
        ELSE 'NO_CHECK' 
    END as check_status
FROM pg_policies 
WHERE tablename IN ('conversations', 'conversation_participants', 'messages')
ORDER BY tablename, policyname;
