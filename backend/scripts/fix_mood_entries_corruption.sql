-- Temporarily disable RLS for mood_entries
ALTER TABLE mood_entries DISABLE ROW LEVEL SECURITY;

-- Find all mood entries and check for corruption
SELECT id::text, user_id::text, source_type, source_id::text 
FROM mood_entries 
ORDER BY created_at DESC;

-- If we find corrupted records, delete all mood entries for this user
-- (Since this is development and we can recreate them)
DELETE FROM mood_entries 
WHERE user_id = '8808956b-11fb-4253-91ef-98b9902ffbc8'::uuid;

-- Re-enable RLS
ALTER TABLE mood_entries ENABLE ROW LEVEL SECURITY;

-- Verify the table is empty for this user
SELECT COUNT(*) FROM mood_entries WHERE user_id = '8808956b-11fb-4253-91ef-98b9902ffbc8'::uuid;
