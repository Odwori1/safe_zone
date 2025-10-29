import { create } from 'zustand';
import { UserSearchResult, UserSearchResults, UsersFilter } from '@/types/users';
import { apiClient } from '@/lib/api-client';

interface UsersState {
  searchResults: UserSearchResult[];
  suggestions: UserSearchResult[];
  isLoading: boolean;
  error: string | null;
  followLoading: { [userId: string]: boolean };
  relationshipStatus: { [userId: string]: { is_following: boolean, is_blocked?: boolean } };
  blockLoading: { [userId: string]: boolean };
  reportLoading: { [userId: string]: boolean };

  // Actions
  searchUsers: (filters: UsersFilter) => Promise<void>;
  getSuggestions: (limit?: number) => Promise<void>;
  clearError: () => void;
  clearResults: () => void;

  // Follow actions
  followUser: (userId: string) => Promise<void>;
  unfollowUser: (userId: string) => Promise<void>;
  getRelationshipStatus: (userId: string) => Promise<void>;
  updateUserFollowStatus: (userId: string, isFollowing: boolean) => void;

  // Block/Report actions
  blockUser: (userId: string) => Promise<void>;
  unblockUser: (userId: string) => Promise<void>;
  reportUser: (userId: string, reason: string, details?: string) => Promise<void>;
  updateUserBlockStatus: (userId: string, isBlocked: boolean) => void;
}

