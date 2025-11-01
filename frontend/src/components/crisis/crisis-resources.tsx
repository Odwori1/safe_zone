'use client';

import { useState, useEffect } from 'react';
import { useCrisisStore } from '@/stores/crisis-store';
import { CrisisResource } from '@/types/crisis';
import { Search, Filter, Phone, Globe, MessageCircle, Loader2, AlertCircle, Heart, MapPin } from 'lucide-react';

const CATEGORY_OPTIONS = [
  { value: 'suicide_prevention', label: 'Suicide Prevention', color: 'bg-red-100 text-red-800' },
  { value: 'crisis_support', label: 'Crisis Support', color: 'bg-orange-100 text-orange-800' },
  { value: 'mental_health', label: 'Mental Health', color: 'bg-blue-100 text-blue-800' },
  { value: 'emergency', label: 'Emergency Services', color: 'bg-purple-100 text-purple-800' },
  { value: 'information', label: 'Information', color: 'bg-green-100 text-green-800' },
  { value: 'support_group', label: 'Support Groups', color: 'bg-indigo-100 text-indigo-800' },
];

const SCOPE_OPTIONS = [
  { value: 'global', label: 'Global' },
  { value: 'UG', label: 'Uganda' },
  { value: 'US', label: 'United States' },
  { value: 'GB', label: 'United Kingdom' },
  { value: 'CA', label: 'Canada' },
  { value: 'AU', label: 'Australia' },
  { value: 'KE', label: 'Kenya' },
  { value: 'ZA', label: 'South Africa' },
];

