// FILE: src/types/audio-rooms.ts (updated to match backend)
export interface AudioRoom {
  id: string;
  title: string;
  description?: string;
  room_type: 'support' | 'discussion' | 'social';
  current_participants: number;
  max_participants: number;
  is_active: boolean;
  visibility: 'public' | 'private';
  created_at: string;
  created_by: {
    id: string;
    username: string;
    avatar_url?: string;
  };
}

export interface CreateAudioRoomData {
  title: string;
  description?: string;
  room_type: 'support' | 'discussion' | 'social';
  max_participants: number;
  visibility: 'public' | 'private';
}
