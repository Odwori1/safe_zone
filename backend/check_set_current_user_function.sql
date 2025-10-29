\c safe_zone

-- Check if set_current_user_id function exists
SELECT 
    routine_name,
    routine_type,
    routine_definition
FROM information_schema.routines 
WHERE routine_name = 'set_current_user_id';

-- Check if it was created in any scripts
SELECT proname, prosrc 
FROM pg_proc 
WHERE proname = 'set_current_user_id';
