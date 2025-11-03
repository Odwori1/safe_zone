'use client';

import { useState } from 'react';
import { PostResponse } from '@/types/posts';
import { usePostsStore } from '@/stores/posts-store';
import { Share2, Heart, MessageCircle, Bookmark } from 'lucide-react';

interface PostActionsProps {
  post: PostResponse;
  onLike?: (postId: string) => void;
  onComment?: (postId: string) => void;
  onSave?: (postId: string) => void;
  onShare?: (postId: string) => void; // ADD THIS
}

export default function PostActions({ post, onLike, onComment, onSave, onShare }: PostActionsProps) {
  const [isLiked, setIsLiked] = useState(post.user_has_liked || false);
  const [isSaved, setIsSaved] = useState(false);
  const [isSharing, setIsSharing] = useState(false);
  
  const sharePost = usePostsStore((state) => state.sharePost);
  const likePost = usePostsStore((state) => state.likePost);
  const unlikePost = usePostsStore((state) => state.unlikePost);

  const handleLike = async () => {
    try {
      if (isLiked) {
        await unlikePost(post.id);
        setIsLiked(false);
      } else {
        await likePost(post.id);
        setIsLiked(true);
      }
      onLike?.(post.id);
    } catch (error) {
      console.error('Error toggling like:', error);
    }
  };

  const handleShare = async () => {
    if (isSharing || post.user_has_shared) return;
    
    setIsSharing(true);
    try {
      await sharePost(post.id);
      onShare?.(post.id);
    } catch (error) {
      console.error('Error sharing post:', error);
    } finally {
      setIsSharing(false);
    }
  };

  const handleSave = () => {
    setIsSaved(!isSaved);
    onSave?.(post.id);
  };

  return (
    <div className="flex items-center justify-between pt-4 border-t border-gray-100">
      <div className="flex items-center space-x-4">
        {/* Like Button */}
        <button
          onClick={handleLike}
          className={`flex items-center space-x-2 transition-colors ${
            isLiked ? 'text-red-500' : 'text-gray-500 hover:text-red-500'
          }`}
          disabled={!likePost}
        >
          <Heart className={`w-4 h-4 ${isLiked ? 'fill-current' : ''}`} />
          <span className="text-sm">
            {post.like_count || 0}
          </span>
        </button>

        {/* Comment Button */}
        <button
          onClick={() => onComment?.(post.id)}
          className="flex items-center space-x-2 text-gray-500 hover:text-green-600 transition-colors"
        >
          <MessageCircle className="w-4 h-4" />
          <span className="text-sm">
            {post.comment_count || 0}
          </span>
        </button>

        {/* Share Button */}
        <button
          onClick={handleShare}
          disabled={isSharing || post.user_has_shared}
          className={`flex items-center space-x-2 transition-colors ${
            post.user_has_shared 
              ? 'text-blue-500 cursor-not-allowed' 
              : 'text-gray-500 hover:text-blue-500'
          } ${isSharing ? 'opacity-50' : ''}`}
        >
          <Share2 className="w-4 h-4" />
          <span className="text-sm">
            {post.share_count || 0}
          </span>
        </button>

        {/* Save Button */}
        <button
          onClick={handleSave}
          className={`flex items-center space-x-2 transition-colors ${
            isSaved ? 'text-purple-500' : 'text-gray-500 hover:text-purple-500'
          }`}
        >
          <Bookmark className={`w-4 h-4 ${isSaved ? 'fill-current' : ''}`} />
          <span className="text-sm">{isSaved ? 'Saved' : 'Save'}</span>
        </button>
      </div>

      <div className="text-xs text-gray-400 capitalize">
        {post.content_type}
      </div>
    </div>
  );
}
