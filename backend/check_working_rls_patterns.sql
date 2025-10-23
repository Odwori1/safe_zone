-- Check RLS policies from working tables to understand the correct pattern
SELECT tablename, policyname, cmd, qual, with_check 
FROM pg_policies 
WHERE tablename IN ('conversation_participants', 'messages', 'posts', 'comments')
ORDER BY tablename, policyname;
