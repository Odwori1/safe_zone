'use client';

import { useState } from 'react';
import { usePostsStore } from '@/stores/posts-store';
import { useAuth } from '@/hooks/use-auth';
import {
  Globe,
  Lock,
  Users,
  Eye,
  EyeOff,
  Smile,
  Loader2,
  Paperclip,
  X,
  Music,
  Video,
  Image
} from 'lucide-react';
import FileUpload from '@/components/media/file-upload';

const MOOD_OPTIONS = [
  { value: 'happy', label: '😊 Happy', color: 'text-yellow-600' },
  { value: 'calm', label: '😌 Calm', color: 'text-green-600' },
  { value: 'neutral', label: '😐 Neutral', color: 'text-blue-600' },
  { value: 'anxious', label: '😰 Anxious', color: 'text-orange-600' },
  { value: 'sad', label: '😢 Sad', color: 'text-indigo-600' },
  { value: 'angry', label: '😠 Angry', color: 'text-red-600' },
  { value: 'tired', label: '😴 Tired', color: 'text-purple-600' },
  { value: 'excited', label: '🤩 Excited', color: 'text-pink-600' },
];

const VISIBILITY_OPTIONS = [
  {
    value: 'public',
    label: 'Public',
    description: 'Visible to everyone',
    icon: Globe,
    color: 'text-green-600'
  },
  {
    value: 'private',
    label: 'Private',
    description: 'Only visible to you',
    icon: Lock,
    color: 'text-blue-600'
  },
  {
    value: 'support_group',
    label: 'Support Group',
    description: 'Visible to support groups',
    icon: Users,
    color: 'text-purple-600'
  },
];

