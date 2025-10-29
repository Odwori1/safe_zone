import { create } from 'zustand';
import { JournalCreate, JournalResponse, JournalUpdate, JournalStats, JournalPrompt, JournalFeedResponse } from '@/types/journals';
import { apiClient } from '@/lib/api-client';

interface JournalsState {
  journals: JournalResponse[];
  currentJournal: JournalResponse | null;
  stats: JournalStats | null;
  prompts: JournalPrompt[];
  isLoading: boolean;
  error: string | null;

  // Actions
  createJournal: (journalData: JournalCreate) => Promise<JournalResponse | null>;
  getJournals: (page?: number, limit?: number, status?: string) => Promise<JournalResponse[]>;
  getJournal: (journalId: string) => Promise<JournalResponse | null>;
  updateJournal: (journalId: string, updateData: JournalUpdate) => Promise<JournalResponse | null>;
  deleteJournal: (journalId: string) => Promise<boolean>;
  getStats: () => Promise<JournalStats | null>;
  getPrompts: (category?: string, difficulty?: string) => Promise<JournalPrompt[]>;
  clearError: () => void;
  clearCurrentJournal: () => void;
}

export const useJournalsStore = create<JournalsState>((set, get) => ({
  journals: [],
  currentJournal: null,
  stats: null,
  prompts: [],
  isLoading: false,
  error: null,

  createJournal: async (journalData: JournalCreate) => {
    console.log('🔄 JOURNALS STORE: Creating journal...', journalData);
    set({ isLoading: true, error: null });

    try {
      const response = await apiClient.request('/api/v1/journals/entries/', {
        method: 'POST',
        body: JSON.stringify(journalData),
      });

      console.log('📥 JOURNALS STORE: Create response status:', response.status);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to create journal`);
      }

      const newJournal: JournalResponse = await response.json();
      console.log('✅ JOURNALS STORE: Journal created successfully:', newJournal.id);

      // Add new journal to the beginning of the list
      set((state) => ({
        journals: [newJournal, ...state.journals],
        isLoading: false
      }));

      return newJournal;

    } catch (error) {
      console.error('❌ JOURNALS STORE: Create error:', error);
      set({
        error: error instanceof Error ? error.message : 'Failed to create journal',
        isLoading: false
      });
      throw error;
    }
  },

  getJournals: async (page = 1, limit = 50, status?: string) => {
    console.log('🔄 JOURNALS STORE: Getting journals...', { page, limit, status });
    set({ isLoading: true, error: null });

    try {
      const params = new URLSearchParams({
        page: page.toString(),
        limit: limit.toString()
      });

      if (status) {
        params.append('status', status);
      }

      const response = await apiClient.request(`/api/v1/journals/entries/?${params}`);
      console.log('📥 JOURNALS STORE: Get journals response status:', response.status);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to fetch journals`);
      }

      const data: JournalFeedResponse = await response.json();
      console.log('✅ JOURNALS STORE: Received', data.entries.length, 'journals');

      set({ journals: data.entries, isLoading: false });
      return data.entries;

    } catch (error) {
      console.error('❌ JOURNALS STORE: Error fetching journals:', error);
      set({
        error: error instanceof Error ? error.message : 'Failed to fetch journals',
        isLoading: false,
        journals: []
      });
      return [];
    }
  },

  getJournal: async (journalId: string) => {
    console.log('🔄 JOURNALS STORE: Getting journal:', journalId);
    set({ isLoading: true, error: null });

    try {
      const response = await apiClient.request(`/api/v1/journals/entries/${journalId}`);
      console.log('📥 JOURNALS STORE: Get journal response status:', response.status);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to fetch journal`);
      }

      const journal: JournalResponse = await response.json();
      console.log('✅ JOURNALS STORE: Received journal:', journal.id);

      set({ currentJournal: journal, isLoading: false });
      return journal;

    } catch (error) {
      console.error('❌ JOURNALS STORE: Error fetching journal:', error);
      set({
        error: error instanceof Error ? error.message : 'Failed to fetch journal',
        isLoading: false
      });
      return null;
    }
  },

  updateJournal: async (journalId: string, updateData: JournalUpdate) => {
    console.log('🔄 JOURNALS STORE: Updating journal:', journalId, updateData);
    set({ isLoading: true, error: null });

    try {
      const response = await apiClient.request(`/api/v1/journals/entries/${journalId}`, {
        method: 'PUT',
        body: JSON.stringify(updateData),
      });

      console.log('📥 JOURNALS STORE: Update response status:', response.status);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to update journal`);
      }

      const updatedJournal: JournalResponse = await response.json();
      console.log('✅ JOURNALS STORE: Journal updated successfully:', updatedJournal.id);

      // Update journal in the list
      set((state) => ({
        journals: state.journals.map(journal =>
          journal.id === journalId ? updatedJournal : journal
        ),
        currentJournal: state.currentJournal?.id === journalId ? updatedJournal : state.currentJournal,
        isLoading: false
      }));

      return updatedJournal;

    } catch (error) {
      console.error('❌ JOURNALS STORE: Update error:', error);
      set({
        error: error instanceof Error ? error.message : 'Failed to update journal',
        isLoading: false
      });
      throw error;
    }
  },

  deleteJournal: async (journalId: string) => {
    console.log('🔄 JOURNALS STORE: Deleting journal:', journalId);
    set({ isLoading: true, error: null });

    try {
      const response = await apiClient.request(`/api/v1/journals/entries/${journalId}`, {
        method: 'DELETE',
      });

      console.log('📥 JOURNALS STORE: Delete response status:', response.status);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to delete journal`);
      }

      // Remove journal from local state immediately
      set((state) => ({
        journals: state.journals.filter((journal) => journal.id !== journalId),
        currentJournal: state.currentJournal?.id === journalId ? null : state.currentJournal,
        isLoading: false
      }));

      console.log('✅ JOURNALS STORE: Journal deleted successfully:', journalId);
      return true;

    } catch (error) {
      console.error('❌ JOURNALS STORE: Delete error:', error);
      set({
        error: error instanceof Error ? error.message : 'Failed to delete journal',
        isLoading: false
      });
      throw error;
    }
  },

  getStats: async () => {
    console.log('🔄 JOURNALS STORE: Getting journal stats...');
    set({ isLoading: true, error: null });

    try {
      const response = await apiClient.request('/api/v1/journals/stats/');
      console.log('📥 JOURNALS STORE: Stats response status:', response.status);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to fetch journal stats`);
      }

      const stats: JournalStats = await response.json();
      console.log('✅ JOURNALS STORE: Received journal stats');

      set({ stats, isLoading: false });
      return stats;

    } catch (error) {
      console.error('❌ JOURNALS STORE: Error fetching stats:', error);
      set({
        error: error instanceof Error ? error.message : 'Failed to fetch journal stats',
        isLoading: false
      });
      return null;
    }
  },

  getPrompts: async (category?: string, difficulty?: string) => {
    console.log('🔄 JOURNALS STORE: Getting journal prompts...', { category, difficulty });
    set({ isLoading: true, error: null });

    try {
      const params = new URLSearchParams();
      if (category) params.append('category', category);
      if (difficulty) params.append('difficulty', difficulty);

      const url = `/api/v1/journals/prompts/${params.toString() ? `?${params}` : ''}`;
      const response = await apiClient.request(url);
      console.log('📥 JOURNALS STORE: Prompts response status:', response.status);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to fetch journal prompts`);
      }

      const prompts: JournalPrompt[] = await response.json();
      console.log('✅ JOURNALS STORE: Received', prompts.length, 'prompts');

      set({ prompts, isLoading: false });
      return prompts;

    } catch (error) {
      console.error('❌ JOURNALS STORE: Error fetching prompts:', error);
      set({
        error: error instanceof Error ? error.message : 'Failed to fetch journal prompts',
        isLoading: false
      });
      return [];
    }
  },

  clearError: () => set({ error: null }),
  clearCurrentJournal: () => set({ currentJournal: null }),
}));
