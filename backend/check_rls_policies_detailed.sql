\c safe_zone

-- Check all RLS policies and their exact conditions
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies 
WHERE tablename IN ('posts', 'comments', 'journals', 'users')
ORDER BY tablename, policyname;
