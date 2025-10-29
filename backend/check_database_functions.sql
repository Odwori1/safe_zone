\c safe_zone

-- Check all functions that might set context
SELECT 
    routine_name,
    routine_type,
    routine_definition
FROM information_schema.routines 
WHERE routine_definition LIKE '%set_config%'
   OR routine_definition LIKE '%request.jwt%'
   OR routine_definition LIKE '%current_setting%';
