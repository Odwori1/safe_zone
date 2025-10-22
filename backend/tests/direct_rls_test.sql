-- Direct RLS Test Script
-- Run this in psql to test RLS enforcement

\echo '🔍 TESTING RLS ENFORCEMENT DIRECTLY'
\echo '=================================='

\echo ''
\echo '1. CURRENT USER CONTEXT:'
SELECT current_user, current_setting('app.current_user_id', true) as current_user_id;

\echo ''
\echo '2. CREATE TEST USERS AND DATA:'

-- Create test users if they don't exist
INSERT INTO users (id, email, username, hashed_password, full_name, is_active)
VALUES 
    ('11111111-1111-1111-1111-111111111111'::uuid, 'test_user1@example.com', 'testuser1', 'fakehash1', 'Test User 1', true),
    ('22222222-2222-2222-2222-222222222222'::uuid, 'test_user2@example.com', 'testuser2', 'fakehash2', 'Test User 2', true),
    ('33333333-3333-3333-3333-333333333333'::uuid, 'test_user3@example.com', 'testuser3', 'fakehash3', 'Test User 3', true)
ON CONFLICT (email) DO NOTHING;

-- Create test conversation between user1 and user2
INSERT INTO conversations (id, title, created_at)
VALUES ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid, 'Test Conversation', NOW())
ON CONFLICT DO NOTHING;

-- Add participants
INSERT INTO conversation_participants (conversation_id, user_id, joined_at)
VALUES 
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid, '11111111-1111-1111-1111-111111111111'::uuid, NOW()),
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid, '22222222-2222-2222-2222-222222222222'::uuid, NOW())
ON CONFLICT DO NOTHING;

-- Add test messages
INSERT INTO messages (id, conversation_id, sender_id, content, message_type, created_at)
VALUES 
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'::uuid, 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid, '11111111-1111-1111-1111-111111111111'::uuid, 'Hello from User 1', 'text', NOW()),
    ('cccccccc-cccc-cccc-cccc-cccccccccccc'::uuid, 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid, '22222222-2222-2222-2222-222222222222'::uuid, 'Hello from User 2', 'text', NOW())
ON CONFLICT DO NOTHING;

\echo ''
\echo '3. TEST RLS AS USER 1:'
SET app.current_user_id TO '11111111-1111-1111-1111-111111111111';

\echo 'Conversations User 1 can see:'
SELECT id, title FROM conversations;

\echo 'Messages User 1 can see:'
SELECT id, sender_id, content FROM messages;

\echo ''
\echo '4. TEST RLS AS USER 3 (NOT IN CONVERSATION):'
SET app.current_user_id TO '33333333-3333-3333-3333-333333333333';

\echo 'Conversations User 3 can see (should be empty):'
SELECT id, title FROM conversations;

\echo 'Messages User 3 can see (should be empty):'
SELECT id, sender_id, content FROM messages;

\echo ''
\echo '5. TEST RLS BYPASS (as table owner):'
RESET app.current_user_id;

\echo 'Conversations without RLS context (as owner):'
SELECT id, title FROM conversations;

\echo ''
\echo '6. CLEANUP:'
DELETE FROM messages WHERE id IN ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'cccccccc-cccc-cccc-cccc-cccccccccccc');
DELETE FROM conversation_participants WHERE conversation_id = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa';
DELETE FROM conversations WHERE id = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa';
DELETE FROM users WHERE id IN (
    '11111111-1111-1111-1111-111111111111',
    '22222222-2222-2222-2222-222222222222', 
    '33333333-3333-3333-3333-333333333333'
);
