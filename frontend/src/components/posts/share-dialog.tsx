'use client';

import { useState } from 'react';

interface ShareDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onShare: (caption: string) => void;
  postContent: string;
  isLoading?: boolean;
}

export function ShareDialog({ 
  isOpen, 
  onClose, 
  onShare, 
  postContent, 
  isLoading = false 
}: ShareDialogProps) {
  const [caption, setCaption] = useState('');

  const handleShare = () => {
    onShare(caption);
    setCaption(''); // Reset for next time
  };

  const handleClose = () => {
    setCaption(''); // Reset when closing
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-md w-full mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-lg font-semibold">Share Post</h2>
          <button
            onClick={handleClose}
            className="text-gray-500 hover:text-gray-700 text-xl"
          >
            ×
          </button>
        </div>
        
        <div className="p-4 space-y-4">
          {/* Original Post Preview */}
          <div className="bg-gray-50 p-3 rounded-lg border">
            <p className="text-sm text-gray-600 mb-1">Original post:</p>
            <p className="text-sm line-clamp-3">{postContent}</p>
          </div>

          {/* Caption Input */}
          <div className="space-y-2">
            <label htmlFor="caption" className="text-sm font-medium block">
              Add your thoughts (optional)
            </label>
            <textarea
              id="caption"
              placeholder="What's on your mind?"
              value={caption}
              onChange={(e) => setCaption(e.target.value)}
              className="w-full min-h-[100px] p-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              maxLength={500}
            />
            <div className="text-xs text-gray-500 text-right">
              {caption.length}/500
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-2 pt-4">
            <button
              onClick={handleClose}
              disabled={isLoading}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleShare}
              disabled={isLoading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {isLoading ? 'Sharing...' : 'Share Post'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