export const useUsersStore = create<UsersState>((set, get) => ({
  searchResults: [],
  suggestions: [],
  isLoading: false,
  error: null,
  followLoading: {},
  relationshipStatus: {},
  blockLoading: {},
  reportLoading: {},

  searchUsers: async (filters: UsersFilter) => {
    console.log('🔄 USERS STORE: Searching users...', { filters });
    set({ isLoading: true, error: null });

    try {
      const { query, limit = 20, offset = 0 } = filters;

      // Build URL parameters matching backend expectations
      const params = new URLSearchParams({
        limit: limit.toString(),
        offset: offset.toString(),
        include_unverified: 'true' // Add this required parameter
      });

      // Add query if provided (backend expects 'query' parameter)
      if (query && query.trim()) {
        params.append('query', query.trim());
      }

      const response = await apiClient.request(`/api/v1/users/search?${params}`);
      console.log('📡 USERS STORE: Search request completed', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ USERS STORE: Search failed with response:', errorText);
        throw new Error(`Failed to search users: ${response.status} ${response.statusText}`);
      }

      const results: UserSearchResults = await response.json();
      console.log('✅ USERS STORE: Search successful, found:', results.users.length, 'users');

      set({
        searchResults: results.users,
        isLoading: false
      });

    } catch (error) {
      console.error('❌ USERS STORE: Search error:', error);
      set({
        error: error instanceof Error ? error.message : 'Failed to search users',
        isLoading: false,
        searchResults: []
      });
    }
  },

  getSuggestions: async (limit = 10) => {
    console.log('🔄 USERS STORE: Getting suggestions...');
    set({ isLoading: true, error: null });

    try {
      const response = await apiClient.request(`/api/v1/users/suggestions?limit=${limit}`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to get suggestions`);
      }

      const results: UserSearchResults = await response.json();
      console.log('✅ USERS STORE: Suggestions:', results.users.length);

      set({
        suggestions: results.users,
        isLoading: false
      });

    } catch (error) {
      console.error('❌ USERS STORE: Suggestions error:', error);
      set({
        error: error instanceof Error ? error.message : 'Failed to get suggestions',
        isLoading: false,
        suggestions: []
      });
    }
  },

  clearError: () => set({ error: null }),
  clearResults: () => set({ searchResults: [] }),

  // Follow user
  followUser: async (userId: string) => {
    set(state => ({
      followLoading: { ...state.followLoading, [userId]: true }
    }));

    try {
      const response = await apiClient.request('/api/v1/users/follow', {
        method: 'POST',
        body: JSON.stringify({ following_id: userId })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to follow user`);
      }

      const result = await response.json();

      // Update local follow state
      set(state => ({
        followLoading: { ...state.followLoading, [userId]: false },
        relationshipStatus: {
          ...state.relationshipStatus,
          [userId]: { is_following: true }
        }
      }));

      // Update follow status in search results and suggestions
      get().updateUserFollowStatus(userId, true);
    } catch (error) {
      console.error('❌ Follow error:', error);
      set(state => ({
        followLoading: { ...state.followLoading, [userId]: false },
        error: error instanceof Error ? error.message : 'Failed to follow user'
      }));
      throw error;
    }
  },

  // Unfollow user
  unfollowUser: async (userId: string) => {
    set(state => ({
      followLoading: { ...state.followLoading, [userId]: true }
    }));

    try {
      const response = await apiClient.request(`/api/v1/users/unfollow/${userId}`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to unfollow user`);
      }

      const result = await response.json();

      // Update local follow state
      set(state => ({
        followLoading: { ...state.followLoading, [userId]: false },
        relationshipStatus: {
          ...state.relationshipStatus,
          [userId]: { is_following: false }
        }
      }));

      // Update follow status in search results and suggestions
      get().updateUserFollowStatus(userId, false);
    } catch (error) {
      console.error('❌ Unfollow error:', error);
      set(state => ({
        followLoading: { ...state.followLoading, [userId]: false },
        error: error instanceof Error ? error.message : 'Failed to unfollow user'
      }));
      throw error;
    }
  },

  // Get relationship status
  getRelationshipStatus: async (userId: string) => {
    try {
      const response = await apiClient.request(`/api/v1/users/relationships/${userId}`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to get relationship status`);
      }

      const status = await response.json();

      set(state => ({
        relationshipStatus: {
          ...state.relationshipStatus,
          [userId]: status
        }
      }));
    } catch (error) {
      console.error('❌ Relationship status error:', error);
      // Optional: handle error silently
    }
  },

  // Update follow status in search results and suggestions
  updateUserFollowStatus: (userId: string, isFollowing: boolean) => {
    set(state => ({
      searchResults: state.searchResults.map(user =>
        user.id === userId ? { ...user, is_following: isFollowing } : user
      ),
      suggestions: state.suggestions.map(user =>
        user.id === userId ? { ...user, is_following: isFollowing } : user
      )
    }));
  },

  // Block user
  blockUser: async (userId: string) => {
    set(state => ({
      blockLoading: { ...state.blockLoading, [userId]: true }
    }));

    try {
      const response = await apiClient.request('/api/v1/users/block', {
        method: 'POST',
        body: JSON.stringify({ blocked_user_id: userId })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to block user`);
      }

      const result = await response.json();

      // Update local block state
      set(state => ({
        blockLoading: { ...state.blockLoading, [userId]: false },
        relationshipStatus: {
          ...state.relationshipStatus,
          [userId]: { 
            ...state.relationshipStatus[userId],
            is_blocked: true 
          }
        }
      }));

      // Update block status in search results and suggestions
      get().updateUserBlockStatus(userId, true);
    } catch (error) {
      console.error('❌ Block error:', error);
      set(state => ({
        blockLoading: { ...state.blockLoading, [userId]: false },
        error: error instanceof Error ? error.message : 'Failed to block user'
      }));
      throw error;
    }
  },

  // Unblock user
  unblockUser: async (userId: string) => {
    set(state => ({
      blockLoading: { ...state.blockLoading, [userId]: true }
    }));

    try {
      const response = await apiClient.request(`/api/v1/users/unblock/${userId}`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to unblock user`);
      }

      const result = await response.json();

      // Update local block state
      set(state => ({
        blockLoading: { ...state.blockLoading, [userId]: false },
        relationshipStatus: {
          ...state.relationshipStatus,
          [userId]: { 
            ...state.relationshipStatus[userId],
            is_blocked: false 
          }
        }
      }));

      // Update block status in search results and suggestions
      get().updateUserBlockStatus(userId, false);
    } catch (error) {
      console.error('❌ Unblock error:', error);
      set(state => ({
        blockLoading: { ...state.blockLoading, [userId]: false },
        error: error instanceof Error ? error.message : 'Failed to unblock user'
      }));
      throw error;
    }
  },

  // Report user
  reportUser: async (userId: string, reason: string, details?: string) => {
    set(state => ({
      reportLoading: { ...state.reportLoading, [userId]: true }
    }));

    try {
      const response = await apiClient.request('/api/v1/users/report', {
        method: 'POST',
        body: JSON.stringify({ 
          reported_user_id: userId,
          report_reason: reason,
          report_details: details 
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to report user`);
      }

      const result = await response.json();

      set(state => ({
        reportLoading: { ...state.reportLoading, [userId]: false }
      }));

      return result;
    } catch (error) {
      console.error('❌ Report error:', error);
      set(state => ({
        reportLoading: { ...state.reportLoading, [userId]: false },
        error: error instanceof Error ? error.message : 'Failed to report user'
      }));
      throw error;
    }
  },

  // Update block status in search results and suggestions
  updateUserBlockStatus: (userId: string, isBlocked: boolean) => {
    set(state => ({
      searchResults: state.searchResults.map(user =>
        user.id === userId ? { 
          ...user, 
          relationship_status: {
            ...user.relationship_status,
            is_blocked: isBlocked
          }
        } : user
      ),
      suggestions: state.suggestions.map(user =>
        user.id === userId ? { 
          ...user, 
          relationship_status: {
            ...user.relationship_status,
            is_blocked: isBlocked
          }
        } : user
      )
    }));
  },
}));
