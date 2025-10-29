'use client';

import { useState } from 'react';
import { PostsFilter as PostsFilterType } from '@/types/posts';
import { Search, Filter, X } from 'lucide-react';

interface PostsFilterProps {
  onFilterChange: (filters: PostsFilterType) => void;
  currentFilters: PostsFilterType;
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
  { value: 'excited', label: '🎉 Excited' }
];

const visibilityOptions = [
  { value: '', label: 'All Visibility' },
  { value: 'public', label: '🌍 Public' },
  { value: 'private', label: '🔒 Private' },
  { value: 'support_group', label: '👥 Support Group' }
];

export default function PostsFilter({ onFilterChange, currentFilters }: PostsFilterProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearchChange = (query: string) => {
    setSearchQuery(query);
    onFilterChange({
      ...currentFilters,
      search: query || undefined, // FIXED: Send search parameter instead of content_type
      skip: 0 // Reset to first page when filtering
    });
  };

  const handleMoodChange = (mood: string) => {
    onFilterChange({
      ...currentFilters,
      mood: mood || undefined,
      skip: 0
    });
  };

  const handleVisibilityChange = (visibility: string) => {
    onFilterChange({
      ...currentFilters,
      visibility: visibility || undefined,
      skip: 0
    });
  };

  const clearFilters = () => {
    setSearchQuery('');
    onFilterChange({
      skip: 0,
      limit: 100
    });
  };

  const hasActiveFilters = currentFilters.mood || currentFilters.visibility || currentFilters.search;

  return (
    <div className="bg-white rounded-lg border shadow-sm p-4 mb-6">
      {/* Search Bar */}
      <div className="flex items-center gap-4 mb-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <input
            type="text"
            placeholder="Search posts..."
            value={searchQuery}
            onChange={(e) => handleSearchChange(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        >
          <Filter className="h-4 w-4" />
          Filters
          {hasActiveFilters && (
            <span className="bg-blue-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
              !
            </span>
          )}
        </button>

        {hasActiveFilters && (
          <button
            onClick={clearFilters}
            className="flex items-center gap-2 px-3 py-2 text-gray-600 hover:text-gray-800 transition-colors"
          >
            <X className="h-4 w-4" />
            Clear
          </button>
        )}
      </div>

      {/* Expanded Filters */}
      {isExpanded && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t border-gray-200 animate-in fade-in duration-300">
          {/* Mood Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Filter by Mood
            </label>
            <select
              value={currentFilters.mood || ''}
              onChange={(e) => handleMoodChange(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
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
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Filter by Visibility
            </label>
            <select
              value={currentFilters.visibility || ''}
              onChange={(e) => handleVisibilityChange(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              {visibilityOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      )}

      {/* Active Filters Display */}
      {hasActiveFilters && (
        <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-gray-200">
          {currentFilters.mood && (
            <span className="inline-flex items-center gap-1 bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-sm">
              Mood: {moodOptions.find(m => m.value === currentFilters.mood)?.label}
              <button
                onClick={() => handleMoodChange('')}
                className="hover:text-blue-600"
              >
                <X className="h-3 w-3" />
              </button>
            </span>
          )}
          {currentFilters.visibility && (
            <span className="inline-flex items-center gap-1 bg-green-100 text-green-800 px-2 py-1 rounded-full text-sm">
              {visibilityOptions.find(v => v.value === currentFilters.visibility)?.label}
              <button
                onClick={() => handleVisibilityChange('')}
                className="hover:text-green-600"
              >
                <X className="h-3 w-3" />
              </button>
            </span>
          )}
          {currentFilters.search && (
            <span className="inline-flex items-center gap-1 bg-purple-100 text-purple-800 px-2 py-1 rounded-full text-sm">
              Search: "{currentFilters.search}"
              <button
                onClick={() => handleSearchChange('')}
                className="hover:text-purple-600"
              >
                <X className="h-3 w-3" />
              </button>
            </span>
          )}
        </div>
      )}
    </div>
  );
}
