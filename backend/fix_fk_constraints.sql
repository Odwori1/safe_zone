-- Fix for live_audio_room_participants UPDATE issue
-- Drop and recreate foreign key constraints to fix INSTEAD OF trigger issue

-- First, drop the foreign key constraints
ALTER TABLE live_audio_room_participants 
DROP CONSTRAINT live_audio_room_participants_room_id_fkey;

ALTER TABLE live_audio_room_participants 
DROP CONSTRAINT live_audio_room_participants_user_id_fkey;

-- Now recreate them with the same specifications
ALTER TABLE live_audio_room_participants 
ADD CONSTRAINT live_audio_room_participants_room_id_fkey 
FOREIGN KEY (room_id) REFERENCES live_audio_rooms(id) ON DELETE CASCADE;

ALTER TABLE live_audio_room_participants 
ADD CONSTRAINT live_audio_room_participants_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Verify the constraints were recreated
SELECT conname, contype, confrelid::regclass 
FROM pg_constraint 
WHERE conrelid = 'live_audio_room_participants'::regclass 
AND contype = 'f';
