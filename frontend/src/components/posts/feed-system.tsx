'use client';

import { useState, useEffect } from 'react';
import { usePostsStore } from '@/stores/posts-store';
import { useAuth } from '@/hooks/use-auth';
import PostsFilter from './posts-filter';
import { FeedFilter } from '@/stores/posts-store';
import {
  RefreshCw,
  Loader2,
  Bookmark,
  Users,
  TrendingUp,
  BarChart3
} from 'lucide-react';

export default function FeedSystem() {
  const {
    feedPosts,
    feedStats,
    isLoading,
    error,
    fetchPersonalFeed,
    fetchDiscoverFeed,
    fetchFeedStats
  } = usePostsStore();
  
  const { user } = useAuth();
  const [activeFeed, setActiveFeed] = useState<'personal' | 'discover'>('personal');
  const [filters, setFilters] = useState<FeedFilter>({
    skip: 0,
    limit: 20
  });

  useEffect(() => {
    if (user) {
      loadFeed();
      fetchFeedStats();
    }
  }, [user, activeFeed, filters]);

  useEffect(() => {
    // Listen for feed type changes from the filter component
    const handleFeedTypeChange = (event: CustomEvent) => {
      const { feedType } = event.detail;
      if (feedType === 'personal') {
        setActiveFeed('personal');
      } else if (feedType === 'discover') {
        setActiveFeed('discover');
      }
    };

    window.addEventListener('feedTypeChange', handleFeedTypeChange as EventListener);
    return () => {
      window.removeEventListener('feedTypeChange', handleFeedTypeChange as EventListener);
    };
  }, []);

  const loadFeed = async () => {
    if (activeFeed === 'personal') {
      await fetchPersonalFeed(filters);
    } else if (activeFeed === 'discover') {
      await fetchDiscoverFeed(filters);
    }
  };

  const handleRefresh = () => {
    loadFeed();
    fetchFeedStats();
  };

  const handleFilterChange = (newFilters: FeedFilter) => {
    setFilters(newFilters);
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
      <div className="text-center py-12">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Please log in</h3>
        <p className="text-gray-600">You need to be logged in to view the feed.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Enhanced Filter */}
      <PostsFilter
        onFilterChange={handleFilterChange}
        currentFilters={filters}
        showFeedOptions={true}
      />

      {/* Feed Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            {activeFeed === 'personal' ? (
              <>
                <Users className="h-6 w-6 text-blue-600" />
                Your Personal Feed
              </>
            ) : (
              <>
                <TrendingUp className="h-6 w-6 text-purple-600" />
                Discover New Content
              </>
            )}
          </h2>
          <p className="text-gray-600 mt-1">
            {activeFeed === 'personal' 
              ? 'Posts from people you follow and relevant content'
              : 'Trending and recommended posts from the community'
            }
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Feed Stats */}
          {feedStats && (
            <div className="hidden sm:block text-sm text-gray-600 bg-gray-100 px-3 py-1 rounded-full">
              {feedStats.total_available_posts} posts available
            </div>
          )}

          {/* Refresh Button */}
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
      </div>

      {/* Feed Stats Cards */}
      {feedStats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center gap-3">
              <BarChart3 className="h-8 w-8 text-blue-600" />
              <div>
                <p className="text-sm text-blue-800">Available Posts</p>
                <p className="text-2xl font-bold text-blue-900">{feedStats.total_available_posts}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center gap-3">
              <Users className="h-8 w-8 text-green-600" />
              <div>
                <p className="text-sm text-green-800">Community Size</p>
                <p className="text-2xl font-bold text-green-900">Growing</p>
              </div>
            </div>
          </div>
          
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
            <div className="flex items-center gap-3">
              <Bookmark className="h-8 w-8 text-purple-600" />
              <div>
                <p className="text-sm text-purple-800">Personalized</p>
                <p className="text-2xl font-bold text-purple-900">AI-Curated</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Feed Posts */}
      {feedPosts.length === 0 ? (
        <div className="bg-white rounded-lg border-2 border-dashed p-12 text-center">
          {isLoading ? (
            <>
              <Loader2 className="h-12 w-12 text-gray-400 animate-spin mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Loading feed...</h3>
              <p className="text-gray-600">Fetching personalized content for you</p>
            </>
          ) : (
            <>
              <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {activeFeed === 'personal' ? 'No posts in your feed yet' : 'No discover posts available'}
              </h3>
              <p className="text-gray-600 mb-4">
                {activeFeed === 'personal' 
                  ? 'Follow more users or engage with posts to personalize your feed.'
                  : 'Check back later for new trending content.'
                }
              </p>
              <button
                onClick={handleRefresh}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                Refresh Feed
              </button>
            </>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          {feedPosts.map((post) => (
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
                    </p>
                  </div>
                </div>

                {/* Feed Badge */}
                <span className={`text-xs px-2 py-1 rounded-full ${
                  activeFeed === 'personal' 
                    ? 'bg-blue-100 text-blue-800' 
                    : 'bg-purple-100 text-purple-800'
                }`}>
                  {activeFeed === 'personal' ? 'Personal' : 'Discover'}
                </span>
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

              {/* Post Stats */}
              <div className="px-4 py-3 border-t bg-gray-50">
                <div className="flex items-center gap-6 text-sm text-gray-600">
                  <span>❤️ {post.like_count || 0} likes</span>
                  <span>💬 {post.comment_count || 0} comments</span>
                  <span>🔗 {post.share_count || 0} shares</span>
                  {post.user_has_saved && (
                    <span className="text-purple-600">📑 Saved</span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Loading indicator */}
      {isLoading && feedPosts.length > 0 && (
        <div className="flex justify-center items-center py-4">
          <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
          <span className="ml-2 text-gray-600">Loading more posts...</span>
        </div>
      )}
    </div>
  );
}
