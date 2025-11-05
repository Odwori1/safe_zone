// FILE: src/stores/audio-rooms-store.ts (CORRECTED - no JSX)
import { create } from 'zustand';
import { AudioRoom, CreateAudioRoomData } from '@/types/audio-rooms';
import { apiClient } from '@/lib/api-client';

interface AudioRoomsState {
  rooms: AudioRoom[];
  isLoading: boolean;
  error: string | null;
  fetchRooms: () => Promise<void>;
  createRoom: (data: CreateAudioRoomData) => Promise<void>;
}

export const useAudioRoomsStore = create<AudioRoomsState>((set, get) => ({
  rooms: [],
  isLoading: false,
  error: null,

  fetchRooms: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.request('/api/v1/audio/rooms/');
      if (!response.ok) throw new Error('Failed to fetch rooms');
      const rooms = await response.json();
      set({ rooms, isLoading: false });
    } catch (error) {
      set({ 
        error: error instanceof Error ? error.message : 'Failed to fetch rooms',
        isLoading: false 
      });
    }
  },

  createRoom: async (data: CreateAudioRoomData) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.request('/api/v1/audio/rooms/', {
        method: 'POST',
        body: JSON.stringify(data),
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Failed to create room: ${response.status}`);
      }
      
      const newRoom = await response.json();
      set(state => ({
        rooms: [...state.rooms, newRoom],
        isLoading: false
      }));
      return newRoom;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to create room';
      set({
        error: errorMessage,
        isLoading: false
      });
      throw error;
    }
  },
}));
