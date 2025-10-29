'use client';

import { useState } from 'react';
import { PostResponse } from '@/types/posts';

interface PostActionsProps {
  post: PostResponse;
  onLike?: (postId: string) => void;
  onComment?: (postId: string) => void;
  onSave?: (postId: string) => void;
}

export default function PostActions({ post, onLike, onComment, onSave }: PostActionsProps) {
  const [isLiked, setIsLiked] = useState(false);
  const [isSaved, setIsSaved] = useState(false);

  const handleLike = () => {
    setIsLiked(!isLiked);
    onLike?.(post.id);
  };

  const handleSave = () => {
    setIsSaved(!isSaved);
    onSave?.(post.id);
  };

  return (
    <div className="flex items-center justify-between pt-4 border-t border-gray-100">
      <div className="flex items-center space-x-4">
        <button 
          onClick={handleLike}
          className={`flex items-center space-x-2 transition-colors ${
            isLiked ? 'text-red-500' : 'text-gray-500 hover:text-red-500'
          }`}
        >
          <span>{isLiked ? '❤️' : '🤍'}</span>
          <span className="text-sm">Like</span>
        </button>
        
        <button 
          onClick={() => onComment?.(post.id)}
          className="flex items-center space-x-2 text-gray-500 hover:text-green-600 transition-colors"
        >
          <span>💬</span>
          <span className="text-sm">Comment</span>
        </button>
        
        <button 
          onClick={handleSave}
          className={`flex items-center space-x-2 transition-colors ${
            isSaved ? 'text-purple-500' : 'text-gray-500 hover:text-purple-500'
          }`}
        >
          <span>{isSaved ? '🔖' : '📑'}</span>
          <span className="text-sm">{isSaved ? 'Saved' : 'Save'}</span>
        </button>
      </div>

      <div className="text-xs text-gray-400 capitalize">
        {post.content_type}
      </div>
    </div>
  );
}
