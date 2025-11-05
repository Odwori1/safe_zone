'use client';

import { useState, useEffect } from 'react';
import { usePostsStore } from '@/stores/posts-store';
import { useAuth } from '@/hooks/use-auth';
import { PostsFilter as PostsFilterType } from '@/types/posts';
import PostsFilter from './posts-filter';
import ShareDialog from './share-dialog';
import PostView from './post-view';
import FeedSystem from './feed-system';
import AudioPlayer from '@/components/media/audio-player'; // NEW: Audio player import
import {
  Heart,
  MessageCircle,
  Trash2,
  Edit3,
  RefreshCw,
  Loader2,
  MoreVertical,
  ChevronDown,
  ChevronUp,
  Share2,
  Bookmark,
  BookmarkCheck,
  Play, // NEW: Video play icon
  Pause, // NEW: Video pause icon
  Volume2, // NEW: Volume icon
  VolumeX // NEW: Mute icon
} from 'lucide-react';
import CommentsList from './comments-list';
import CommentForm from './comment-form';

let renderCount = 0;

interface PostsFeedProps {
  useFeedSystem?: boolean;
}

export default function PostsFeed({ useFeedSystem = false }: PostsFeedProps) {
  // If using feed system, return the FeedSystem component
  if (useFeedSystem) {
    return <FeedSystem />;
  }

  const {
    posts,
    isLoading,
    error,
    getPosts,
    deletePost,
    likePost,
    unlikePost,
    sharePost,
    savePost,
    unsavePost,
    getPostById
  } = usePostsStore();
  const { user } = useAuth();

  // State variables
  const [hasLoaded, setHasLoaded] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [likingId, setLikingId] = useState<string | null>(null);
  const [sharingId, setSharingId] = useState<string | null>(null);
  const [savingId, setSavingId] = useState<string | null>(null);
  const [activeMenu, setActiveMenu] = useState<string | null>(null);
  const [expandedPostId, setExpandedPostId] = useState<string | null>(null);

  // SHARE DIALOG
  const [shareDialogOpen, setShareDialogOpen] = useState(false);
  const [currentSharingPost, setCurrentSharingPost] = useState<{id: string, content: string} | null>(null);

  // POST VIEW MODAL
  const [viewingPostId, setViewingPostId] = useState<string | null>(null);

  // NEW: Video control states
  const [playingVideoId, setPlayingVideoId] = useState<string | null>(null);
  const [mutedVideos, setMutedVideos] = useState<{ [key: string]: boolean }>({});
  const [loadingVideoId, setLoadingVideoId] = useState<string | null>(null);
  const [videoRefs] = useState<{ [key: string]: HTMLVideoElement | null }>({});

  const [currentFilters, setCurrentFilters] = useState<PostsFilterType>({
    skip: 0,
    limit: 100
  });

  renderCount++;
  console.log(`🔄 PostsFeed RENDER #${renderCount}`, {
    hasLoaded,
    postsCount: posts.length,
    isLoading,
    error,
    expandedPostId,
    currentFilters
  });

  const handleLoadPosts = () => {
    console.log('🔄 Manual load triggered with filters:', currentFilters);
    getPosts(currentFilters).then(() => {
      console.log('✅ Posts loaded successfully with filters');
      setHasLoaded(true);
    });
  };

  const handleFilterChange = (filters: PostsFilterType) => {
    console.log('🎯 Filter changed:', filters);
    setCurrentFilters(filters);

    if (hasLoaded) {
      getPosts(filters);
    }
  };

  const handleRefresh = () => {
    if (user) {
      console.log('🔄 Refreshing with current filters:', currentFilters);
      getPosts(currentFilters);
    }
  };

  const handleDeletePost = async (postId: string) => {
    setDeletingId(postId);
    setActiveMenu(null);
    try {
      await deletePost(postId);
    } finally {
      setDeletingId(null);
    }
  };

  const handleLikePost = async (postId: string) => {
    setLikingId(postId);
    try {
      const post = posts.find(p => p.id === postId);
      if (post?.user_has_liked) {
        await unlikePost(postId);
      } else {
        await likePost(postId);
      }
    } finally {
      setLikingId(null);
    }
  };

  const handleSavePost = async (postId: string) => {
    setSavingId(postId);
    try {
      const post = posts.find(p => p.id === postId);
      if (post?.user_has_saved) {
        await unsavePost(postId);
      } else {
        await savePost(postId);
      }
    } finally {
      setSavingId(null);
    }
  };

  // UPDATED: Share handler with dialog
  const handleShareClick = (postId: string, postContent: string) => {
    const post = posts.find(p => p.id === postId);
    if (post?.user_has_shared) {
      alert('You have already shared this post!');
      return;
    }

    setCurrentSharingPost({ id: postId, content: postContent });
    setShareDialogOpen(true);
  };

  const handleSharePost = async (caption: string, method: "platform" | "copy" = "platform") => {
    if (!currentSharingPost) return;

    setSharingId(currentSharingPost.id);
    setShareDialogOpen(false);

    try {
      if (method === "copy") {
        const postUrl = `${window.location.origin}/posts/${currentSharingPost.id}`;
        await navigator.clipboard.writeText(postUrl);
        console.log("✅ Link copied to clipboard:", currentSharingPost.id);
        alert("Post link copied to clipboard!");
      } else {
        await sharePost(currentSharingPost.id, caption);
        console.log("✅ Post shared successfully:", currentSharingPost.id);
      }
    } catch (error) {
      console.error("❌ Error sharing post:", error);
      alert(method === "copy" ? "Failed to copy link. Please try again." : "Failed to share post.");
    } finally {
      setSharingId(null);
      setCurrentSharingPost(null);
    }
  };

  const toggleComments = (postId: string) => {
    console.log('🎯 Toggling comments for post:', postId);
    setExpandedPostId(expandedPostId === postId ? null : postId);
  };

  // NEW: Video control functions
  const toggleVideoPlayback = async (postId: string) => {
    const video = videoRefs[postId];
    if (!video) return;

    try {
      if (playingVideoId === postId) {
        video.pause();
        setPlayingVideoId(null);
      } else {
        setLoadingVideoId(postId);
        if (playingVideoId && videoRefs[playingVideoId]) {
          videoRefs[playingVideoId]?.pause();
        }
        await video.play();
        setPlayingVideoId(postId);
      }
    } catch (error) {
      console.error('Error playing video:', error);
    } finally {
      setLoadingVideoId(null);
    }
  };

  const toggleMuteVideo = (postId: string) => {
    const video = videoRefs[postId];
    if (!video) return;

    video.muted = !video.muted;
    setMutedVideos(prev => ({
      ...prev,
      [postId]: video.muted
    }));
  };

  const handleVideoEnd = (postId: string) => {
    setPlayingVideoId(null);
    const video = videoRefs[postId];
    if (video) {
      video.currentTime = 0;
    }
  };

  const handleVideoLoad = (postId: string) => {
    setLoadingVideoId(null);
  };

  // Helper: format date
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

  // Mood color helper
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

  // ADD THIS MISSING FUNCTION:
  const getContentTypeBadge = (post: any) => {
    if (!post.content_type || post.content_type === 'text') return null;

    const badgeConfig = {
      audio: { label: '🎵 Audio', color: 'bg-blue-100 text-blue-800 border border-blue-200' },
      video: { label: '🎬 Video', color: 'bg-purple-100 text-purple-800 border border-purple-200' },
      image: { label: '🖼️ Image', color: 'bg-green-100 text-green-800 border border-green-200' },
      journal: { label: '📔 Journal', color: 'bg-orange-100 text-orange-800 border border-orange-200' }
    };

    const config = badgeConfig[post.content_type as keyof typeof badgeConfig];
    if (!config) return null;

    return (
      <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ml-2 ${config.color}`}>
        {config.label}
      </span>
    );
  };

  // Function to render post content with clickable shared post links
  const renderPostContent = (content: string, postId: string) => {
    const originalPostMatch = content.match(/\[original_post:([a-f0-9-]+)\]/);

    if (originalPostMatch) {
      const originalPostId = originalPostMatch[1];
      const contentWithoutMarker = content.replace(/\[original_post:[a-f0-9-]+\]/, '');

      return (
        <div>
          {contentWithoutMarker.split('\n').map((line, index) => {
            if (line.includes('Shared from')) {
              return (
                <div key={index} className="mt-2">
                  {line.split('Shared from').map((part, partIndex) => {
                    if (partIndex === 0) return part;
                    return (
                      <span key={partIndex}>
                        <button
                          onClick={() => setViewingPostId(originalPostId)}
                          className="text-blue-600 hover:text-blue-800 hover:underline font-medium cursor-pointer"
                        >
                          Shared from{part}
                        </button>
                      </span>
                    );
                  })}
                </div>
              );
            }
            return <div key={index}>{line}</div>;
          })}
        </div>
      );
    }
    return content.split('\n').map((line, index) => (
      <div key={index}>{line}</div>
    ));
  };

  // NEW: Function to render media attachments
  const renderMediaAttachments = (post: any) => {
    // Check for audio posts
    if (post.audio_url && post.content_type === 'audio') {
      return (
        <div className="mt-3">
          <AudioPlayer src={post.audio_url} title="Audio post" />
        </div>
      );
    }

    // FIXED: Check for video posts with professional styling
    if (post.video_url && post.content_type === 'video') {
      return (
        <div className="mt-3">
          <div className="relative bg-black rounded-xl overflow-hidden shadow-lg max-w-2xl mx-auto">
            <video
              ref={(el) => { videoRefs[post.id] = el; }}
              src={post.video_url}
              className="w-full h-auto max-h-96 object-contain"
              onEnded={() => handleVideoEnd(post.id)}
              onClick={() => toggleVideoPlayback(post.id)}
              poster={post.thumbnail_url}
              preload="metadata"
            />
            {/* Video Controls Overlay */}
            <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-0 hover:bg-opacity-20 transition-all duration-300 cursor-pointer">
              <button
                onClick={() => toggleVideoPlayback(post.id)}
                className="bg-black bg-opacity-60 hover:bg-opacity-80 rounded-full p-4 transition-all duration-200 transform hover:scale-110"
              >
                {playingVideoId === post.id ? (
                  <Pause className="h-8 w-8 text-white" />
                ) : (
                  <Play className="h-8 w-8 text-white ml-1" />
                )}
              </button>
            </div>

            {/* Video Info Bar */}
            <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black to-transparent p-4">
              <div className="flex justify-between items-center">
                {post.video_duration && (
                  <div className="bg-black bg-opacity-70 text-white text-sm px-2 py-1 rounded">
                    {Math.floor(post.video_duration / 60)}:{(post.video_duration % 60).toString().padStart(2, '0')}
                  </div>
                )}
                {/* Video Quality Info */}
                {(post.video_width && post.video_height) && (
                  <div className="text-white text-sm bg-black bg-opacity-50 px-2 py-1 rounded">
                    {post.video_width}×{post.video_height}
                  </div>
                )}
              </div>
            </div>

            {/* Loading State */}
            {loadingVideoId === post.id && (
              <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50">
                <Loader2 className="h-8 w-8 text-white animate-spin" />
              </div>
            )}
          </div>

          {/* Video Controls Bar (Optional - for more controls) */}
          <div className="flex justify-center mt-2 space-x-4">
            <button
              onClick={() => toggleVideoPlayback(post.id)}
              className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-800 transition-colors"
            >
              {playingVideoId === post.id ? (
                <>
                  <Pause className="h-4 w-4" />
                  Pause
                </>
              ) : (
                <>
                  <Play className="h-4 w-4" />
                  Play
                </>
              )}
            </button>

            <button
              onClick={() => toggleMuteVideo(post.id)}
              className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-800 transition-colors"
            >
              {mutedVideos[post.id] ? (
                <>
                  <VolumeX className="h-4 w-4" />
                  Unmute
                </>
              ) : (
                <>
                  <Volume2 className="h-4 w-4" />
                  Mute
                </>
              )}
            </button>
          </div>
        </div>
      );
    }

    // FIXED: Check for image posts (images are text posts with image_url)
    if (post.image_url) {
      return (
        <div className="mt-3">
          <div className="bg-gray-50 rounded-lg border overflow-hidden max-w-2xl mx-auto">
            <img
              src={post.image_url}
              alt="Post image"
              className="w-full h-auto max-h-96 object-contain"
              loading="lazy"
              onError={(e) => {
                console.error('Failed to load image:', post.image_url);
                (e.target as HTMLImageElement).style.display = 'none';
              }}
            />
          </div>
        </div>
      );
    }

    return null;
  };

  return (
    <div className="space-y-6">
      {/* SHARE DIALOG */}
      <ShareDialog
        isOpen={shareDialogOpen}
        onClose={() => setShareDialogOpen(false)}
        onShare={(caption, method) => handleSharePost(caption, method)}
        postContent={currentSharingPost?.content || ''}
        isLoading={sharingId !== null}
      />

      {/* POST VIEW MODAL */}
      <PostView
        postId={viewingPostId || ''}
        isOpen={viewingPostId !== null}
        onClose={() => setViewingPostId(null)}
      />

      {/* ADD FILTER COMPONENT HERE */}
      <PostsFilter
        onFilterChange={handleFilterChange}
        currentFilters={currentFilters}
      />

      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Community Posts</h2>
          <p className="text-gray-600 mt-1">
            {posts.length} {posts.length === 1 ? 'post' : 'posts'}
            {currentFilters.mood && ` • Filtered by ${currentFilters.mood} mood`}
            {currentFilters.visibility && ` • ${currentFilters.visibility} only`}
            {currentFilters.content_type && ` • ${currentFilters.content_type} posts`}
          </p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={isLoading}
          className="flex items-center gap-2 border border-gray-300 px-4 py-2 rounded-lg hover:bg-gray-50 disabled:opacity-50 transition-colors"
        >
          {isLoading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <RefreshCw className="h-4 w-4" />
          )}
          Refresh
        </button>
      </div>

      {/* Posts List */}
      {posts.length === 0 ? (
        <div className="bg-white rounded-lg border-2 border-dashed p-8 text-center">
          <div className="max-w-md mx-auto">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              {currentFilters.mood || currentFilters.visibility || currentFilters.content_type ? 'No matching posts' : 'No posts yet'}
            </h3>
            <p className="text-gray-600 mb-4">
              {currentFilters.mood || currentFilters.visibility || currentFilters.content_type
                ? 'Try changing your filters to see more posts.'
                : 'Be the first to share your thoughts and start the conversation.'}
            </p>
            {(currentFilters.mood || currentFilters.visibility || currentFilters.content_type) && (
              <button
                onClick={() => handleFilterChange({ skip: 0, limit: 100 })}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                Clear Filters
              </button>
            )}
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {posts.map((post) => (
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
                    <div className="flex items-center">
                      <p className="font-medium text-sm">
                        {post.is_anonymous ? 'Anonymous' : post.username || 'User'}
                      </p>
                      {getContentTypeBadge(post)}
                    </div>
                    <p className="text-xs text-gray-500">
                      {formatDate(post.created_at)}
                      {post.visibility === 'private' && ' · 🔒 Private'}
                      {post.visibility === 'support_group' && ' · 👥 Support Group'}
                    </p>
                  </div>
                </div>

                {/* Post Actions Menu */}
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
                        <button
                          onClick={() => setActiveMenu(null)}
                          className="flex items-center gap-2 w-full px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 rounded-b-lg transition-colors"
                        >
                          <Edit3 className="h-3 w-3" />
                          Edit
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Post Content */}
              <div className="px-4 py-2">
                <p className="text-gray-800 whitespace-pre-wrap">
                  {renderPostContent(post.content, post.id)}
                </p>

                {/* Mood Badge */}
                {post.mood && (
                  <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium mt-3 ${getMoodColor(post.mood)}`}>
                    {post.mood}
                  </span>
                )}

                {/* Media Attachments */}
                {renderMediaAttachments(post)}
              </div>

              {/* Post Footer - Actions */}
              <div className="px-4 py-3 border-t">
                <div className="flex items-center justify-between">
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
                      onClick={() => handleShareClick(post.id, post.content)}
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

                  {/* Save Button */}
                  <button
                    onClick={() => handleSavePost(post.id)}
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
                      <BookmarkCheck className="h-5 w-5 fill-current" />
                    ) : (
                      <Bookmark className="h-5 w-5" />
                    )}
                    <span className="font-medium">{post.user_has_saved ? 'Saved' : 'Save'}</span>
                  </button>
                </div>
              </div>

              {/* Comments Section */}
              {expandedPostId === post.id && (
                <div className="border-t bg-gray-50 animate-in fade-in duration-300">
                  <div className="p-4 space-y-4">
                    <div className="flex items-center justify-between">
                      <h4 className="font-semibold text-gray-900">Comments</h4>
                      <span className="text-sm text-gray-500">
                        {post.comment_count || 0} {post.comment_count === 1 ? 'comment' : 'comments'}
                      </span>
                    </div>

                    {/* Comment Form */}
                    <CommentForm
                      postId={post.id}
                      onCommentAdded={() => {
                        console.log('✅ New comment added, should refresh comments list');
                      }}
                    />

                    {/* Comments List */}
                    <CommentsList postId={post.id} />
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
          <span className="ml-2 text-gray-600">Refreshing posts...</span>
        </div>
      )}
    </div>
  );
}
