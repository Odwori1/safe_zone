'use client';

import { useEffect, useState } from 'react';
import { useCommentsStore } from '@/stores/comments-store';
import { useAuth } from '@/hooks/use-auth';
import CommentItem from './comment-item';
import { Loader2, MessageCircle, AlertCircle } from 'lucide-react';

interface CommentsListProps {
  postId: string;
}

export default function CommentsList({ postId }: CommentsListProps) {
  const { comments, isLoading, error, getComments } = useCommentsStore();
  const { isAuthenticated } = useAuth();
  const [hasLoaded, setHasLoaded] = useState(false);

  useEffect(() => {
    if (isAuthenticated && postId) {
      loadComments();
    }
  }, [isAuthenticated, postId]);

  const loadComments = async () => {
    try {
      await getComments({ post_id: postId, limit: 50 });
      setHasLoaded(true);
    } catch (error) {
      console.error('Failed to load comments:', error);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-center">
        <p className="text-yellow-800 text-sm">
          Please log in to view comments
        </p>
      </div>
    );
  }

  if (isLoading && !hasLoaded) {
    return (
      <div className="flex justify-center items-center py-8">
        <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
        <span className="ml-2 text-gray-600">Loading comments...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center gap-2 text-red-800 mb-2">
          <AlertCircle className="h-4 w-4" />
          <span className="font-medium">Error loading comments</span>
        </div>
        <p className="text-red-600 text-sm">{error}</p>
        <button
          onClick={loadComments}
          className="mt-2 text-sm text-red-700 hover:text-red-800 underline"
        >
          Try again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Comments Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <MessageCircle className="h-5 w-5" />
          Comments ({comments.length})
        </h3>
        <button
          onClick={loadComments}
          disabled={isLoading}
          className="text-sm text-blue-600 hover:text-blue-700 disabled:opacity-50 flex items-center gap-1"
        >
          {isLoading ? (
            <Loader2 className="h-3 w-3 animate-spin" />
          ) : null}
          Refresh
        </button>
      </div>

      {/* Comments List */}
      {comments.length === 0 ? (
        <div className="text-center py-8 border-2 border-dashed rounded-lg">
          <MessageCircle className="h-8 w-8 text-gray-400 mx-auto mb-2" />
          <p className="text-gray-500 text-sm">No comments yet</p>
          <p className="text-gray-400 text-xs mt-1">Be the first to comment</p>
        </div>
      ) : (
        <div className="space-y-3">
          {comments.map((comment) => (
            <CommentItem
              key={comment.id}
              comment={comment}
              postId={postId}
            />
          ))}
        </div>
      )}

      {/* Loading indicator for refreshes */}
      {isLoading && hasLoaded && (
        <div className="flex justify-center items-center py-4">
          <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
          <span className="ml-2 text-gray-600">Refreshing comments...</span>
        </div>
      )}
    </div>
  );
}
