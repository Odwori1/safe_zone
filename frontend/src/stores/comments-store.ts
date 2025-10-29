import { create } from 'zustand';
import { CommentResponse, CommentCreate, CommentUpdate } from '@/types/comments';
import { apiClient } from '@/lib/api-client';

interface CommentsState {
  comments: CommentResponse[];
  isLoading: boolean;
  error: string | null;
  currentPostId: string | null;

  // Actions
  getComments: (filters: { post_id: string; page?: number; limit?: number }) => Promise<void>;
  createComment: (commentData: CommentCreate) => Promise<CommentResponse | void>;
  updateComment: (commentId: string, commentData: CommentUpdate) => Promise<CommentResponse | void>;
  deleteComment: (commentId: string) => Promise<void>;
  likeComment: (commentId: string) => Promise<void>;
  unlikeComment: (commentId: string) => Promise<void>;
  clearError: () => void;
  clearComments: () => void;
}

export const useCommentsStore = create<CommentsState>((set, get) => ({
  comments: [],
  isLoading: false,
  error: null,
  currentPostId: null,

  getComments: async ({ post_id, page = 1, limit = 50 }) => {
    console.log('🔄 COMMENTS STORE: Getting comments for post:', post_id);
    set({ isLoading: true, error: null, currentPostId: post_id });

    try {
      const response = await apiClient.request(`/api/v1/comments/post/${post_id}?page=${page}&limit=${limit}`);
      console.log('📥 COMMENTS STORE: Response status:', response.status);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to fetch comments`);
      }

      const data = await response.json();
      console.log('✅ COMMENTS STORE: Received', data.comments.length, 'comments');

      set({ comments: data.comments, isLoading: false });
    } catch (error) {
      console.error('❌ COMMENTS STORE: Error fetching comments:', error);
      set({
        error: error instanceof Error ? error.message : 'Failed to fetch comments',
        isLoading: false,
        comments: []
      });
    }
  },

  createComment: async (commentData: CommentCreate) => {
    console.log('🔄 COMMENTS STORE: Creating comment...', commentData);
    set({ isLoading: true, error: null });

    try {
      const response = await apiClient.request('/api/v1/comments/', {
        method: 'POST',
        body: JSON.stringify(commentData),
      });
      console.log('📥 COMMENTS STORE: Create response status:', response.status);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to create comment`);
      }

      const newComment: CommentResponse = await response.json();
      console.log('✅ COMMENTS STORE: Comment created successfully:', newComment.id);

      // Add new comment appropriately
      set((state) => {
        if (newComment.parent_comment_id) {
          // It's a reply; find the parent and add
          const updateReply = (comments: CommentResponse[]): CommentResponse[] => 
            comments.map(comment => {
              if (comment.id === newComment.parent_comment_id) {
                return {
                  ...comment,
                  replies: [...(comment.replies || []), newComment],
                  reply_count: (comment.reply_count || 0) + 1
                };
              }
              if (comment.replies && comment.replies.length > 0) {
                return {
                  ...comment,
                  replies: updateReply(comment.replies)
                };
              }
              return comment;
            });

          return {
            comments: updateReply(state.comments),
            isLoading: false
          };
        } else {
          // Top-level comment
          return {
            comments: [newComment, ...state.comments],
            isLoading: false
          };
        }
      });

      return newComment;
    } catch (error) {
      console.error('❌ COMMENTS STORE: Create error:', error);
      set({
        error: error instanceof Error ? error.message : 'Failed to create comment',
        isLoading: false
      });
    }
  },

  updateComment: async (commentId: string, commentData: CommentUpdate) => {
    console.log('🔄 COMMENTS STORE: Updating comment:', commentId, commentData);
    set({ isLoading: true, error: null });

    try {
      const response = await apiClient.request(`/api/v1/comments/${commentId}`, {
        method: 'PUT',
        body: JSON.stringify(commentData),
      });
      console.log('📥 COMMENTS STORE: Update response status:', response.status);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to update comment`);
      }

      const updatedComment: CommentResponse = await response.json();
      console.log('✅ COMMENTS STORE: Comment updated successfully:', updatedComment.id);

      // Update in state
      const updateCommentInState = (comments: CommentResponse[]): CommentResponse[] => 
        comments.map(comment => {
          if (comment.id === commentId) {
            return updatedComment;
          }
          if (comment.replies && comment.replies.length > 0) {
            return {
              ...comment,
              replies: updateCommentInState(comment.replies)
            };
          }
          return comment;
        });

      set((state) => ({
        comments: updateCommentInState(state.comments),
        isLoading: false
      }));

      return updatedComment;
    } catch (error) {
      console.error('❌ COMMENTS STORE: Update error:', error);
      set({
        error: error instanceof Error ? error.message : 'Failed to update comment',
        isLoading: false
      });
    }
  },

  deleteComment: async (commentId: string) => {
    console.log('🔄 COMMENTS STORE: Deleting comment:', commentId);
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.request(`/api/v1/comments/${commentId}`, {
        method: 'DELETE',
      });
      console.log('📥 COMMENTS STORE: Delete response status:', response.status);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to delete comment`);
      }

      // Remove from state
      const removeComment = (comments: CommentResponse[]): CommentResponse[] => 
        comments
          .filter(c => c.id !== commentId)
          .map(c => ({
            ...c,
            replies: c.replies ? removeComment(c.replies) : []
          }));

      set((state) => ({
        comments: removeComment(state.comments),
        isLoading: false
      }));

      console.log('✅ COMMENTS STORE: Comment deleted successfully:', commentId);
    } catch (error) {
      console.error('❌ COMMENTS STORE: Delete error:', error);
      set({
        error: error instanceof Error ? error.message : 'Failed to delete comment',
        isLoading: false
      });
    }
  },

  likeComment: async (commentId: string) => {
    console.log('🔄 COMMENTS STORE: Liking comment:', commentId);
    try {
      const response = await apiClient.request(`/api/v1/comments/${commentId}/like`, {
        method: 'POST',
      });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to like comment`);
      }

      // optimistic update
      set((state) => {
        const updateLikes = (comments: CommentResponse[]): CommentResponse[] =>
          comments.map(c => {
            if (c.id === commentId) {
              return {
                ...c,
                like_count: (c.like_count || 0) + 1,
                user_has_liked: true
              };
            }
            if (c.replies && c.replies.length > 0) {
              return {
                ...c,
                replies: updateLikes(c.replies)
              };
            }
            return c;
          });
        return { comments: updateLikes(state.comments) };
      });
      console.log('✅ COMMENTS STORE: Comment liked successfully:', commentId);
    } catch (error) {
      console.error('❌ COMMENTS STORE: Like error:', error);
      // revert
      set((state) => {
        const revertLikes = (comments: CommentResponse[]): CommentResponse[] =>
          comments.map(c => {
            if (c.id === commentId) {
              return {
                ...c,
                like_count: Math.max(0, (c.like_count || 1) - 1),
                user_has_liked: false
              };
            }
            if (c.replies && c.replies.length > 0) {
              return {
                ...c,
                replies: revertLikes(c.replies)
              };
            }
            return c;
          });
        return { comments: revertLikes(state.comments) };
      });
    }
  },

  unlikeComment: async (commentId: string) => {
    console.log('🔄 COMMENTS STORE: Unliking comment:', commentId);
    try {
      const response = await apiClient.request(`/api/v1/comments/${commentId}/unlike`, {
        method: 'POST',
      });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to unlike comment`);
      }

      // optimistic update
      set((state) => {
        const updateLikes = (comments: CommentResponse[]): CommentResponse[] =>
          comments.map(c => {
            if (c.id === commentId) {
              return {
                ...c,
                like_count: Math.max(0, (c.like_count || 1) - 1),
                user_has_liked: false
              };
            }
            if (c.replies && c.replies.length > 0) {
              return {
                ...c,
                replies: updateLikes(c.replies)
              };
            }
            return c;
          });
        return { comments: updateLikes(state.comments) };
      });
      console.log('✅ COMMENTS STORE: Comment unliked successfully:', commentId);
    } catch (error) {
      console.error('❌ COMMENTS STORE: Unlike error:', error);
      // revert
      set((state) => {
        const revertLikes = (comments: CommentResponse[]): CommentResponse[] =>
          comments.map(c => {
            if (c.id === commentId) {
              return {
                ...c,
                like_count: (c.like_count || 0) + 1,
                user_has_liked: true
              };
            }
            if (c.replies && c.replies.length > 0) {
              return {
                ...c,
                replies: revertLikes(c.replies)
              };
            }
            return c;
          });
        return { comments: revertLikes(state.comments) };
      });
    }
  },

  clearError: () => set({ error: null }),
  clearComments: () => set({ comments: [], currentPostId: null }),
}));

// Helper function for nested replies updates
function updateCommentLikes(comments: CommentResponse[], commentId: string, isLiked: boolean): CommentResponse[] {
  return comments.map(comment => {
    if (comment.id === commentId) {
      return {
        ...comment,
        like_count: isLiked ? (comment.like_count || 0) + 1 : Math.max(0, (comment.like_count || 1) - 1),
        user_has_liked: isLiked
      };
    }
    if (comment.replies && comment.replies.length > 0) {
      return {
        ...comment,
        replies: updateCommentLikes(comment.replies, commentId, isLiked)
      };
    }
    return comment;
  });
}
