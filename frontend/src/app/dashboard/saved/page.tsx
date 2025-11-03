'use client';

import { useState, useEffect } from 'react';
import { usePostsStore } from '@/stores/posts-store';
import { useAuth } from '@/hooks/use-auth';
import { SavedPostResponse } from '@/stores/posts-store';
import { 
  Heart, 
  MessageCircle, 
  Share2, 
  Bookmark, 
  BookmarkCheck,
  RefreshCw,
  Loader2,
  ChevronDown,
  ChevronUp,
  MoreVertical,
  Trash2
} from 'lucide-react';

export default function SavedPostsPage() {
  const {
    savedPosts,
    savedStats,
    isLoading,
    error,
    fetchSavedPosts,
    fetchSavedStats,
    unsavePost,
    likePost,
    unlikePost,
    sharePost,
    deletePost
  } = usePostsStore();
  
  const { user } = useAuth();
  const [hasLoaded, setHasLoaded] = useState(false);
  const [unsavingId, setUnsavingId] = useState<string | null>(null);
  const [likingId, setLikingId] = useState<string | null>(null);
  const [sharingId, setSharingId] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [activeMenu, setActiveMenu] = useState<string | null>(null);
  const [expandedPostId, setExpandedPostId] = useState<string | null>(null);

  useEffect(() => {
    if (user && !hasLoaded) {
      loadSavedPosts();
    }
  }, [user]);

  const loadSavedPosts = async () => {
    console.log('🔄 Loading saved posts...');
    await Promise.all([
      fetchSavedPosts(),
      fetchSavedStats()
    ]);
    setHasLoaded(true);
  };

  const handleRefresh = () => {
    if (user) {
      loadSavedPosts();
    }
  };

  const handleUnsavePost = async (postId: string) => {
    setUnsavingId(postId);
    setActiveMenu(null);
    try {
      await unsavePost(postId);
    } finally {
      setUnsavingId(null);
    }
  };

  const handleLikePost = async (postId: string) => {
    setLikingId(postId);
    try {
      const post = savedPosts.find(p => p.id === postId);
      if (post?.user_has_liked) {
        await unlikePost(postId);
      } else {
        await likePost(postId);
      }
      // Refresh to get updated counts
      await fetchSavedPosts();
    } finally {
      setLikingId(null);
    }
  };

  const handleSharePost = async (postId: string) => {
    setSharingId(postId);
    try {
      await sharePost(postId);
      // Refresh to get updated counts
      await fetchSavedPosts();
    } finally {
      setSharingId(null);
    }
  };

  const handleDeletePost = async (postId: string) => {
    setDeletingId(postId);
    setActiveMenu(null);
    try {
      await deletePost(postId);
      // Refresh the list
      await fetchSavedPosts();
      await fetchSavedStats();
    } finally {
      setDeletingId(null);
    }
  };

  const toggleComments = (postId: string) => {
    setExpandedPostId(expandedPostId === postId ? null : postId);
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

  const getMoodColor = (mood: string | null) => {
    if (!mood) return 'bg-gray-100 text-gray-800';

    const moodColors: { [key: string]: string } = {
      happy: 'bg-yellow-100 text-yellow-800',
      calm: 'bg-green-100 text-green-800',
      neutral: 'bg-blue-100 text-blue-800',
      anxious: 'bg-orange-100 text-orange-800',
      sad: 'bg-indigo-100 text-indigo-800',
      angry: 'bg-red-100 text-red-800',
      tired: 'bg-purple-100 text-purple-800',
      excited: 'bg-pink-100 text-pink-800'
    };

    return moodColors[mood.toLowerCase()] || 'bg-gray-100 text-gray-800';
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Please log in</h2>
          <p className="text-gray-600">You need to be logged in to view saved posts.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Saved Posts</h1>
            <p className="text-gray-600 mt-2">
              {savedStats ? `${savedStats.total_saved_posts} saved posts` : 'Loading...'}
            </p>
          </div>
          <button
            onClick={handleRefresh}
            disabled={isLoading}
            className="flex items-center gap-2 bg-white border border-gray-300 px-4 py-2 rounded-lg hover:bg-gray-50 disabled:opacity-50 transition-colors"
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <RefreshCw className="h-4 w-4" />
            )}
            Refresh
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Saved Posts List */}
        {savedPosts.length === 0 ? (
          <div className="bg-white rounded-lg border-2 border-dashed p-12 text-center">
            <Bookmark className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              {hasLoaded ? 'No saved posts yet' : 'Loading saved posts...'}
            </h3>
            <p className="text-gray-600 mb-4">
              {hasLoaded 
                ? 'Posts you save will appear here for easy access later.'
                : 'Fetching your saved posts...'
              }
            </p>
            {hasLoaded && (
              <p className="text-sm text-gray-500">
                Click the save button on any post to add it to your collection.
              </p>
            )}
          </div>
        ) : (
          <div className="space-y-6">
            {savedPosts.map((post) => (
              <div
                key={post.id}
                className="bg-white rounded-lg border shadow-sm hover:shadow-md transition-shadow"
              >
                {/* Post Header */}
                <div className="flex justify-between items-start p-4 pb-2">
                  <div className="flex items-center gap-3">
                    <div className="flex-shrink-0">
                      {post.is_anonymous ? (
                        <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                          <span className="text-xs font-medium text-gray-600">A</span>
                        </div>
                      ) : (
                        <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                          <span className="text-xs font-medium text-white">
                            {post.username?.[0]?.toUpperCase() || 'U'}
                          </span>
                        </div>
                      )}
                    </div>
                    <div>
                      <p className="font-medium text-sm">
                        {post.is_anonymous ? 'Anonymous' : post.username || 'User'}
                      </p>
                      <p className="text-xs text-gray-500">
                        {formatDate(post.created_at)}
                        {post.visibility === 'private' && ' · 🔒 Private'}
                        {post.visibility === 'support_group' && ' · 👥 Support Group'}
                        {post.saved_at && ` · Saved ${formatDate(post.saved_at)}`}
                      </p>
                    </div>
                  </div>

                  {/* Post Actions Menu */}
                  <div className="flex items-center gap-2">
                    {/* Unsave Button */}
                    <button
                      onClick={() => handleUnsavePost(post.id)}
                      disabled={unsavingId === post.id}
                      className="flex items-center gap-2 text-purple-600 hover:text-purple-700 disabled:opacity-50 transition-colors"
                      title="Remove from saved"
                    >
                      {unsavingId === post.id ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <BookmarkCheck className="h-5 w-5 fill-current" />
                      )}
                    </button>

                    {/* More Actions Menu */}
                    {user && post.user_id === user.id && (
                      <div className="relative">
                        <button
                          onClick={() => setActiveMenu(activeMenu === post.id ? null : post.id)}
                          className="h-8 w-8 p-0 rounded-md hover:bg-gray-100 transition-colors"
                        >
                          <MoreVertical className="h-4 w-4 mx-auto" />
                        </button>

                        {activeMenu === post.id && (
                          <div className="absolute right-0 top-8 bg-white border rounded-lg shadow-lg z-10 min-w-[120px]">
                            <button
                              onClick={() => handleDeletePost(post.id)}
                              disabled={deletingId === post.id}
                              className="flex items-center gap-2 w-full px-3 py-2 text-sm text-red-600 hover:bg-red-50 disabled:opacity-50 rounded-t-lg transition-colors"
                            >
                              {deletingId === post.id ? (
                                <Loader2 className="h-3 w-3 animate-spin" />
                              ) : (
                                <Trash2 className="h-3 w-3" />
                              )}
                              Delete
                            </button>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>

                {/* Post Content */}
                <div className="px-4 py-2">
                  <p className="text-gray-800 whitespace-pre-wrap">{post.content}</p>

                  {/* Mood Badge */}
                  {post.mood && (
                    <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium mt-3 ${getMoodColor(post.mood)}`}>
                      {post.mood}
                    </span>
                  )}
                </div>

                {/* Post Footer - Actions */}
                <div className="px-4 py-3 border-t">
                  <div className="flex items-center gap-6">
                    {/* Like Button */}
                    <button
                      onClick={() => handleLikePost(post.id)}
                      disabled={likingId === post.id}
                      className={`flex items-center gap-2 text-sm ${
                        post.user_has_liked
                          ? 'text-red-600 hover:text-red-700'
                          : 'text-gray-600 hover:text-gray-700'
                      } disabled:opacity-50 transition-colors`}
                    >
                      {likingId === post.id ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Heart
                          className={`h-5 w-5 ${post.user_has_liked ? 'fill-current' : ''}`}
                        />
                      )}
                      <span className="font-medium">{post.like_count || 0}</span>
                    </button>

                    {/* Comment Button */}
                    <button
                      onClick={() => toggleComments(post.id)}
                      className={`flex items-center gap-2 text-sm ${
                        expandedPostId === post.id
                          ? 'text-blue-600 hover:text-blue-700'
                          : 'text-gray-600 hover:text-gray-700'
                      } transition-colors`}
                    >
                      <MessageCircle className="h-5 w-5" />
                      <span className="font-medium">{post.comment_count || 0}</span>
                      {expandedPostId === post.id ? (
                        <ChevronUp className="h-4 w-4" />
                      ) : (
                        <ChevronDown className="h-4 w-4" />
                      )}
                    </button>

                    {/* Share Button */}
                    <button
                      onClick={() => handleSharePost(post.id)}
                      disabled={sharingId === post.id || post.user_has_shared}
                      className={`flex items-center gap-2 text-sm ${
                        post.user_has_shared
                          ? 'text-blue-600 cursor-not-allowed'
                          : 'text-gray-600 hover:text-gray-700'
                      } disabled:opacity-50 transition-colors`}
                    >
                      {sharingId === post.id ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Share2 className="h-5 w-5" />
                      )}
                      <span className="font-medium">{post.share_count || 0}</span>
                    </button>
                  </div>
                </div>

                {/* Comments Section */}
                {expandedPostId === post.id && (
                  <div className="border-t bg-gray-50 animate-in fade-in duration-300">
                    <div className="p-4">
                      <div className="flex items-center justify-between mb-4">
                        <h4 className="font-semibold text-gray-900">Comments</h4>
                        <span className="text-sm text-gray-500">
                          {post.comment_count || 0} {post.comment_count === 1 ? 'comment' : 'comments'}
                        </span>
                      </div>
                      <div className="text-center text-gray-500 py-8">
                        <MessageCircle className="h-8 w-8 mx-auto mb-2 opacity-50" />
                        <p>Comment functionality coming soon</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Loading indicator for refreshes */}
        {isLoading && hasLoaded && (
          <div className="flex justify-center items-center py-4">
            <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
            <span className="ml-2 text-gray-600">Refreshing saved posts...</span>
          </div>
        )}
      </div>
    </div>
  );
}
