import { create } from 'zustand';
import { PostCreate, PostResponse, PostUpdate, PostsFilter, ShareResponse } from '@/types/posts';
import { apiClient } from '@/lib/api-client';

// ADD NEW INTERFACES FOR FEED AND SAVED POSTS
export interface FeedFilter {
  skip?: number;
  limit?: number;
  mood?: string;
  visibility?: string;
  content_type?: string;
}

export interface SavedPostResponse extends PostResponse {
  saved_at?: string;
}

export interface FeedStats {
  total_available_posts: number;
  user_id: string;
  message: string;
}

export interface SavedStats {
  total_saved_posts: number;
  user_id: string;
}

export interface SaveResponse {
  message: string;
  already_saved: boolean;
}

// Define the return type for getPostById
export interface Post {
  id: string;
  // Add other relevant fields if needed
  [key: string]: any;
}

interface PostsState {
  posts: PostResponse[];
  currentPost: PostResponse | null;
  savedPosts: SavedPostResponse[];
  feedPosts: PostResponse[];
  isLoading: boolean;
  error: string | null;
  feedStats: FeedStats | null;
  savedStats: SavedStats | null;

  // Existing Actions
  getPosts: (filters?: PostsFilter) => Promise<void>;
  getPost: (postId: string) => Promise<void>;
  createPost: (postData: PostCreate) => Promise<void>;
  updatePost: (postId: string, postData: PostUpdate) => Promise<void>;
  deletePost: (postId: string) => Promise<void>;
  likePost: (postId: string) => Promise<void>;
  unlikePost: (postId: string) => Promise<void>;
  sharePost: (postId: string, caption?: string) => Promise<ShareResponse>;
  clearError: () => void;
  clearCurrentPost: () => void;

  // NEW: Phase 2.7 Feed System Actions
  fetchPersonalFeed: (filters?: FeedFilter) => Promise<void>;
  fetchDiscoverFeed: (filters?: FeedFilter) => Promise<void>;
  fetchFeedStats: () => Promise<void>;

  // NEW: Saved Posts Actions
  savePost: (postId: string) => Promise<SaveResponse>;
  unsavePost: (postId: string) => Promise<void>;
  fetchSavedPosts: (filters?: FeedFilter) => Promise<void>;
  fetchSavedStats: () => Promise<void>;

  // NEW: getPostById method
  getPostById: (postId: string) => Promise<Post>;
}

