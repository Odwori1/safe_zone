'use client';

import { useState } from 'react';
import { PostResponse } from '@/types/posts';
import { usePostsStore } from '@/stores/posts-store';

interface PostActionsProps {
  post: PostResponse;
  onLike?: (postId: string) => void;
  onComment?: (postId: string) => void;
  onSave?: (postId: string) => void;
  onShare?: (postId: string, method?: 'platform' | 'copy') => void;
}

/* Small inline SVG icon components — avoids external icon import issues */
function IconHeart({ filled = false }: { filled?: boolean }) {
  return (
    <svg viewBox="0 0 24 24" className="w-4 h-4" aria-hidden>
      {filled ? (
        <path d="M12 21s-7.5-4.9-9.2-7.2C1.2 11.4 2.2 7.8 5 6c1.7-1 3.7-.9 4 0 .3-.9 2.3-1 4-.1 2.8 1.8 3.8 5.4 2.2 7.8C19.5 16.1 12 21 12 21z" />
      ) : (
        <path d="M12.1 8.64l-.1.1-.11-.1C10.14 6.87 7 7.4 7 10.28c0 1.81.92 3.16 2.11 4.26C10.79 15.9 12 17 12 17s1.21-1.1 2.89-2.46A5.3 5.3 0 0 0 17 10.28c0-2.88-3.14-3.41-4.9-1.64z" fill="none" stroke="currentColor" strokeWidth="1.2" />
      )}
    </svg>
  );
}

function IconComment() {
  return (
    <svg viewBox="0 0 24 24" className="w-4 h-4" aria-hidden>
      <path d="M21 15a2 2 0 0 1-2 2H8l-5 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" fill="none" stroke="currentColor" strokeWidth="1.2" />
    </svg>
  );
}

function IconShare() {
  return (
    <svg viewBox="0 0 24 24" className="w-4 h-4" aria-hidden>
      <path d="M4 12v7a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-7" fill="none" stroke="currentColor" strokeWidth="1.2" />
      <path d="M16 6l-4-4-4 4" fill="none" stroke="currentColor" strokeWidth="1.2" />
      <path d="M12 2v14" fill="none" stroke="currentColor" strokeWidth="1.2" />
    </svg>
  );
}

function IconBookmark({ filled = false }: { filled?: boolean }) {
  return (
    <svg viewBox="0 0 24 24" className="w-4 h-4" aria-hidden>
      {filled ? (
        <path d="M6 2h12v20l-6-4-6 4V2z" />
      ) : (
        <path d="M6 2h12v20l-6-4-6 4V2z" fill="none" stroke="currentColor" strokeWidth="1.2" />
      )}
    </svg>
  );
}

