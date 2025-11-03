'use client';

import { useState } from 'react';
import { X, Share2, Link, MessageCircle, Users } from 'lucide-react';

interface ShareDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onShare: (caption: string, method: 'platform' | 'copy') => void;
  postContent: string;
  isLoading?: boolean;
}

export default function ShareDialog({
  isOpen,
  onClose,
  onShare,
  postContent,
  isLoading = false
}: ShareDialogProps) {
  const [caption, setCaption] = useState('');
  const [shareMethod, setShareMethod] = useState<'platform' | 'copy'>('platform');

  if (!isOpen) return null;

  const handleShare = () => {
    onShare(caption, shareMethod);
    setCaption('');
    setShareMethod('platform');
  };

  const truncateContent = (content: string, maxLength: number = 100) => {
    return content.length > maxLength ? content.substring(0, maxLength) + '...' : content;
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b flex-shrink-0">
          <div className="flex items-center gap-3">
            <Share2 className="h-6 w-6 text-blue-600" />
            <h2 className="text-xl font-semibold text-gray-900">Share Post</h2>
          </div>
          <button
            onClick={onClose}
            disabled={isLoading}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content - Scrollable area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {/* Original Post Preview */}
          <div className="bg-gray-50 rounded-lg p-4 border">
            <h3 className="text-sm font-medium text-gray-700 mb-2">Original Post:</h3>
            <p className="text-gray-600 text-sm">{truncateContent(postContent)}</p>
          </div>

          {/* Share Method Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              How would you like to share?
            </label>
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => setShareMethod('platform')}
                className={`p-4 rounded-lg border-2 text-left transition-all ${
                  shareMethod === 'platform'
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
              >
                <MessageCircle className={`h-5 w-5 mb-2 ${
                  shareMethod === 'platform' ? 'text-blue-600' : 'text-gray-600'
                }`} />
                <div className="text-sm font-medium">Share on Platform</div>
                <div className="text-xs text-gray-500 mt-1">Create a new post with your thoughts</div>
              </button>

              <button
                onClick={() => setShareMethod('copy')}
                className={`p-4 rounded-lg border-2 text-left transition-all ${
                  shareMethod === 'copy'
                    ? 'border-green-500 bg-green-50'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
              >
                <Link className={`h-5 w-5 mb-2 ${
                  shareMethod === 'copy' ? 'text-green-600' : 'text-gray-600'
                }`} />
                <div className="text-sm font-medium">Copy Link</div>
                <div className="text-xs text-gray-500 mt-1">Share the post URL</div>
              </button>
            </div>
          </div>

          {/* Caption Input (only for platform sharing) */}
          {shareMethod === 'platform' && (
            <div>
              <label htmlFor="caption" className="block text-sm font-medium text-gray-700 mb-2">
                Add your thoughts (optional)
              </label>
              <textarea
                id="caption"
                value={caption}
                onChange={(e) => setCaption(e.target.value)}
                placeholder="What are your thoughts on this post?"
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none transition-colors"
                disabled={isLoading}
              />
              <div className="flex items-center gap-2 mt-2 text-xs text-gray-500">
                <Users className="h-3 w-3" />
                <span>This will create a new post that references the original</span>
              </div>
            </div>
          )}

          {/* Share Options Preview */}
          {shareMethod === 'platform' && caption && (
            <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
              <h4 className="text-sm font-medium text-blue-800 mb-2">Preview:</h4>
              <div className="text-sm text-blue-700 space-y-2">
                <p className="font-medium">Your comment:</p>
                <p className="italic">"{caption}"</p>
                <div className="border-t border-blue-200 pt-2">
                  <p className="text-xs opacity-75">🔗 Shared from original post</p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer - Fixed at bottom */}
        <div className="border-t bg-gray-50 p-6 flex-shrink-0">
          <div className="flex gap-3">
            <button
              onClick={onClose}
              disabled={isLoading}
              className="flex-1 px-4 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors disabled:opacity-50 font-medium"
            >
              Cancel
            </button>

            <button
              onClick={handleShare}
              disabled={isLoading}
              className={`flex-1 px-4 py-3 text-white rounded-lg hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium flex items-center justify-center gap-2 ${
                shareMethod === 'platform' ? 'bg-blue-600 hover:bg-blue-700' : 'bg-green-600 hover:bg-green-700'
              }`}
            >
              {isLoading ? (
                <>
                  <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  {shareMethod === 'platform' ? 'Sharing...' : 'Copying...'}
                </>
              ) : (
                <>
                  {shareMethod === 'platform' ? (
                    <>
                      <Share2 className="h-4 w-4" />
                      Share Post
                    </>
                  ) : (
                    <>
                      <Link className="h-4 w-4" />
                      Copy Link
                    </>
                  )}
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
