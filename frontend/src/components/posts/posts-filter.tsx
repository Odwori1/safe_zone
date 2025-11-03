'use client';

import { useState } from 'react';
import { PostsFilter as PostsFilterType } from '@/types/posts';

interface PostsFilterProps {
  onFilterChange: (filters: PostsFilterType) => void;
  currentFilters: PostsFilterType;
  showFeedOptions?: boolean; // NEW: Option to show feed-specific filters
}

const moodOptions = [
  { value: '', label: 'All Moods' },
  { value: 'happy', label: '😊 Happy' },
  { value: 'calm', label: '😌 Calm' },
  { value: 'neutral', label: '😐 Neutral' },
  { value: 'anxious', label: '😰 Anxious' },
  { value: 'sad', label: '😢 Sad' },
  { value: 'angry', label: '😠 Angry' },
  { value: 'tired', label: '😴 Tired' },
  { value: 'excited', label: '🤩 Excited' }
];

const visibilityOptions = [
  { value: '', label: 'All Visibility' },
  { value: 'public', label: '🌍 Public' },
  { value: 'private', label: '🔒 Private' },
  { value: 'support_group', label: '👥 Support Group' }
];

const contentTypeOptions = [
  { value: '', label: 'All Types' },
  { value: 'text', label: '📝 Text' },
  { value: 'journal', label: '📔 Journal' },
  { value: 'audio', label: '🎵 Audio' },
  { value: 'video', label: '🎥 Video' }
];

// NEW: Feed-specific filter options
const feedTypeOptions = [
  { value: 'all', label: '📱 All Posts' },
  { value: 'personal', label: '👤 Personal Feed' },
  { value: 'discover', label: '🔍 Discover' },
  { value: 'saved', label: '📑 Saved Posts' }
];