export default function CrisisResources() {
  const {
    resources,
    resourcesLoading,
    resourcesError,
    recommendations,
    recommendationsLoading,
    getResources,
    searchResources,
    getRecommendations,
    clearErrors
  } = useCrisisStore();

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedScope, setSelectedScope] = useState('');
  const [showRecommendations, setShowRecommendations] = useState(false);
  const [activeTab, setActiveTab] = useState<'all' | 'search' | 'recommendations'>('all');

  useEffect(() => {
    getResources();
  }, [getResources]);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setActiveTab('search');
    clearErrors();
    await searchResources(searchQuery);
  };

  const handleFilterChange = () => {
    setActiveTab('all');
    clearErrors();
    getResources({
      category: selectedCategory || undefined,
      geographic_scope: selectedScope || undefined,
    });
  };

  const handleGetRecommendations = async () => {
    setActiveTab('recommendations');
    setShowRecommendations(true);
    clearErrors();
    await getRecommendations('anxious'); // Default mood for demo
  };

  const clearSearch = () => {
    setSearchQuery('');
    setActiveTab('all');
    getResources();
  };

  const ResourceCard = ({ resource }: { resource: CrisisResource }) => (
    <div className="bg-white rounded-lg border shadow-sm hover:shadow-md transition-shadow p-6">
      <div className="flex justify-between items-start mb-3">
        <div className="flex items-center gap-2">
          <h3 className="font-semibold text-lg text-gray-900">{resource.name}</h3>
          {resource.geographic_scope === 'UG' && (
            <span className="flex items-center gap-1 bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full text-xs font-medium">
              <MapPin className="h-3 w-3" />
              Uganda
            </span>
          )}
        </div>
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
          CATEGORY_OPTIONS.find(cat => cat.value === resource.category)?.color || 'bg-gray-100 text-gray-800'
        }`}>
          {CATEGORY_OPTIONS.find(cat => cat.value === resource.category)?.label || resource.category}
        </span>
      </div>

      <p className="text-gray-600 mb-4">{resource.description}</p>

      <div className="space-y-2">
        {resource.phone_number && (
          <div className="flex items-center gap-2">
            <Phone className="h-4 w-4 text-green-600" />
            <a
              href={`tel:${resource.phone_number}`}
              className="text-green-600 hover:text-green-700 font-medium"
            >
              {resource.phone_number}
            </a>
          </div>
        )}

        {resource.website_url && (
          <div className="flex items-center gap-2">
            <Globe className="h-4 w-4 text-blue-600" />
            <a
              href={resource.website_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-700 truncate"
            >
              Visit Website
            </a>
          </div>
        )}

        {resource.chat_url && (
          <div className="flex items-center gap-2">
            <MessageCircle className="h-4 w-4 text-purple-600" />
            <a
              href={resource.chat_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-purple-600 hover:text-purple-700"
            >
              Live Chat
            </a>
          </div>
        )}

        {resource.text_line && (
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <span>📱 Text: {resource.text_line}</span>
          </div>
        )}
      </div>

      <div className="flex justify-between items-center mt-4 pt-4 border-t border-gray-100">
        <span className="text-xs text-gray-500 capitalize">
          {resource.geographic_scope === 'UG' ? 'Uganda' : 
           resource.geographic_scope === 'US' ? 'United States' :
           resource.geographic_scope === 'GB' ? 'United Kingdom' :
           resource.geographic_scope} • {resource.languages.join(', ')}
        </span>
        {resource.priority === 1 && (
          <span className="flex items-center gap-1 text-xs text-red-600 font-medium">
            <Heart className="h-3 w-3 fill-current" />
            High Priority
          </span>
        )}
      </div>
    </div>
  );

  const displayResources = activeTab === 'recommendations' ? recommendations : resources;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-red-500 to-orange-600 rounded-lg text-white p-6">
        <div className="flex items-center gap-3 mb-2">
          <AlertCircle className="h-8 w-8" />
          <h2 className="text-2xl font-bold">Crisis Support Resources</h2>
        </div>
        <p className="opacity-90">
          Immediate help and support resources available 24/7. You're not alone.
        </p>
      </div>

      {/* Search and Filter Section */}
      <div className="bg-white rounded-lg border shadow-sm p-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-4">
          {/* Search */}
          <div className="lg:col-span-2">
            <form onSubmit={handleSearch} className="flex gap-2">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <input
                  type="text"
                  placeholder="Search crisis resources..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
                />
              </div>
              <button
                type="submit"
                disabled={resourcesLoading || !searchQuery.trim()}
                className="bg-red-600 text-white px-6 py-2 rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Search
              </button>
              {searchQuery && (
                <button
                  type="button"
                  onClick={clearSearch}
                  className="border border-gray-300 px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Clear
                </button>
              )}
            </form>
          </div>

          {/* Recommendations Button */}
          <button
            onClick={handleGetRecommendations}
            disabled={recommendationsLoading}
            className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
          >
            {recommendationsLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Heart className="h-4 w-4" />
            )}
            Get Recommendations
          </button>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-4">
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-gray-600" />
            <span className="text-sm font-medium text-gray-700">Filter by:</span>
          </div>

          <select
            value={selectedCategory}
            onChange={(e) => {
              setSelectedCategory(e.target.value);
              handleFilterChange();
            }}
            className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-red-500 focus:border-red-500"
          >
            <option value="">All Categories</option>
            {CATEGORY_OPTIONS.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>

          <select
            value={selectedScope}
            onChange={(e) => {
              setSelectedScope(e.target.value);
              handleFilterChange();
            }}
            className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-red-500 focus:border-red-500"
          >
            <option value="">All Regions</option>
            {SCOPE_OPTIONS.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Error Display */}
      {resourcesError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center gap-2 text-red-800">
            <AlertCircle className="h-4 w-4" />
            <p>{resourcesError}</p>
          </div>
          <button
            onClick={clearErrors}
            className="mt-2 text-red-600 hover:text-red-800 text-sm"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Results Header */}
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-gray-900">
          {activeTab === 'recommendations' ? 'Personalized Recommendations' :
           activeTab === 'search' ? 'Search Results' : 'All Resources'}
          {displayResources.length > 0 && ` (${displayResources.length})`}
        </h3>

        {activeTab !== 'all' && (
          <button
            onClick={() => {
              setActiveTab('all');
              getResources();
            }}
            className="text-red-600 hover:text-red-700 text-sm font-medium"
          >
            View All Resources
          </button>
        )}
      </div>

      {/* Resources Grid */}
      {displayResources.length === 0 && !resourcesLoading ? (
        <div className="bg-gray-50 rounded-lg p-8 text-center">
          <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">
            {activeTab === 'search'
              ? 'No resources found matching your search'
              : activeTab === 'recommendations'
              ? 'No recommendations available at the moment'
              : 'No crisis resources available'
            }
          </p>
        </div>
      ) : (
        <div className="grid gap-4">
          {displayResources.map((resource) => (
            <ResourceCard key={resource.id} resource={resource} />
          ))}
        </div>
      )}

      {/* Loading State */}
      {(resourcesLoading || recommendationsLoading) && (
        <div className="flex justify-center items-center py-8">
          <Loader2 className="h-8 w-8 animate-spin text-red-600" />
          <span className="ml-2 text-gray-600">
            {recommendationsLoading ? 'Getting recommendations...' : 'Loading resources...'}
          </span>
        </div>
      )}
    </div>
  );
}
