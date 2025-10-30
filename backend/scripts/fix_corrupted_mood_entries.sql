-- Find potentially corrupted UUIDs in mood_entries table
-- Check for source_id values that might not be valid UUIDs
SELECT 
    id::text,
    user_id::text, 
    source_type,
    source_id::text,
    length(source_id::text) as source_id_length
FROM mood_entries 
WHERE source_id IS NOT NULL 
AND source_id::text !~ '^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$';

-- Alternative: Check all mood entries to see what we have
SELECT count(*) as total_entries FROM mood_entries;

-- Check entries by source_type
SELECT source_type, count(*) 
FROM mood_entries 
GROUP BY source_type;
