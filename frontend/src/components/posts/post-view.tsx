'use client';

import { useState, useEffect } from 'react';
import { usePostsStore } from '@/stores/posts-store';
import { useAuth } from '@/hooks/use-auth';
import { X, Heart, MessageCircle, Share2, Bookmark, BookmarkCheck, Loader2 } from 'lucide-react';
import CommentsList from './comments-list';
import CommentForm from './comment-form';

interface PostViewProps {
  postId: string;
  isOpen: boolean;
  onClose: () => void;
}

export default function PostView({ postId, isOpen, onClose }: PostViewProps) {
  const { getPostById, likePost, unlikePost, savePost, unsavePost } = usePostsStore();
  const { user } = useAuth();
  const [post, setPost] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [likingId, setLikingId] = useState<string | null>(null);
  const [savingId, setSavingId] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && postId) {
      loadPost();
    }
  }, [isOpen, postId]);

  const loadPost = async () => {
    setIsLoading(true);
    try {
      const postData = await getPostById(postId);
      setPost(postData);
    } catch (error) {
      console.error('Error loading post:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLikePost = async () => {
    if (!post || !user) return;
    
    setLikingId(post.id);
    try {
      if (post.user_has_liked) {
        await unlikePost(post.id);
      } else {
        await likePost(post.id);
      }
      // Reload post to get updated like status
      await loadPost();
    } finally {
      setLikingId(null);
    }
  };

  const handleSavePost = async () => {
    if (!post || !user) return;
    
    setSavingId(post.id);
    try {
      if (post.user_has_saved) {
        await unsavePost(post.id);
      } else {
        await savePost(post.id);
      }
      // Reload post to get updated save status
      await loadPost();
    } finally {
      setSavingId(null);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);

    if (diffInHours < 1) {
      return 'Just now';
    } else if (diffInHours < 24) {
      return `${Math.floor(diffInHours)}h ago`;
    } else if (diffInHours < 168) {
      return `${Math.floor(diffInHours / 24)}d ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">Post</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        <div className="overflow-y-auto max-h-[calc(90vh-140px)]">
          {isLoading ? (
            <div className="flex justify-center items-center p-8">
              <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
            </div>
          ) : post ? (
            <div className="p-6 space-y-4">
              {/* Post Header */}
              <div className="flex items-center gap-3">
                <div className="flex-shrink-0">
                  {post.is_anonymous ? (
                    <div className="w-10 h-10 bg-gray-300 rounded-full flex items-center justify-center">
                      <span className="text-sm font-medium text-gray-600">A</span>
                    </div>
                  ) : (
                    <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center">
                      <span className="text-sm font-medium text-white">
                        {post.author?.username?.[0]?.toUpperCase() || post.username?.[0]?.toUpperCase() || 'U'}
                      </span>
                    </div>
                  )}
                </div>
                <div>
                  <p className="font-medium">
                    {post.is_anonymous ? 'Anonymous' : post.author?.username || post.username || 'User'}
                  </p>
                  <p className="text-sm text-gray-500">
                    {formatDate(post.created_at)}
                    {post.visibility === 'private' && ' · 🔒 Private'}
                    {post.visibility === 'support_group' && ' · 👥 Support Group'}
                  </p>
                </div>
              </div>

              {/* Post Content */}
              <div className="text-gray-800 whitespace-pre-wrap">
                {post.content}
              </div>

              {/* Mood Badge */}
              {post.mood && (
                <span className="inline-block px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                  {post.mood}
                </span>
              )}

              {/* Post Stats */}
              <div className="flex items-center gap-6 text-sm text-gray-500 border-t pt-4">
                <span>{post.like_count || 0} likes</span>
                <span>{post.comment_count || 0} comments</span>
                <span>{post.share_count || 0} shares</span>
              </div>

              {/* Post Actions */}
              <div className="flex items-center justify-between border-t pt-4">
                <div className="flex items-center gap-6">
                  {/* Like Button */}
                  <button
                    onClick={handleLikePost}
                    disabled={likingId === post.id}
                    className={`flex items-center gap-2 text-sm ${
                      post.user_has_liked
                        ? 'text-red-600 hover:text-red-700'
                        : 'text-gray-600 hover:text-gray-700'
                    } disabled:opacity-50 transition-colors`}
                  >
                    {likingId === post.id ? (
                      <Loader2 className="h-5 w-5 animate-spin" />
                    ) : (
                      <Heart
                        className={`h-5 w-5 ${post.user_has_liked ? 'fill-current' : ''}`}
                      />
                    )}
                    Like
                  </button>

                  {/* Comment Button */}
                  <button className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-700 transition-colors">
                    <MessageCircle className="h-5 w-5" />
                    Comment
                  </button>

                  {/* Share Button */}
                  <button className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-700 transition-colors">
                    <Share2 className="h-5 w-5" />
                    Share
                  </button>
                </div>

                {/* Save Button */}
                <button
                  onClick={handleSavePost}
                  disabled={savingId === post.id}
                  className={`flex items-center gap-2 text-sm ${
                    post.user_has_saved
                      ? 'text-purple-600 hover:text-purple-700'
                      : 'text-gray-600 hover:text-gray-700'
                  } disabled:opacity-50 transition-colors`}
                >
                  {savingId === post.id ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : post.user_has_saved ? (
                    <BookmarkCheck className="h-4 w-4 fill-current" />
                  ) : (
                    <Bookmark className="h-4 w-4" />
                  )}
                  {post.user_has_saved ? 'Saved' : 'Save'}
                </button>
              </div>

              {/* Comments Section */}
              <div className="border-t pt-4">
                <CommentForm
                  postId={post.id}
                  onCommentAdded={loadPost}
                />
                <CommentsList postId={post.id} />
              </div>
            </div>
          ) : (
            <div className="p-8 text-center">
              <p className="text-gray-500">Post not found</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
