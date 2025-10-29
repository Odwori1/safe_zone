'use client';

import { useState, useEffect } from 'react';
import { useJournalsStore } from '@/stores/journals-store';
import { JournalResponse, JournalUpdate } from '@/types/journals';
import {
  X,
  Lock,
  Globe,
  Smile,
  Tag,
  Loader2,
  BookOpen
} from 'lucide-react';

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

const MOOD_INTENSITY_OPTIONS = [
  { value: 1, label: 'Very Low', emoji: '😔' },
  { value: 2, label: 'Low', emoji: '😕' },
  { value: 3, label: 'Somewhat Low', emoji: '🙁' },
  { value: 4, label: 'Neutral Low', emoji: '😐' },
  { value: 5, label: 'Neutral', emoji: '😶' },
  { value: 6, label: 'Neutral High', emoji: '🙂' },
  { value: 7, label: 'Somewhat High', emoji: '😊' },
  { value: 8, label: 'High', emoji: '😄' },
  { value: 9, label: 'Very High', emoji: '😁' },
  { value: 10, label: 'Extreme', emoji: '🤩' },
];

interface JournalEditModalProps {
  journal: JournalResponse;
  isOpen: boolean;
  onClose: () => void;
  onSave: () => void;
}

export default function JournalEditModal({ journal, isOpen, onClose, onSave }: JournalEditModalProps) {
  const { updateJournal, isLoading } = useJournalsStore();

  const [title, setTitle] = useState(journal.title);
  const [content, setContent] = useState(journal.content);
  const [mood, setMood] = useState(journal.mood || '');
  const [moodIntensity, setMoodIntensity] = useState<number>(journal.mood_intensity || 5);
  const [tags, setTags] = useState<string[]>(journal.tags || []);
  const [tagInput, setTagInput] = useState('');
  const [isPrivate, setIsPrivate] = useState(journal.is_private);
  const [showMoodPicker, setShowMoodPicker] = useState(false);
  const [charCount, setCharCount] = useState(journal.content.length);

  // Reset form when journal changes
  useEffect(() => {
    if (journal) {
      setTitle(journal.title);
      setContent(journal.content);
      setMood(journal.mood || '');
      setMoodIntensity(journal.mood_intensity || 5);
      setTags(journal.tags || []);
      setIsPrivate(journal.is_private);
      setCharCount(journal.content.length);
    }
  }, [journal]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!title.trim() || !content.trim()) return;

    try {
      const updateData: JournalUpdate = {
        title: title.trim(),
        content: content.trim(),
        mood: mood || undefined,
        mood_intensity: moodIntensity,
        tags: tags.length > 0 ? tags : undefined,
        is_private: isPrivate,
      };

      await updateJournal(journal.id, updateData);
      onSave();
      onClose();
    } catch (error) {
      console.error('Failed to update journal:', error);
    }
  };

  const handleContentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    setContent(value);
    setCharCount(value.length);
  };

  const handleAddTag = () => {
    if (tagInput.trim() && !tags.includes(tagInput.trim())) {
      setTags([...tags, tagInput.trim()]);
      setTagInput('');
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter(tag => tag !== tagToRemove));
  };

  const handleTagInputKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddTag();
    }
  };

  const isSubmitDisabled = !title.trim() || !content.trim() || isLoading || charCount > 10000;

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center gap-2">
            <BookOpen className="h-5 w-5 text-blue-600" />
            <h2 className="text-lg font-semibold">Edit Journal Entry</h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Title Input */}
          <div>
            <label htmlFor="edit-title" className="block text-sm font-medium text-gray-700 mb-1">
              Title
            </label>
            <input
              type="text"
              id="edit-title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              maxLength={200}
            />
          </div>

          {/* Content Textarea */}
          <div>
            <label htmlFor="edit-content" className="block text-sm font-medium text-gray-700 mb-1">
              Your Thoughts
            </label>
            <textarea
              id="edit-content"
              value={content}
              onChange={handleContentChange}
              className="w-full h-48 px-3 py-2 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              maxLength={10000}
            />
            <div className="flex justify-between items-center mt-2">
              <p className="text-xs text-gray-500">
                {charCount}/10000 characters
              </p>
              {charCount > 8000 && (
                <p className="text-xs text-orange-600">
                  {10000 - charCount} characters remaining
                </p>
              )}
            </div>
          </div>

          {/* Mood Selection */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="relative">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                <Smile className="h-4 w-4 inline mr-1" />
                Mood
              </label>
              
              {!showMoodPicker ? (
                <button
                  type="button"
                  onClick={() => setShowMoodPicker(true)}
                  className="w-full px-3 py-2 text-left border border-gray-300 rounded-lg hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
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
                <div className="border border-gray-300 rounded-lg p-2">
                  <div className="grid grid-cols-4 gap-2 mb-2">
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
                  {mood && (
                    <button
                      type="button"
                      onClick={() => {
                        setMood('');
                        setShowMoodPicker(false);
                      }}
                      className="text-xs text-gray-500 hover:text-gray-700"
                    >
                      Clear selection
                    </button>
                  )}
                </div>
              )}
            </div>

            {/* Mood Intensity */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Mood Intensity
              </label>
              <select
                value={moodIntensity}
                onChange={(e) => setMoodIntensity(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {MOOD_INTENSITY_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.emoji} {option.label} ({option.value}/10)
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Tags Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <Tag className="h-4 w-4 inline mr-1" />
              Tags
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyDown={handleTagInputKeyDown}
                placeholder="Add a tag..."
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <button
                type="button"
                onClick={handleAddTag}
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
              >
                Add
              </button>
            </div>
            {tags.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {tags.map((tag) => (
                  <span
                    key={tag}
                    className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-800 text-sm rounded-full"
                  >
                    {tag}
                    <button
                      type="button"
                      onClick={() => handleRemoveTag(tag)}
                      className="hover:text-blue-600"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Privacy Toggle */}
          <div className="flex items-center justify-between p-3 border border-gray-300 rounded-lg">
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-full ${isPrivate ? 'bg-blue-100' : 'bg-gray-100'}`}>
                {isPrivate ? (
                  <Lock className="h-4 w-4 text-blue-600" />
                ) : (
                  <Globe className="h-4 w-4 text-gray-600" />
                )}
              </div>
              <div>
                <p className="font-medium text-sm">
                  {isPrivate ? 'Private Entry' : 'Public Entry'}
                </p>
                <p className="text-xs text-gray-600">
                  {isPrivate
                    ? 'Only you can see this entry'
                    : 'This entry may be visible to others'
                  }
                </p>
              </div>
            </div>
            <button
              type="button"
              onClick={() => setIsPrivate(!isPrivate)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                isPrivate ? 'bg-blue-600' : 'bg-gray-300'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  isPrivate ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitDisabled}
              className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Updating...
                </>
              ) : (
                'Update Entry'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
