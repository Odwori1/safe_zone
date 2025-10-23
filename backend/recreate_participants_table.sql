-- Comprehensive fix: Recreate live_audio_room_participants table properly
-- This preserves data but fixes the INSTEAD OF trigger issue

BEGIN;

-- Create a backup table with the same structure
CREATE TABLE live_audio_room_participants_backup AS 
SELECT * FROM live_audio_room_participants;

-- Drop the problematic table (this will drop dependent objects too)
DROP TABLE live_audio_room_participants CASCADE;

-- Recreate the table with the exact same schema but proper constraints
CREATE TABLE live_audio_room_participants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    room_id UUID NOT NULL,
    user_id UUID NOT NULL,
    role VARCHAR(50) DEFAULT 'participant',
    is_active BOOLEAN DEFAULT true,
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    left_at TIMESTAMPTZ NULL,
    
    -- Add the expected constraints
    CONSTRAINT live_audio_room_participants_role_check 
        CHECK (role IN ('host', 'co-host', 'participant', 'listener'))
);

-- Add foreign key constraints (should create normal triggers)
ALTER TABLE live_audio_room_participants 
ADD CONSTRAINT live_audio_room_participants_room_id_fkey 
FOREIGN KEY (room_id) REFERENCES live_audio_rooms(id) ON DELETE CASCADE;

ALTER TABLE live_audio_room_participants 
ADD CONSTRAINT live_audio_room_participants_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Add unique constraint
ALTER TABLE live_audio_room_participants
ADD CONSTRAINT live_audio_room_participants_room_id_user_id_key 
UNIQUE (room_id, user_id);

-- Restore the data
INSERT INTO live_audio_room_participants 
(id, room_id, user_id, role, is_active, joined_at, left_at)
SELECT id, room_id, user_id, role, is_active, joined_at, left_at
FROM live_audio_room_participants_backup;

-- Drop the backup table
DROP TABLE live_audio_room_participants_backup;

-- Enable RLS
ALTER TABLE live_audio_room_participants ENABLE ROW LEVEL SECURITY;

-- Recreate RLS policies
CREATE POLICY live_audio_room_participants_select_policy ON live_audio_room_participants
    FOR SELECT USING (user_id = current_setting('app.current_user_id')::UUID);

CREATE POLICY live_audio_room_participants_insert_policy ON live_audio_room_participants
    FOR INSERT WITH CHECK (user_id = current_setting('app.current_user_id')::UUID);

CREATE POLICY live_audio_room_participants_update_policy ON live_audio_room_participants
    FOR UPDATE USING (user_id = current_setting('app.current_user_id')::UUID);

COMMIT;

-- Verify the table was recreated properly
SELECT 'Table recreated successfully' as status;

-- Check triggers
SELECT tgname, 
    CASE WHEN tgtype & 4 != 0 THEN 'INSTEAD OF' ELSE 'NORMAL' END as trigger_type
FROM pg_trigger 
WHERE tgrelid = 'live_audio_room_participants'::regclass;
