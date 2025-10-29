'use client';

import { useState } from 'react';
import { useCommentsStore } from '@/stores/comments-store';
import { useAuth } from '@/hooks/use-auth';
import { Send, Loader2, Eye, EyeOff } from 'lucide-react';

interface CommentFormProps {
  postId: string;
  parentCommentId?: string | null;
  onCommentAdded?: () => void;
  autoFocus?: boolean;
}

export default function CommentForm({ 
  postId, 
  parentCommentId = null, 
  onCommentAdded,
  autoFocus = false 
}: CommentFormProps) {
  const { createComment, isLoading } = useCommentsStore();
  const { user } = useAuth();
  const [content, setContent] = useState('');
  const [isAnonymous, setIsAnonymous] = useState(false);
  const [charCount, setCharCount] = useState(0);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!content.trim()) return;

    try {
      await createComment({
        post_id: postId,
        content: content.trim(),
        parent_comment_id: parentCommentId,
        is_anonymous: isAnonymous,
      });

      // Reset form
      setContent('');
      setCharCount(0);
      
      // Notify parent component
      onCommentAdded?.();
      
    } catch (error) {
      console.error('Failed to create comment:', error);
    }
  };

  const handleContentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    setContent(value);
    setCharCount(value.length);
  };

  const isSubmitDisabled = !content.trim() || isLoading || charCount > 1000;

  if (!user) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-center">
        <p className="text-yellow-800 text-sm">
          Please log in to comment
        </p>
      </div>
    );
  }

  return (
    <div className="bg-gray-50 border rounded-lg p-4">
      <form onSubmit={handleSubmit} className="space-y-3">
        {/* Content Textarea */}
        <div>
          <textarea
            value={content}
            onChange={handleContentChange}
            placeholder={parentCommentId ? "Write a reply..." : "Write a comment..."}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows={3}
            maxLength={1000}
            autoFocus={autoFocus}
          />
          <div className="flex justify-between items-center mt-1">
            <p className="text-xs text-gray-500">
              {charCount}/1000 characters
            </p>
            {charCount > 800 && (
              <p className="text-xs text-orange-600">
                {1000 - charCount} characters remaining
              </p>
            )}
          </div>
        </div>

        {/* Form Footer */}
        <div className="flex justify-between items-center">
          {/* Anonymous Toggle */}
          <button
            type="button"
            onClick={() => setIsAnonymous(!isAnonymous)}
            className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-700 transition-colors"
          >
            {isAnonymous ? (
              <EyeOff className="h-4 w-4 text-purple-600" />
            ) : (
              <Eye className="h-4 w-4 text-gray-600" />
            )}
            <span className={isAnonymous ? 'text-purple-600 font-medium' : ''}>
              {isAnonymous ? 'Posting Anonymously' : 'Post Anonymously'}
            </span>
          </button>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isSubmitDisabled}
            className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Posting...
              </>
            ) : (
              <>
                <Send className="h-4 w-4" />
                {parentCommentId ? 'Reply' : 'Comment'}
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
