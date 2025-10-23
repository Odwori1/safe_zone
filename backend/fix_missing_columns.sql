-- Add missing columns required by the RLS policies
ALTER TABLE live_audio_rooms ADD COLUMN IF NOT EXISTS visibility VARCHAR(20) DEFAULT 'public' CHECK (visibility IN ('public', 'private'));

-- Verify the columns exist
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_name = 'live_audio_rooms' 
AND column_name IN ('visibility', 'is_active', 'created_by');
