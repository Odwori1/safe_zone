import { create } from 'zustand';
import { PostCreate, PostResponse, PostUpdate, PostsFilter } from '@/types/posts';
import { apiClient } from '@/lib/api-client';

interface PostsState {
  posts: PostResponse[];
  currentPost: PostResponse | null;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  getPosts: (filters?: PostsFilter) => Promise<void>;
  getPost: (postId: string) => Promise<void>;
  createPost: (postData: PostCreate) => Promise<void>;
  updatePost: (postId: string, postData: PostUpdate) => Promise<void>;
  deletePost: (postId: string) => Promise<void>;
  likePost: (postId: string) => Promise<void>;
  unlikePost: (postId: string) => Promise<void>;
  clearError: () => void;
  clearCurrentPost: () => void;
}

export const usePostsStore = create<PostsState>((set, get) => ({
  posts: [],
  currentPost: null,
  isLoading: false,
  error: null,

  getPosts: async (filters = {}) => {
    const { skip = 0, limit = 100, ...otherFilters } = filters;
    
    console.log('🔄 POSTS STORE: Getting posts...', { filters });
    set({ isLoading: true, error: null });

    try {
      // Build query string from filters
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

      // Add new post to the beginning of the list
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

      // Update post in the list
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

      // Remove post from local state immediately
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

      // Optimistically update the post
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
      // Revert optimistic update
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

      // Optimistically update the post
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
      // Revert optimistic update
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

  clearError: () => set({ error: null }),
  clearCurrentPost: () => set({ currentPost: null }),
}));
