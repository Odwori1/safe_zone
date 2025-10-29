'use client';

import { useState } from 'react';
import { CommentResponse } from '@/types/comments';
import { useAuth } from '@/hooks/use-auth';
import { useCommentsStore } from '@/stores/comments-store';
import { Trash2, Edit3, MoreVertical, Loader2, Heart, MessageCircle, Reply } from 'lucide-react';
import CommentForm from './comment-form';

interface CommentItemProps {
  comment: CommentResponse;
  postId: string;
  isReply?: boolean;
}

export default function CommentItem({ comment, postId, isReply = false }: CommentItemProps) {
  const { user } = useAuth();
  const { deleteComment, likeComment, unlikeComment, isLoading } = useCommentsStore();
  const [isDeleting, setIsDeleting] = useState(false);
  const [isLiking, setIsLiking] = useState(false);
  const [activeMenu, setActiveMenu] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [showReplyForm, setShowReplyForm] = useState(false);
  const [editedContent, setEditedContent] = useState(comment.content);

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

  const handleDelete = async () => {
    setIsDeleting(true);
    setActiveMenu(false);
    try {
      await deleteComment(comment.id);
    } finally {
      setIsDeleting(false);
    }
  };

  const handleLike = async () => {
    if (isLiking) return;
    
    setIsLiking(true);
    try {
      if (comment.user_has_liked) {
        await unlikeComment(comment.id);
      } else {
        await likeComment(comment.id);
      }
    } finally {
      setIsLiking(false);
    }
  };

  const handleEdit = () => {
    setIsEditing(true);
    setActiveMenu(false);
  };

  const handleSaveEdit = async () => {
    // TODO: Implement edit functionality
    setIsEditing(false);
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
    setEditedContent(comment.content);
  };

  const handleReply = () => {
    setShowReplyForm(true);
  };

  const handleReplyAdded = () => {
    setShowReplyForm(false);
    // Refresh comments to show the new reply
    // This will be handled by parent component
  };

  const isOwnComment = user && comment.user_id === user.id;

  return (
    <div className={`bg-white border rounded-lg p-4 mb-3 ${isReply ? 'ml-6 border-l-2 border-l-blue-200' : ''}`}>
      {/* Comment Header */}
      <div className="flex justify-between items-start mb-2">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
            <span className="text-xs font-medium text-white">
              {comment.is_anonymous ? 'A' : (comment.username?.[0]?.toUpperCase() || 'U')}
            </span>
          </div>
          <div>
            <p className="text-sm font-medium">
              {comment.is_anonymous ? 'Anonymous' : comment.username || 'User'}
            </p>
            <p className="text-xs text-gray-500">
              {formatDate(comment.created_at)}
            </p>
          </div>
        </div>

        {/* Comment Actions Menu */}
        {isOwnComment && (
          <div className="relative">
            <button
              onClick={() => setActiveMenu(!activeMenu)}
              className="p-1 rounded hover:bg-gray-100 transition-colors"
            >
              <MoreVertical className="h-4 w-4" />
            </button>

            {activeMenu && (
              <div className="absolute right-0 top-8 bg-white border rounded-lg shadow-lg z-10 min-w-[120px]">
                <button
                  onClick={handleEdit}
                  className="flex items-center gap-2 w-full px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 rounded-t-lg transition-colors"
                >
                  <Edit3 className="h-3 w-3" />
                  Edit
                </button>
                <button
                  onClick={handleDelete}
                  disabled={isDeleting}
                  className="flex items-center gap-2 w-full px-3 py-2 text-sm text-red-600 hover:bg-red-50 disabled:opacity-50 rounded-b-lg transition-colors"
                >
                  {isDeleting ? (
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

      {/* Comment Content */}
      <div className="mb-3">
        {isEditing ? (
          <div className="space-y-2">
            <textarea
              value={editedContent}
              onChange={(e) => setEditedContent(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={3}
            />
            <div className="flex gap-2">
              <button
                onClick={handleSaveEdit}
                className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700"
              >
                Save
              </button>
              <button
                onClick={handleCancelEdit}
                className="bg-gray-300 text-gray-700 px-3 py-1 rounded text-sm hover:bg-gray-400"
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <p className="text-gray-800 text-sm whitespace-pre-wrap">{comment.content}</p>
        )}
      </div>

      {/* Comment Footer */}
      <div className="flex items-center gap-4 text-xs text-gray-600">
        {/* Like Button - NOW ACTIVE */}
        <button
          onClick={handleLike}
          disabled={isLiking}
          className={`flex items-center gap-1 transition-colors ${
            comment.user_has_liked
              ? 'text-red-600 hover:text-red-700'
              : 'text-gray-600 hover:text-gray-800'
          } disabled:opacity-50`}
        >
          {isLiking ? (
            <Loader2 className="h-3 w-3 animate-spin" />
          ) : (
            <Heart
              className={`h-3 w-3 ${comment.user_has_liked ? 'fill-current' : ''}`}
            />
          )}
          <span>{comment.like_count || 0}</span>
        </button>

        {!isReply && (
          <button
            onClick={handleReply}
            className="flex items-center gap-1 hover:text-blue-600 transition-colors"
          >
            <Reply className="h-3 w-3" />
            <span>Reply</span>
          </button>
        )}
      </div>

      {/* Reply Form */}
      {showReplyForm && (
        <div className="mt-3 border-t pt-3">
          <CommentForm
            postId={postId}
            parentCommentId={comment.id}
            onCommentAdded={handleReplyAdded}
            autoFocus={true}
          />
        </div>
      )}

      {/* Nested Replies */}
      {comment.replies && comment.replies.length > 0 && (
        <div className="mt-3 space-y-2">
          {comment.replies.map((reply) => (
            <CommentItem
              key={reply.id}
              comment={reply}
              postId={postId}
              isReply={true}
            />
          ))}
        </div>
      )}
    </div>
  );
}