export default function CreatePostForm() {
  const { createPost, isLoading } = usePostsStore();
  const { user } = useAuth();

  const [content, setContent] = useState('');
  const [mood, setMood] = useState('');
  const [visibility, setVisibility] = useState<'public' | 'private' | 'support_group'>('public');
  const [isAnonymous, setIsAnonymous] = useState(false);
  const [showMoodPicker, setShowMoodPicker] = useState(false);
  const [charCount, setCharCount] = useState(0);

  // New state for attached files
  const [attachedFiles, setAttachedFiles] = useState<Array<{
    fileId: string;
    url: string;
    fileType: string;
    fileName: string;
  }>>([]);

  // Function to remove attached files
  const removeAttachedFile = (fileId: string) => {
    setAttachedFiles(prev => prev.filter(file => file.fileId !== fileId));
  };

  // FIXED: Handle file uploads - accept file parameter properly
  const handleFileUploaded = (fileInfo: { fileId: string; url: string; fileType: string; fileName?: string }, file?: File) => {
    // Use file.name if available, otherwise use fileInfo.fileName or a default
    const fileName = file?.name || fileInfo.fileName || `Uploaded ${fileInfo.fileType} file`;

    setAttachedFiles(prev => [...prev, {
      fileId: fileInfo.fileId,
      url: fileInfo.url,
      fileType: fileInfo.fileType,
      fileName: fileName
    }]);
  };

  // FIXED: Updated handleSubmit to properly include file URLs in post data
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!content.trim() && attachedFiles.length === 0) return;

    try {
      // FIXED: Determine content type and include proper file URLs
      let contentType: 'text' | 'audio' | 'video' = 'text';
      let audioUrl = null;
      let videoUrl = null;
      let imageUrl = null;

      // FIXED: Handle multiple files and find the first media file
      if (attachedFiles.length > 0) {
        // Find the first image file if any
        const imageFile = attachedFiles.find(file => file.fileType === 'image');
        if (imageFile) {
          imageUrl = imageFile.url;
          contentType = 'text'; // Images are text posts with image_url
        }

        // Find the first audio file if any
        const audioFile = attachedFiles.find(file => file.fileType === 'audio');
        if (audioFile) {
          audioUrl = audioFile.url;
          contentType = 'audio';
        }

        // Find the first video file if any
        const videoFile = attachedFiles.find(file => file.fileType === 'video');
        if (videoFile) {
          videoUrl = videoFile.url;
          contentType = 'video';
        }
      }

      console.log('📤 Creating post with:', {
        content: content.trim(),
        contentType,
        audioUrl,
        videoUrl,
        imageUrl,
        attachedFiles: attachedFiles.map(f => ({ fileId: f.fileId, url: f.url, type: f.fileType }))
      });

      // FIXED: Create proper post data with file URLs
      const postData: any = {
        content: content.trim(),
        content_type: contentType,
        mood: mood || undefined,
        visibility,
        is_anonymous: isAnonymous,
        file_attachments: attachedFiles.map(file => file.fileId),
      };

      // Add specific media URLs based on content type
      if (audioUrl) {
        postData.audio_url = audioUrl;
        postData.audio_duration = null;
      }

      if (videoUrl) {
        postData.video_url = videoUrl;
        postData.video_duration = null;
      }

      if (imageUrl) {
        postData.image_url = imageUrl;
      }

      console.log('🎯 Final post data being sent:', postData);

      await createPost(postData);

      // Reset form
      setContent('');
      setMood('');
      setVisibility('public');
      setIsAnonymous(false);
      setAttachedFiles([]);
      setCharCount(0);
      setShowMoodPicker(false);

    } catch (error) {
      console.error('Failed to create post:', error);
    }
  };

  const handleContentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    setContent(value);
    setCharCount(value.length);
  };

  const isSubmitDisabled = !content.trim() || isLoading || charCount > 5000;

  return (
    <div className="bg-white rounded-lg border shadow-sm">
      <div className="p-6">
        <h3 className="text-lg font-semibold mb-4">Share what's on your mind</h3>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Content Textarea */}
          <div>
            <textarea
              value={content}
              onChange={handleContentChange}
              placeholder="What would you like to share today?"
              className="w-full h-32 px-3 py-2 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              maxLength={5000}
            />
            <div className="flex justify-between items-center mt-2">
              <p className="text-xs text-gray-500">
                {charCount}/5000 characters
              </p>
              {charCount > 4000 && (
                <p className="text-xs text-orange-600">
                  {5000 - charCount} characters remaining
                </p>
              )}
            </div>
          </div>

          {/* Mood Selection */}
          <div className="relative">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-gray-700 flex items-center gap-2">
                <Smile className="h-4 w-4" />
                How are you feeling?
              </label>
              {mood && (
                <button
                  type="button"
                  onClick={() => setMood('')}
                  className="text-xs text-gray-500 hover:text-gray-700"
                >
                  Clear
                </button>
              )}
            </div>

            {!showMoodPicker ? (
              <button
                type="button"
                onClick={() => setShowMoodPicker(true)}
                className="w-full mt-1 px-3 py-2 text-left border border-gray-300 rounded-lg hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
              >
                {mood ? (
                  <span className={MOOD_OPTIONS.find(m => m.value === mood)?.color}>
                    {MOOD_OPTIONS.find(m => m.value === mood)?.label}
                  </span>
                ) : (
                  <span className="text-gray-500">Select a mood (optional)</span>
                )}
              </button>
            ) : (
              <div className="mt-2 grid grid-cols-4 gap-2">
                {MOOD_OPTIONS.map((moodOption) => (
                  <button
                    key={moodOption.value}
                    type="button"
                    onClick={() => {
                      setMood(moodOption.value);
                      setShowMoodPicker(false);
                    }}
                    className={`p-2 rounded-lg border text-sm text-center hover:border-gray-400 transition-colors ${
                      mood === moodOption.value
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-300'
                    }`}
                  >
                    <div className={moodOption.color}>
                      {moodOption.label}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Privacy Settings */}
          <div>
            <label className="text-sm font-medium text-gray-700 mb-2 block">
              Privacy Settings
            </label>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
              {VISIBILITY_OPTIONS.map((option) => {
                const Icon = option.icon;
                return (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => setVisibility(option.value as any)}
                    className={`p-3 rounded-lg border text-left transition-all ${
                      visibility === option.value
                        ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-200'
                        : 'border-gray-300 hover:border-gray-400'
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <Icon className={`h-4 w-4 ${option.color}`} />
                      <span className="font-medium text-sm">{option.label}</span>
                    </div>
                    <p className="text-xs text-gray-600">{option.description}</p>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Anonymous Toggle */}
          <div className="flex items-center justify-between p-3 border border-gray-300 rounded-lg">
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-full ${isAnonymous ? 'bg-purple-100' : 'bg-gray-100'}`}>
                {isAnonymous ? (
                  <EyeOff className="h-4 w-4 text-purple-600" />
                ) : (
                  <Eye className="h-4 w-4 text-gray-600" />
                )}
              </div>
              <div>
                <p className="font-medium text-sm">Post Anonymously</p>
                <p className="text-xs text-gray-600">
                  {isAnonymous
                    ? 'Your identity will be hidden'
                    : 'Your username will be visible'
                  }
                </p>
              </div>
            </div>
            <button
              type="button"
              onClick={() => setIsAnonymous(!isAnonymous)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                isAnonymous ? 'bg-purple-600' : 'bg-gray-300'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  isAnonymous ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>

          {/* File Attachments Section */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <label className="text-sm font-medium text-gray-700 flex items-center gap-2">
                <Paperclip className="h-4 w-4" />
                Attach Media (Optional)
              </label>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-3">
              {/* Audio Upload */}
              <FileUpload
                onFileUploaded={handleFileUploaded}
                fileType="audio"
                maxFileSize={50 * 1024 * 1024} // 50MB
              />

              {/* Video Upload */}
              <FileUpload
                onFileUploaded={handleFileUploaded}
                fileType="video"
                maxFileSize={100 * 1024 * 1024} // 100MB
              />

              {/* Image Upload */}
              <FileUpload
                onFileUploaded={handleFileUploaded}
                fileType="image"
                maxFileSize={10 * 1024 * 1024} // 10MB
              />
            </div>

            {/* Attached Files List */}
            {attachedFiles.length > 0 && (
              <div className="space-y-2">
                <p className="text-sm font-medium text-gray-700">Attached files:</p>
                {attachedFiles.map((file) => (
                  <div
                    key={file.fileId}
                    className="flex items-center justify-between p-2 bg-gray-50 rounded-lg border"
                  >
                    <div className="flex items-center gap-2">
                      {file.fileType === 'audio' && <Music className="h-4 w-4 text-blue-600" />}
                      {file.fileType === 'video' && <Video className="h-4 w-4 text-purple-600" />}
                      {file.fileType === 'image' && <Image className="h-4 w-4 text-green-600" />}
                      <span className="text-sm text-gray-700">{file.fileName}</span>
                    </div>
                    <button
                      type="button"
                      onClick={() => removeAttachedFile(file.fileId)}
                      className="p-1 hover:bg-gray-200 rounded-full transition-colors"
                    >
                      <X className="h-3 w-3 text-gray-500" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isSubmitDisabled}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Sharing...
              </>
            ) : (
              'Share Post'
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
