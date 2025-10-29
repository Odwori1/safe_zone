\c safe_zone

-- Get the exact policy definitions for posts table
SELECT 
    schemaname,
    tablename, 
    policyname,
    cmd,
    qual::text as qualifier,
    with_check::text as with_check
FROM pg_policies 
WHERE tablename = 'posts';
