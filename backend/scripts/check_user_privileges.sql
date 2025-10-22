-- Check current user RLS bypass privileges
SELECT 
    usename,
    usesuper as is_superuser,
    usebypassrls as can_bypass_rls
FROM pg_user 
WHERE usename = current_user;

-- Check table ownership
SELECT 
    tablename,
    tableowner
FROM pg_tables 
WHERE tablename IN ('conversations', 'conversation_participants', 'messages');
