-- Fixed Direct RLS Test Script
-- Run this in psql to test RLS enforcement without message_type

\echo '🔍 TESTING RLS ENFORCEMENT DIRECTLY (FIXED)'
\echo '=========================================='

\echo ''
\echo '1. CURRENT USER CONTEXT:'
SELECT current_user, current_setting('app.current_user_id', true) as current_user_id;

\echo ''
\echo '2. CHECK MESSAGES TABLE STRUCTURE:'
\d messages

\echo ''
\echo '3. CREATE TEST USERS AND DATA:'

-- Create test users if they don't exist
INSERT INTO users (id, email, username, hashed_password, full_name, is_active)
VALUES 
    ('11111111-1111-1111-1111-111111111111'::uuid, 'test_user1_rls@example.com', 'testuser1_rls', 'fakehash1', 'Test User 1 RLS', true),
    ('22222222-2222-2222-2222-222222222222'::uuid, 'test_user2_rls@example.com', 'testuser2_rls', 'fakehash2', 'Test User 2 RLS', true),
    ('33333333-3333-3333-3333-333333333333'::uuid, 'test_user3_rls@example.com', 'testuser3_rls', 'fakehash3', 'Test User 3 RLS', true)
ON CONFLICT (email) DO NOTHING;

-- Create test conversation between user1 and user2
INSERT INTO conversations (id, title, created_at)
VALUES ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid, 'RLS Test Conversation', NOW())
ON CONFLICT DO NOTHING;

-- Add participants
INSERT INTO conversation_participants (conversation_id, user_id, joined_at)
VALUES 
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid, '11111111-1111-1111-1111-111111111111'::uuid, NOW()),
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid, '22222222-2222-2222-2222-222222222222'::uuid, NOW())
ON CONFLICT DO NOTHING;

-- Add test messages (without message_type)
INSERT INTO messages (id, conversation_id, sender_id, content, created_at)
VALUES 
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'::uuid, 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid, '11111111-1111-1111-1111-111111111111'::uuid, 'Hello from User 1 - RLS Test', NOW()),
    ('cccccccc-cccc-cccc-cccc-cccccccccccc'::uuid, 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid, '22222222-2222-2222-2222-222222222222'::uuid, 'Hello from User 2 - RLS Test', NOW())
ON CONFLICT DO NOTHING;

\echo ''
\echo '4. TEST RLS AS USER 1 (PARTICIPANT):'
SET app.current_user_id TO '11111111-1111-1111-1111-111111111111';

\echo 'Conversations User 1 can see (SHOULD SEE 1):'
SELECT id, title FROM conversations;

\echo 'Messages User 1 can see (SHOULD SEE 2):'
SELECT id, sender_id, content FROM messages;

\echo ''
\echo '5. TEST RLS AS USER 3 (NOT IN CONVERSATION):'
SET app.current_user_id TO '33333333-3333-3333-3333-333333333333';

\echo 'Conversations User 3 can see (SHOULD BE EMPTY):'
SELECT id, title FROM conversations;

\echo 'Messages User 3 can see (SHOULD BE EMPTY):'
SELECT id, sender_id, content FROM messages;

\echo ''
\echo '6. TEST RLS BYPASS (as table owner - current behavior):'
RESET app.current_user_id;

\echo 'Conversations without RLS context (as owner - sees ALL):'
SELECT count(*) as total_conversations FROM conversations;

\echo ''
\echo '7. CHECK RLS POLICY DEFINITIONS:'
\echo 'Conversations policies:'
SELECT policyname, cmd, qual FROM pg_policies WHERE tablename = 'conversations';

\echo 'Messages policies:'
SELECT policyname, cmd, qual FROM pg_policies WHERE tablename = 'messages';

\echo ''
\echo '8. CLEANUP:'
DELETE FROM messages WHERE id IN ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'cccccccc-cccc-cccc-cccc-cccccccccccc');
DELETE FROM conversation_participants WHERE conversation_id = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa';
DELETE FROM conversations WHERE id = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa';
DELETE FROM users WHERE id IN (
    '11111111-1111-1111-1111-111111111111',
    '22222222-2222-2222-2222-222222222222', 
    '33333333-3333-3333-3333-333333333333'
);