export const usePostsStore = create<PostsState>((set, get) => {
  // FIXED VERSION: getPostById function
  const getPostById = async (postId: string): Promise<Post> => {
    try {
      console.log('🔄 POSTS STORE: Fetching post by ID:', postId);
      
      // ✅ CORRECT: Use request method with full API path
      const response = await apiClient.request(`/api/v1/posts/${postId}`);
      console.log('📥 POSTS STORE: Response status:', response.status);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to fetch post`);
      }
      
      const postData: Post = await response.json();
      console.log('✅ POSTS STORE: Received post:', postData);
      return postData;
      
    } catch (error) {
      console.error('❌ POSTS STORE: Error fetching post:', error);
      throw error;
    }
  };

  return {
    posts: [],
    currentPost: null,
    savedPosts: [],
    feedPosts: [],
    isLoading: false,
    error: null,
    feedStats: null,
    savedStats: null,

    // ========== EXISTING METHODS (UNCHANGED) ==========

    getPosts: async (filters = {}) => {
      const { skip = 0, limit = 100, ...otherFilters } = filters;
      console.log('🔄 POSTS STORE: Getting posts...', { filters });
      set({ isLoading: true, error: null });
      try {
        const params = new URLSearchParams({
          skip: skip.toString(),
          limit: limit.toString(),
          ...Object.fromEntries(
            Object.entries(otherFilters).filter(([_, value]) => value !== undefined)
          )
        });
        const response = await apiClient.request(`/api/v1/posts/?${params}`);
        console.log('📥 POSTS STORE: Response status:', response.status);
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: Failed to fetch posts`);
        }
        const posts: PostResponse[] = await response.json();
        console.log('✅ POSTS STORE: Received', posts.length, 'posts');
        set({ posts, isLoading: false });
      } catch (error) {
        console.error('❌ POSTS STORE: Error fetching posts:', error);
        set({
          error: error instanceof Error ? error.message : 'Failed to fetch posts',
          isLoading: false,
          posts: []
        });
      }
    },

    getPost: async (postId: string) => {
      console.log('🔄 POSTS STORE: Getting post:', postId);
      set({ isLoading: true, error: null });
      try {
        const response = await apiClient.request(`/api/v1/posts/${postId}`);
        console.log('📥 POSTS STORE: Get post response status:', response.status);
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: Failed to fetch post`);
        }
        const post: PostResponse = await response.json();
        console.log('✅ POSTS STORE: Received post:', post.id);
        set({ currentPost: post, isLoading: false });
      } catch (error) {
        console.error('❌ POSTS STORE: Error fetching post:', error);
        set({
          error: error instanceof Error ? error.message : 'Failed to fetch post',
          isLoading: false
        });
      }
    },

    createPost: async (postData: PostCreate) => {
      console.log('🔄 POSTS STORE: Creating post...', postData);
      set({ isLoading: true, error: null });
      try {
        const response = await apiClient.request('/api/v1/posts/', {
          method: 'POST',
          body: JSON.stringify(postData),
        });
        console.log('📥 POSTS STORE: Create response status:', response.status);
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: Failed to create post`);
        }
        const newPost: PostResponse = await response.json();
        console.log('✅ POSTS STORE: Post created successfully:', newPost.id);
        set((state) => ({
          posts: [newPost, ...state.posts],
          isLoading: false
        }));
        return newPost;
      } catch (error) {
        console.error('❌ POSTS STORE: Create error:', error);
        set({
          error: error instanceof Error ? error.message : 'Failed to create post',
          isLoading: false
        });
        throw error;
      }
    },

    updatePost: async (postId: string, postData: PostUpdate) => {
      console.log('🔄 POSTS STORE: Updating post:', postId, postData);
      set({ isLoading: true, error: null });
      try {
        const response = await apiClient.request(`/api/v1/posts/${postId}`, {
          method: 'PUT',
          body: JSON.stringify(postData),
        });
        console.log('📥 POSTS STORE: Update response status:', response.status);
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: Failed to update post`);
        }
        const updatedPost: PostResponse = await response.json();
        console.log('✅ POSTS STORE: Post updated successfully:', updatedPost.id);
        set((state) => ({
          posts: state.posts.map(post =>
            post.id === postId ? updatedPost : post
          ),
          currentPost: state.currentPost?.id === postId ? updatedPost : state.currentPost,
          isLoading: false
        }));
        return updatedPost;
      } catch (error) {
        console.error('❌ POSTS STORE: Update error:', error);
        set({
          error: error instanceof Error ? error.message : 'Failed to update post',
          isLoading: false
        });
        throw error;
      }
    },

    deletePost: async (postId: string) => {
      console.log('🔄 POSTS STORE: Deleting post:', postId);
      set({ isLoading: true, error: null });
      try {
        const response = await apiClient.request(`/api/v1/posts/${postId}`, {
          method: 'DELETE',
        });
        console.log('📥 POSTS STORE: Delete response status:', response.status);
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: Failed to delete post`);
        }
        set((state) => ({
          posts: state.posts.filter((post) => post.id !== postId),
          currentPost: state.currentPost?.id === postId ? null : state.currentPost,
          isLoading: false
        }));
        console.log('✅ POSTS STORE: Post deleted successfully:', postId);
      } catch (error) {
        console.error('❌ POSTS STORE: Delete error:', error);
        set({
          error: error instanceof Error ? error.message : 'Failed to delete post',
          isLoading: false
        });
        throw error;
      }
    },

    likePost: async (postId: string) => {
      console.log('🔄 POSTS STORE: Liking post:', postId);
      try {
        const response = await apiClient.request(`/api/v1/posts/${postId}/like`, {
          method: 'POST',
        });
        console.log('📥 POSTS STORE: Like response status:', response.status);
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: Failed to like post`);
        }
        set((state) => ({
          posts: state.posts.map(post =>
            post.id === postId
              ? {
                  ...post,
                  like_count: (post.like_count || 0) + 1,
                  user_has_liked: true
                }
              : post
          )
        }));
        console.log('✅ POSTS STORE: Post liked successfully:', postId);
      } catch (error) {
        console.error('❌ POSTS STORE: Like error:', error);
        set((state) => ({
          posts: state.posts.map(post =>
            post.id === postId
              ? {
                  ...post,
                  like_count: Math.max(0, (post.like_count || 1) - 1),
                  user_has_liked: false
                }
              : post
          )
        }));
        throw error;
      }
    },

    unlikePost: async (postId: string) => {
      console.log('🔄 POSTS STORE: Unliking post:', postId);
      try {
        const response = await apiClient.request(`/api/v1/posts/${postId}/unlike`, {
          method: 'POST',
        });
        console.log('📥 POSTS STORE: Unlike response status:', response.status);
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: Failed to unlike post`);
        }
        set((state) => ({
          posts: state.posts.map(post =>
            post.id === postId
              ? {
                  ...post,
                  like_count: Math.max(0, (post.like_count || 1) - 1),
                  user_has_liked: false
                }
              : post
          )
        }));
        console.log('✅ POSTS STORE: Post unliked successfully:', postId);
      } catch (error) {
        console.error('❌ POSTS STORE: Unlike error:', error);
        set((state) => ({
          posts: state.posts.map(post =>
            post.id === postId
              ? {
                  ...post,
                  like_count: (post.like_count || 0) + 1,
                  user_has_liked: true
                }
              : post
          )
        }));
        throw error;
      }
    },

    sharePost: async (postId: string, caption?: string) => {
      console.log('🔄 POSTS STORE: Sharing post:', postId, { caption });
      try {
        const shareData = caption ? { caption } : undefined;
        console.log("📤 SHARE STORE: Sharing post", postId, "with method:", caption ? "platform" : "copy");
        const share_method = caption ? "platform" : "copy";

        const response = await apiClient.request(`/api/v1/posts/${postId}/share`, {
          method: 'POST',
          body: shareData ? JSON.stringify(shareData) : undefined,
        });
        console.log('📥 POSTS STORE: Share response status:', response.status);
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: Failed to share post`);
        }
        const shareDataResponse: ShareResponse = await response.json();
        const enhancedResponse = {
          ...shareDataResponse,
          share_method,
          share_url: share_method === "copy" ? `${window.location.origin}/posts/${postId}` : undefined
        };
        console.log("✅ SHARE STORE: Enhanced share response:", enhancedResponse);
        console.log('✅ POSTS STORE: Share response:', shareDataResponse);
        // Update the post with new share data
        set((state) => ({
          posts: state.posts.map(post =>
            post.id === postId
              ? {
                  ...post,
                  share_count: shareDataResponse.share_count,
                  user_has_shared: !shareDataResponse.already_shared,
                }
              : post
          ),
          currentPost: state.currentPost?.id === postId
            ? {
                ...state.currentPost,
                share_count: shareDataResponse.share_count,
                user_has_shared: !shareDataResponse.already_shared,
              }
            : state.currentPost,
        }));
        console.log('✅ POSTS STORE: Post share status updated:', postId);
        return enhancedResponse;
      } catch (error) {
        console.error('❌ POSTS STORE: Share error:', error);
        throw error;
      }
    },

    // ========== PHASE 2.7: FEED SYSTEM METHODS ==========

    fetchPersonalFeed: async (filters: FeedFilter = {}) => {
      const { skip = 0, limit = 20, ...otherFilters } = filters;
      console.log('🔄 POSTS STORE: Fetching personal feed...', { filters });
      set({ isLoading: true, error: null });
      try {
        const params = new URLSearchParams({
          skip: skip.toString(),
          limit: limit.toString(),
          ...Object.fromEntries(
            Object.entries(otherFilters).filter(([_, value]) => value !== undefined)
          )
        });
        const response = await apiClient.request(`/api/v1/posts/feed/personal?${params}`);
        console.log('📥 POSTS STORE: Personal feed response status:', response.status);
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: Failed to fetch personal feed`);
        }
        const feedPosts: PostResponse[] = await response.json();
        console.log('✅ POSTS STORE: Received', feedPosts.length, 'posts in personal feed');
        set({ feedPosts, isLoading: false });
      } catch (error) {
        console.error('❌ POSTS STORE: Error fetching personal feed:', error);
        set({
          error: error instanceof Error ? error.message : 'Failed to fetch personal feed',
          isLoading: false,
          feedPosts: []
        });
      }
    },

    fetchDiscoverFeed: async (filters: FeedFilter = {}) => {
      const { skip = 0, limit = 10, ...otherFilters } = filters;
      console.log('🔄 POSTS STORE: Fetching discover feed...', { filters });
      set({ isLoading: true, error: null });
      try {
        const params = new URLSearchParams({
          skip: skip.toString(),
          limit: limit.toString(),
          ...Object.fromEntries(
            Object.entries(otherFilters).filter(([_, value]) => value !== undefined)
          )
        });
        const response = await apiClient.request(`/api/v1/posts/feed/discover?${params}`);
        console.log('📥 POSTS STORE: Discover feed response status:', response.status);
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: Failed to fetch discover feed`);
        }
        const discoverPosts: PostResponse[] = await response.json();
        console.log('✅ POSTS STORE: Received', discoverPosts.length, 'posts in discover feed');
        set({ feedPosts: discoverPosts, isLoading: false });
      } catch (error) {
        console.error('❌ POSTS STORE: Error fetching discover feed:', error);
        set({
          error: error instanceof Error ? error.message : 'Failed to fetch discover feed',
          isLoading: false,
          feedPosts: []
        });
      }
    },

    fetchFeedStats: async () => {
      console.log('🔄 POSTS STORE: Fetching feed stats...');
      set({ isLoading: true, error: null });
      try {
        const response = await apiClient.request('/api/v1/posts/feed/stats');
        console.log('📥 POSTS STORE: Feed stats response status:', response.status);
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: Failed to fetch feed stats`);
        }
        const feedStats: FeedStats = await response.json();
        console.log('✅ POSTS STORE: Received feed stats:', feedStats);
        set({ feedStats, isLoading: false });
      } catch (error) {
        console.error('❌ POSTS STORE: Error fetching feed stats:', error);
        set({
          error: error instanceof Error ? error.message : 'Failed to fetch feed stats',
          isLoading: false
        });
      }
    },

    // ========== PHASE 2.7: SAVED POSTS METHODS ==========

    savePost: async (postId: string) => {
      console.log('🔄 POSTS STORE: Saving post:', postId);
      try {
        const response = await apiClient.request(`/api/v1/posts/${postId}/save`, {
          method: 'POST',
        });
        console.log('📥 POSTS STORE: Save response status:', response.status);
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: Failed to save post`);
        }
        const saveResponse: SaveResponse = await response.json();
        console.log('✅ POSTS STORE: Save response:', saveResponse);
        set((state) => ({
          posts: state.posts.map(post =>
            post.id === postId
              ? { ...post, user_has_saved: true }
              : post
          ),
          feedPosts: state.feedPosts.map(post =>
            post.id === postId
              ? { ...post, user_has_saved: true }
              : post
          ),
          currentPost: state.currentPost?.id === postId
            ? { ...state.currentPost, user_has_saved: true }
            : state.currentPost,
        }));
        if (!saveResponse.already_saved) {
          set((state) => ({
            savedStats: state.savedStats
              ? { ...state.savedStats, total_saved_posts: state.savedStats.total_saved_posts + 1 }
              : { total_saved_posts: 1, user_id: '' }
          }));
        }
        console.log('✅ POSTS STORE: Post saved successfully:', postId);
        return saveResponse;
      } catch (error) {
        console.error('❌ POSTS STORE: Save error:', error);
        throw error;
      }
    },

    unsavePost: async (postId: string) => {
      console.log('🔄 POSTS STORE: Unsaving post:', postId);
      try {
        const response = await apiClient.request(`/api/v1/posts/${postId}/unsave`, {
          method: 'POST',
        });
        console.log('📥 POSTS STORE: Unsave response status:', response.status);
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: Failed to unsave post`);
        }
        set((state) => ({
          posts: state.posts.map(post =>
            post.id === postId
              ? { ...post, user_has_saved: false }
              : post
          ),
          feedPosts: state.feedPosts.map(post =>
            post.id === postId
              ? { ...post, user_has_saved: false }
              : post
          ),
          currentPost: state.currentPost?.id === postId
            ? { ...state.currentPost, user_has_saved: false }
            : state.currentPost,
          savedPosts: state.savedPosts.filter(post => post.id !== postId),
        }));
        set((state) => ({
          savedStats: state.savedStats
            ? { ...state.savedStats, total_saved_posts: Math.max(0, state.savedStats.total_saved_posts - 1) }
            : { total_saved_posts: 0, user_id: '' }
        }));
        console.log('✅ POSTS STORE: Post unsaved successfully:', postId);
      } catch (error) {
        console.error('❌ POSTS STORE: Unsave error:', error);
        throw error;
      }
    },

    fetchSavedPosts: async (filters: FeedFilter = {}) => {
      const { skip = 0, limit = 20, ...otherFilters } = filters;
      console.log('🔄 POSTS STORE: Fetching saved posts...', { filters });
      set({ isLoading: true, error: null });
      try {
        const params = new URLSearchParams({
          skip: skip.toString(),
          limit: limit.toString(),
          ...Object.fromEntries(
            Object.entries(otherFilters).filter(([_, value]) => value !== undefined)
          )
        });
        const response = await apiClient.request(`/api/v1/posts/saved/posts?${params}`);
        console.log('📥 POSTS STORE: Saved posts response status:', response.status);
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: Failed to fetch saved posts`);
        }
        const savedPosts: SavedPostResponse[] = await response.json();
        console.log('✅ POSTS STORE: Received', savedPosts.length, 'saved posts');
        set({ savedPosts, isLoading: false });
      } catch (error) {
        console.error('❌ POSTS STORE: Error fetching saved posts:', error);
        set({
          error: error instanceof Error ? error.message : 'Failed to fetch saved posts',
          isLoading: false,
          savedPosts: []
        });
      }
    },

    fetchSavedStats: async () => {
      console.log('🔄 POSTS STORE: Fetching saved stats...');
      set({ isLoading: true, error: null });
      try {
        const response = await apiClient.request('/api/v1/posts/saved/stats');
        console.log('📥 POSTS STORE: Saved stats response status:', response.status);
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: Failed to fetch saved stats`);
        }
        const savedStats: SavedStats = await response.json();
        console.log('✅ POSTS STORE: Received saved stats:', savedStats);
        set({ savedStats, isLoading: false });
      } catch (error) {
        console.error('❌ POSTS STORE: Error fetching saved stats:', error);
        set({
          error: error instanceof Error ? error.message : 'Failed to fetch saved stats',
          isLoading: false
        });
      }
    },

    clearError: () => set({ error: null }),
    clearCurrentPost: () => set({ currentPost: null }),

    // add the new method
    getPostById,
  };
});
