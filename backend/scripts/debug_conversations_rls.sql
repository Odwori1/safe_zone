-- Debug conversations RLS policies
-- Run this as postgres user

\c safe_zone;

-- Check if RLS is enabled on conversations
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE tablename = 'conversations';

-- List all policies on conversations
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check
FROM pg_policies 
WHERE tablename = 'conversations';

-- Check if there are any other policies that might be interfering
SELECT schemaname, tablename, policyname 
FROM pg_policies 
WHERE tablename IN ('conversations', 'conversation_participants', 'messages');

-- Let's also check if there are any triggers that might be causing issues
SELECT tgname, tgrelid::regclass, tgfoid::regproc, tgtype, tgenabled
FROM pg_trigger 
WHERE tgrelid = 'conversations'::regclass;
