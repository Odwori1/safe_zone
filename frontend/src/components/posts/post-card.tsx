'use client';

import { PostResponse } from '@/types/posts';
import { usePostsStore } from '@/stores/posts-store';
import { useAuth } from '@/hooks/use-auth';
import { HappyIcon, SadIcon, TiredIcon, CalmIcon, AnxiousIcon, AngryIcon, NeutralIcon, ThoughtfulIcon } from '@/components/ui/icons';

interface PostCardProps {
  post: PostResponse;
}

export default function PostCard({ post }: PostCardProps) {
  const { deletePost, isLoading } = usePostsStore();
  const { user } = useAuth();

  const isOwnPost = user?.id === post.user_id;

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this post?')) {
      await deletePost(post.id);
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
    } else {
      return date.toLocaleDateString();
    }
  };

  const getVisibilityIcon = (visibility: string) => {
    switch (visibility) {
      case 'public': return '🌍';
      case 'private': return '🔒';
      case 'support_group': return '🤝';
      default: return '🌍';
    }
  };

  const getMoodIcon = (mood: string) => {
    const moodIcons: { [key: string]: any } = {
      'Happy': HappyIcon,
      'Sad': SadIcon,
      'Tired': TiredIcon,
      'Calm': CalmIcon,
      'Anxious': AnxiousIcon,
      'Angry': AngryIcon,
      'Neutral': NeutralIcon,
      'Thoughtful': ThoughtfulIcon,
    };
    
    const IconComponent = moodIcons[mood] || NeutralIcon;
    return <IconComponent className="w-4 h-4" />;
  };

  const getMoodColor = (mood: string) => {
    const moodColors: { [key: string]: string } = {
      'Happy': 'text-green-600 bg-green-50',
      'Sad': 'text-blue-600 bg-blue-50',
      'Tired': 'text-gray-600 bg-gray-50',
      'Calm': 'text-purple-600 bg-purple-50',
      'Anxious': 'text-yellow-600 bg-yellow-50',
      'Angry': 'text-red-600 bg-red-50',
      'Neutral': 'text-gray-500 bg-gray-50',
      'Thoughtful': 'text-indigo-600 bg-indigo-50',
    };
    
    return moodColors[mood] || 'text-gray-500 bg-gray-50';
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm hover:shadow-md transition-shadow">
      {/* Post Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-start space-x-3">
          <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center text-white font-semibold shadow-sm">
            {post.is_anonymous ? '?' : (post.username?.[0]?.toUpperCase() || 'U')}
          </div>
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-1">
              <span className="font-semibold text-gray-900">
                {post.is_anonymous ? 'Anonymous' : post.username || 'Unknown User'}
              </span>
              {post.mood && (
                <span className={`inline-flex items-center space-x-1 px-2 py-1 rounded-full text-xs ${getMoodColor(post.mood)}`}>
                  {getMoodIcon(post.mood)}
                  <span>{post.mood}</span>
                </span>
              )}
            </div>
            <div className="flex items-center space-x-3 text-sm text-gray-500">
              <span>{formatDate(post.created_at)}</span>
              <span>•</span>
              <span className="flex items-center space-x-1">
                <span>{getVisibilityIcon(post.visibility)}</span>
                <span className="capitalize">{post.visibility.replace('_', ' ')}</span>
              </span>
              <span>•</span>
              <span className={`px-2 py-1 rounded-full text-xs ${
                post.moderation_status === 'approved' 
                  ? 'bg-green-100 text-green-800'
                  : post.moderation_status === 'pending'
                  ? 'bg-yellow-100 text-yellow-800'
                  : 'bg-red-100 text-red-800'
              }`}>
                {post.moderation_status}
              </span>
            </div>
          </div>
        </div>

        {/* Delete Button for Own Posts */}
        {isOwnPost && (
          <button
            onClick={handleDelete}
            disabled={isLoading}
            className="text-gray-400 hover:text-red-500 disabled:opacity-50 transition-colors p-1 rounded"
            title="Delete post"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        )}
      </div>

      {/* Post Content */}
      <div className="mb-4">
        <p className="text-gray-900 whitespace-pre-wrap leading-relaxed text-[15px]">
          {post.content}
        </p>
      </div>

      {/* Post Actions */}
      <div className="flex items-center justify-between pt-4 border-t border-gray-100">
        <div className="flex items-center space-x-4">
          <button className="flex items-center space-x-2 text-gray-500 hover:text-red-600 transition-colors group">
            <div className="p-1 rounded group-hover:bg-red-50 transition-colors">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </div>
            <span className="text-sm font-medium">Support</span>
          </button>
          
          <button className="flex items-center space-x-2 text-gray-500 hover:text-green-600 transition-colors group">
            <div className="p-1 rounded group-hover:bg-green-50 transition-colors">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <span className="text-sm font-medium">Comment</span>
          </button>
          
          <button className="flex items-center space-x-2 text-gray-500 hover:text-purple-600 transition-colors group">
            <div className="p-1 rounded group-hover:bg-purple-50 transition-colors">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
              </svg>
            </div>
            <span className="text-sm font-medium">Save</span>
          </button>
        </div>

        <div className="text-xs text-gray-400 capitalize">
          {post.content_type}
        </div>
      </div>
    </div>
  );
}
