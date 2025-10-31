// Complete Mood Store with all backend features
import { create } from 'zustand';
import { apiClient } from '@/lib/api-client';
import { 
  MoodEntry, 
  MoodStatistics, 
  EnhancedMoodStats, 
  MoodTaxonomy, 
  MoodCreate, 
  HybridMoodResponse,
  MoodHistoryResponse,
  ClinicalInsights,
  MoodCategory 
} from '@/types/mood';

interface MoodStore {
  // State
  moods: MoodEntry[];
  currentMood: MoodEntry | null;
  statistics: MoodStatistics | null;
  enhancedStats: EnhancedMoodStats | null;
  taxonomy: MoodTaxonomy | null;
  clinicalInsights: ClinicalInsights | null;
  loading: boolean;
  error: string | null;
  
  // Actions
  createMood: (moodData: MoodCreate) => Promise<void>;
  getMoodHistory: (days?: number, page?: number, limit?: number) => Promise<void>;
  getMoodStatistics: (days?: number) => Promise<void>;
  getEnhancedMoodStats: (days?: number) => Promise<void>;
  getMoodTaxonomy: () => Promise<void>;
  getClinicalInsights: (days?: number) => Promise<void>;
  getHybridMoodEntries: (days?: number) => Promise<HybridMoodResponse>;
  getEnhancedHybridEntries: (days?: number) => Promise<HybridMoodResponse>;
  createMoodFromPost: (postId: string, mood: string, intensity: number) => Promise<void>;
  createMoodFromJournal: (journalId: string, mood: string, intensity: number) => Promise<void>;
  clearError: () => void;
}

export const useMoodStore = create<MoodStore>((set, get) => ({
  // Initial state
  moods: [],
  currentMood: null,
  statistics: null,
  enhancedStats: null,
  taxonomy: null,
  clinicalInsights: null,
  loading: false,
  error: null,

  // Create a new mood entry
  createMood: async (moodData: MoodCreate) => {
    set({ loading: true, error: null });
    try {
      const response = await apiClient.request('/api/v1/mood/entries/', {
        method: 'POST',
        body: JSON.stringify(moodData)
      });
      const newMood: MoodEntry = await response.json();
      
      set(state => ({
        moods: [newMood, ...state.moods],
        currentMood: newMood,
        loading: false
      }));
    } catch (error: any) {
      set({ 
        error: error.message || 'Failed to create mood entry',
        loading: false 
      });
    }
  },

  // Get mood history with pagination
  getMoodHistory: async (days?: number, page: number = 1, limit: number = 20) => {
    set({ loading: true, error: null });
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        limit: limit.toString()
      });
      
      if (days) {
        params.append('days', days.toString());
      }

      const response = await apiClient.request(`/api/v1/mood/entries/?${params}`);
      const data: MoodHistoryResponse = await response.json();
      
      set({
        moods: data.entries,
        loading: false
      });
    } catch (error: any) {
      set({ 
        error: error.message || 'Failed to fetch mood history',
        loading: false 
      });
    }
  },

  // Get basic mood statistics
  getMoodStatistics: async (days: number = 30) => {
    set({ loading: true, error: null });
    try {
      const response = await apiClient.request(`/api/v1/mood/stats/?days=${days}`);
      const data: MoodStatistics = await response.json();
      
      set({
        statistics: data,
        loading: false
      });
    } catch (error: any) {
      set({ 
        error: error.message || 'Failed to fetch mood statistics',
        loading: false 
      });
    }
  },

  // Get enhanced mood statistics with clinical insights
  getEnhancedMoodStats: async (days: number = 30) => {
    set({ loading: true, error: null });
    try {
      const response = await apiClient.request(`/api/v1/mood/stats/enhanced?days=${days}`);
      const data: EnhancedMoodStats = await response.json();
      
      set({
        enhancedStats: data,
        loading: false
      });
    } catch (error: any) {
      set({ 
        error: error.message || 'Failed to fetch enhanced mood statistics',
        loading: false 
      });
    }
  },

  // Get professional mood taxonomy
  getMoodTaxonomy: async () => {
    set({ loading: true, error: null });
    try {
      const response = await apiClient.request('/api/v1/mood/taxonomy');
      const data: MoodTaxonomy = await response.json();
      
      set({
        taxonomy: data,
        loading: false
      });
    } catch (error: any) {
      set({ 
        error: error.message || 'Failed to fetch mood taxonomy',
        loading: false 
      });
    }
  },

  // Get clinical insights from mood patterns
  getClinicalInsights: async (days: number = 30) => {
    set({ loading: true, error: null });
    try {
      const response = await apiClient.request(`/api/v1/mood/insights/clinical?days=${days}`);
      const data: ClinicalInsights = await response.json();
      
      set({
        clinicalInsights: data,
        loading: false
      });
    } catch (error: any) {
      set({ 
        error: error.message || 'Failed to fetch clinical insights',
        loading: false 
      });
    }
  },

  // Get hybrid mood entries (basic)
  getHybridMoodEntries: async (days: number = 30): Promise<HybridMoodResponse> => {
    set({ loading: true, error: null });
    try {
      const response = await apiClient.request(`/api/v1/mood/entries/hybrid-working?days=${days}`);
      const data: HybridMoodResponse = await response.json();
      set({ loading: false });
      return data;
    } catch (error: any) {
      set({ 
        error: error.message || 'Failed to fetch hybrid mood entries',
        loading: false 
      });
      throw error;
    }
  },

  // Get enhanced hybrid entries with post/journal context
  getEnhancedHybridEntries: async (days: number = 30): Promise<HybridMoodResponse> => {
    set({ loading: true, error: null });
    try {
      const response = await apiClient.request(`/api/v1/mood/entries/hybrid-enhanced?days=${days}`);
      const data: HybridMoodResponse = await response.json();
      set({ loading: false });
      return data;
    } catch (error: any) {
      set({ 
        error: error.message || 'Failed to fetch enhanced hybrid entries',
        loading: false 
      });
      throw error;
    }
  },

  // Create mood entry from existing post
  createMoodFromPost: async (postId: string, mood: string, intensity: number) => {
    set({ loading: true, error: null });
    try {
      const response = await apiClient.request(`/api/v1/mood/entries/from-post/${postId}?mood=${mood}&intensity=${intensity}`, {
        method: 'POST'
      });
      const newMood: MoodEntry = await response.json();
      
      set(state => ({
        moods: [newMood, ...state.moods],
        loading: false
      }));
    } catch (error: any) {
      set({ 
        error: error.message || 'Failed to create mood from post',
        loading: false 
      });
    }
  },

  // Create mood entry from existing journal
  createMoodFromJournal: async (journalId: string, mood: string, intensity: number) => {
    set({ loading: true, error: null });
    try {
      const response = await apiClient.request(`/api/v1/mood/entries/from-journal/${journalId}?mood=${mood}&intensity=${intensity}`, {
        method: 'POST'
      });
      const newMood: MoodEntry = await response.json();
      
      set(state => ({
        moods: [newMood, ...state.moods],
        loading: false
      }));
    } catch (error: any) {
      set({ 
        error: error.message || 'Failed to create mood from journal',
        loading: false 
      });
    }
  },

  // Clear errors
  clearError: () => set({ error: null })
}));
