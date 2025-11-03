-- Secure fix for missing current_participants column
-- Following exact same security patterns as established architecture

-- Step 1: Add the missing column with proper constraints
ALTER TABLE live_audio_rooms 
ADD COLUMN IF NOT EXISTS current_participants INTEGER DEFAULT 0;

-- Step 2: Drop existing constraint if it exists, then add security constraint
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'live_audio_rooms' AND constraint_name = 'valid_current_participants'
    ) THEN
        ALTER TABLE live_audio_rooms DROP CONSTRAINT valid_current_participants;
    END IF;
END $$;

ALTER TABLE live_audio_rooms 
ADD CONSTRAINT valid_current_participants 
CHECK (current_participants BETWEEN 0 AND max_participants);

-- Step 3: Create secure triggers (following established trigger patterns)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_trigger WHERE tgname = 'update_participant_count_on_join'
    ) THEN
        EXECUTE 'CREATE TRIGGER update_participant_count_on_join
            AFTER INSERT ON live_audio_room_participants
            FOR EACH ROW 
            WHEN (NEW.left_at IS NULL)
            EXECUTE FUNCTION update_room_participant_count()';
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_trigger WHERE tgname = 'update_participant_count_on_leave'
    ) THEN
        EXECUTE 'CREATE TRIGGER update_participant_count_on_leave
            AFTER UPDATE ON live_audio_room_participants
            FOR EACH ROW 
            WHEN (NEW.left_at IS NOT NULL AND OLD.left_at IS NULL)
            EXECUTE FUNCTION update_room_participant_count()';
    END IF;
END $$;

-- Step 4: Initialize counts securely (respecting RLS policies)
DO $$
DECLARE
    room_record RECORD;
BEGIN
    FOR room_record IN 
        SELECT id FROM live_audio_rooms 
        WHERE is_active = true
    LOOP
        UPDATE live_audio_rooms 
        SET current_participants = (
            SELECT COUNT(*) 
            FROM live_audio_room_participants 
            WHERE room_id = room_record.id 
            AND left_at IS NULL
        )
        WHERE id = room_record.id;
    END LOOP;
    
    -- Verification notice
    RAISE NOTICE 'Secure fix completed:';
    RAISE NOTICE '- Added current_participants column with security constraints';
    RAISE NOTICE '- Created secure triggers following established patterns';
    RAISE NOTICE '- Initialized participant counts maintaining RLS integrity';
END $$;