export default function PostsFilter({ 
  onFilterChange, 
  currentFilters, 
  showFeedOptions = false 
}: PostsFilterProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [localFilters, setLocalFilters] = useState<PostsFilterType>(currentFilters);
  const [feedType, setFeedType] = useState<string>('all'); // NEW: Feed type state

  const handleFilterChange = (key: keyof PostsFilterType, value: string) => {
    const newFilters = {
      ...localFilters,
      [key]: value || undefined
    };
    
    setLocalFilters(newFilters);
    onFilterChange(newFilters);
  };

  const handleFeedTypeChange = (type: string) => {
    setFeedType(type);
    
    // Reset filters when changing feed type
    const baseFilters: PostsFilterType = {
      skip: 0,
      limit: 100
    };
    
    setLocalFilters(baseFilters);
    
    // Emit custom event for feed type change
    const event = new CustomEvent('feedTypeChange', { 
      detail: { feedType: type, filters: baseFilters }
    });
    window.dispatchEvent(event);
  };

  const clearFilters = () => {
    const baseFilters: PostsFilterType = {
      skip: 0,
      limit: 100
    };
    
    setLocalFilters(baseFilters);
    setFeedType('all');
    onFilterChange(baseFilters);
    
    // Emit clear event
    const event = new CustomEvent('feedTypeChange', { 
      detail: { feedType: 'all', filters: baseFilters }
    });
    window.dispatchEvent(event);
  };

  const hasActiveFilters = 
    localFilters.mood || 
    localFilters.visibility || 
    localFilters.content_type || 
    localFilters.search ||
    feedType !== 'all';

  return (
    <div className="bg-white rounded-lg border shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <div className="flex items-center gap-3">
          <h3 className="font-semibold text-gray-900">Filters</h3>
          {hasActiveFilters && (
            <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
              Active
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {hasActiveFilters && (
            <button
              onClick={clearFilters}
              className="text-sm text-gray-600 hover:text-gray-900 transition-colors"
            >
              Clear All
            </button>
          )}
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-sm text-blue-600 hover:text-blue-700 transition-colors"
          >
            {isExpanded ? 'Show Less' : 'Show More'}
          </button>
        </div>
      </div>

      {/* Feed Type Selector - NEW */}
      {showFeedOptions && (
        <div className="p-4 border-b bg-gray-50">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Feed Type
          </label>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            {feedTypeOptions.map((option) => (
              <button
                key={option.value}
                onClick={() => handleFeedTypeChange(option.value)}
                className={`p-3 rounded-lg border text-sm font-medium transition-all ${
                  feedType === option.value
                    ? 'border-blue-500 bg-blue-50 text-blue-700 shadow-sm'
                    : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400'
                }`}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Basic Filters - Always Visible */}
      <div className="p-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Search */}
          <div>
            <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-1">
              Search Posts
            </label>
            <input
              id="search"
              type="text"
              placeholder="Search content..."
              value={localFilters.search || ''}
              onChange={(e) => handleFilterChange('search', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
            />
          </div>

          {/* Mood Filter */}
          <div>
            <label htmlFor="mood" className="block text-sm font-medium text-gray-700 mb-1">
              Mood
            </label>
            <select
              id="mood"
              value={localFilters.mood || ''}
              onChange={(e) => handleFilterChange('mood', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
            >
              {moodOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          {/* Visibility Filter */}
          <div>
            <label htmlFor="visibility" className="block text-sm font-medium text-gray-700 mb-1">
              Visibility
            </label>
            <select
              id="visibility"
              value={localFilters.visibility || ''}
              onChange={(e) => handleFilterChange('visibility', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
            >
              {visibilityOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          {/* Content Type Filter */}
          <div>
            <label htmlFor="contentType" className="block text-sm font-medium text-gray-700 mb-1">
              Content Type
            </label>
            <select
              id="contentType"
              value={localFilters.content_type || ''}
              onChange={(e) => handleFilterChange('content_type', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
            >
              {contentTypeOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Advanced Filters - Expandable */}
      {isExpanded && (
        <div className="p-4 border-t bg-gray-50">
          <h4 className="font-medium text-gray-900 mb-3">Advanced Options</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Pagination Controls */}
            <div>
              <label htmlFor="limit" className="block text-sm font-medium text-gray-700 mb-1">
                Posts per page
              </label>
              <select
                id="limit"
                value={localFilters.limit || 100}
                onChange={(e) => handleFilterChange('limit', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              >
                <option value={20}>20 posts</option>
                <option value={50}>50 posts</option>
                <option value={100}>100 posts</option>
              </select>
            </div>

            {/* User Filter (if needed) */}
            <div>
              <label htmlFor="userId" className="block text-sm font-medium text-gray-700 mb-1">
                User ID (Advanced)
              </label>
              <input
                id="userId"
                type="text"
                placeholder="Filter by user ID..."
                value={localFilters.user_id || ''}
                onChange={(e) => handleFilterChange('user_id', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              />
            </div>
          </div>
        </div>
      )}

      {/* Active Filters Summary */}
      {hasActiveFilters && (
        <div className="p-3 bg-blue-50 border-t">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-sm text-blue-800 font-medium">Active:</span>
            
            {feedType !== 'all' && (
              <span className="bg-blue-200 text-blue-800 text-xs px-2 py-1 rounded-full">
                {feedTypeOptions.find(opt => opt.value === feedType)?.label}
              </span>
            )}
            
            {localFilters.mood && (
              <span className="bg-blue-200 text-blue-800 text-xs px-2 py-1 rounded-full">
                Mood: {moodOptions.find(opt => opt.value === localFilters.mood)?.label}
              </span>
            )}
            
            {localFilters.visibility && (
              <span className="bg-blue-200 text-blue-800 text-xs px-2 py-1 rounded-full">
                {visibilityOptions.find(opt => opt.value === localFilters.visibility)?.label}
              </span>
            )}
            
            {localFilters.content_type && (
              <span className="bg-blue-200 text-blue-800 text-xs px-2 py-1 rounded-full">
                {contentTypeOptions.find(opt => opt.value === localFilters.content_type)?.label}
              </span>
            )}
            
            {localFilters.search && (
              <span className="bg-blue-200 text-blue-800 text-xs px-2 py-1 rounded-full">
                Search: "{localFilters.search}"
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