export default function PostActions({ post, onLike, onComment, onSave, onShare }: PostActionsProps) {
  const [isLiked, setIsLiked] = useState<boolean>(post.user_has_liked || false);
  const [isSaved, setIsSaved] = useState<boolean>(post.user_has_saved || false);
  const [isSharing, setIsSharing] = useState<boolean>(false);

  // local share UI state so the count and button update immediately
  const [shareCount, setShareCount] = useState<number>(post.share_count || 0);
  const [userSharedLocal, setUserSharedLocal] = useState<boolean>(post.user_has_shared || false);

  const sharePost = usePostsStore((state) => state.sharePost);
  const likePost = usePostsStore((state) => state.likePost);
  const unlikePost = usePostsStore((state) => state.unlikePost);
  const savePost = usePostsStore((state) => state.savePost);
  const unsavePost = usePostsStore((state) => state.unsavePost);

  const handleLike = async () => {
    try {
      if (isLiked) {
        if (unlikePost) await unlikePost(post.id);
        setIsLiked(false);
      } else {
        if (likePost) await likePost(post.id);
        setIsLiked(true);
      }
      onLike?.(post.id);
    } catch (error) {
      console.error('Error toggling like:', error);
    }
  };

  /**
   * Handles share:
   * - method 'platform' tries navigator.share first (native share),
   *   falls back to copying link to clipboard if share API is not available or fails.
   * - method 'copy' explicitly copies link to clipboard.
   *
   * After a successful share (platform or copy) we call backend sharePost and update UI.
   */
  const handleShare = async (method: 'platform' | 'copy' = 'platform') => {
    if (isSharing || userSharedLocal) return;

    setIsSharing(true);
    try {
      const postUrl = `${typeof window !== 'undefined' ? window.location.origin : ''}/posts/${post.id}`;
      let sharedSucceeded = false;

      if (method === 'platform') {
        // Try the Web Share API first
        if (typeof navigator !== 'undefined' && (navigator as any).share) {
          try {
            await (navigator as any).share({
              title: document?.title || 'Post',
              text: (post as any).excerpt ?? undefined,
              url: postUrl,
            });
            sharedSucceeded = true;
            onShare?.(post.id, 'platform');
          } catch (err) {
            // native share failed or was cancelled — fall back to copy
            console.info('Native share failed or cancelled, falling back to copy.', err);
          }
        }
      }

      if (!sharedSucceeded && method === 'copy') {
        // explicit copy flow
        if (typeof navigator !== 'undefined' && navigator.clipboard) {
          await navigator.clipboard.writeText(postUrl);
          sharedSucceeded = true;
          onShare?.(post.id, 'copy');
          console.log('✅ Link copied to clipboard:', postUrl);
        } else {
          throw new Error('Clipboard API not available');
        }
      }

      // If platform method was attempted but didn't succeed with native share,
      // try copy as final fallback
      if (!sharedSucceeded && method === 'platform') {
        if (typeof navigator !== 'undefined' && navigator.clipboard) {
          try {
            await navigator.clipboard.writeText(postUrl);
            sharedSucceeded = true;
            onShare?.(post.id, 'copy');
            console.log('✅ Fallback: link copied to clipboard:', postUrl);
          } catch (err) {
            console.error('Fallback copy failed:', err);
          }
        }
      }

      // If any share action succeeded, notify backend and update local UI
      if (sharedSucceeded) {
        try {
          if (sharePost) await sharePost(post.id);
        } catch (err) {
          // backend share call failing shouldn't block UI update but log it
          console.error('Error notifying backend about share:', err);
        }
        setUserSharedLocal(true);
        setShareCount((c) => c + 1);
      }
    } catch (error) {
      console.error('Error sharing post:', error);
      if (method === 'copy') {
        // only show a browser alert as fallback — in real app prefer a toast
        alert('Failed to copy link. Please try again.');
      }
    } finally {
      setIsSharing(false);
    }
  };

  const handleSave = async () => {
    try {
      if (isSaved) {
        if (unsavePost) await unsavePost(post.id);
        setIsSaved(false);
      } else {
        if (savePost) await savePost(post.id);
        setIsSaved(true);
      }
      onSave?.(post.id);
    } catch (error) {
      console.error('Error toggling save:', error);
    }
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
          aria-pressed={isLiked}
          type="button"
        >
          <IconHeart filled={isLiked} />
          <span className="text-sm">{post.like_count ?? 0}</span>
        </button>

        {/* Comment Button */}
        <button
          onClick={() => onComment?.(post.id)}
          className="flex items-center space-x-2 text-gray-500 hover:text-green-600 transition-colors"
          type="button"
        >
          <IconComment />
          <span className="text-sm">{post.comment_count ?? 0}</span>
        </button>

        {/* Share Button (platform) */}
        <button
          onClick={() => handleShare('platform')}
          disabled={isSharing || userSharedLocal}
          className={`flex items-center space-x-2 transition-colors ${
            userSharedLocal ? 'text-blue-500 cursor-not-allowed' : 'text-gray-500 hover:text-blue-500'
          } ${isSharing ? 'opacity-50' : ''}`}
          aria-pressed={userSharedLocal}
          title={userSharedLocal ? 'Already shared' : 'Share post'}
          type="button"
        >
          <IconShare />
          <span className="text-sm">{shareCount}</span>
        </button>

        {/* Quick Copy Link (explicit copy) */}
        <button
          onClick={() => handleShare('copy')}
          disabled={isSharing}
          className={`flex items-center space-x-2 text-gray-500 hover:text-blue-500 transition-colors ${isSharing ? 'opacity-50' : ''}`}
          title="Copy post link"
          type="button"
        >
          <IconShare />
          <span className="sr-only">Copy link</span>
        </button>

        {/* Save Button */}
        <button
          onClick={handleSave}
          disabled={isSharing}
          className={`flex items-center space-x-2 transition-colors ${
            isSaved ? 'text-purple-500' : 'text-gray-500 hover:text-purple-500'
          } ${isSharing ? 'opacity-50' : ''}`}
          aria-pressed={isSaved}
          type="button"
        >
          <IconBookmark filled={isSaved} />
          <span className="text-sm">{isSaved ? 'Saved' : 'Save'}</span>
        </button>
      </div>

      <div className="text-xs text-gray-400 capitalize">{post.content_type}</div>
    </div>
  );
}

