'use client';

import { useState, useEffect } from 'react';
import { useUsersStore } from '@/stores/users-store';
import { UserSearchResult } from '@/types/users';
import { Search, Users, Loader2, UserPlus, UserCheck, Ban, Shield} from 'lucide-react';
import { formatDate } from '@/lib/date-utils';
import { UserActions } from './user-actions'; // Added import for UserActions

// Updated UserCardProps interface
interface UserCardProps {
  user: UserSearchResult;
  onFollow: (userId: string) => void;
  onUnfollow: (userId: string) => void;
  isLoading?: boolean;
  isFollowing?: boolean;
  isBlocked?: boolean;
  isBlockedBy?: boolean;
  onActionComplete?: () => void;
}

// Updated UserCard component
function UserCard({ 
  user, 
  onFollow, 
  onUnfollow, 
  isLoading = false, 
  isFollowing = false,
  isBlocked = false,
  isBlockedBy = false,
  onActionComplete 
}: UserCardProps) {
  const handleFollowClick = () => {
    if (isFollowing) {
      onUnfollow(user.id);
    } else {
      onFollow(user.id);
    }
  };

  return (
    <div className="bg-white rounded-lg border p-4 hover:shadow-md transition-shadow">
      <div className="flex items-center gap-4">
        {/* Avatar */}
        <div className="flex-shrink-0">
          {user.profile_picture ? (
            <img
              src={user.profile_picture}
              alt={user.username}
              className="w-12 h-12 rounded-full object-cover"
            />
          ) : (
            <div className="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center">
              <span className="text-white font-medium text-sm">
                {user.username[0].toUpperCase()}
              </span>
            </div>
          )}
        </div>

        {/* User Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h4 className="font-semibold text-gray-900 truncate">
              {user.username}
            </h4>
            {user.is_helper && (
              <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium">
                Helper
              </span>
            )}
            {isBlocked && (
              <span className="bg-red-100 text-red-800 px-2 py-1 rounded-full text-xs font-medium flex items-center gap-1">
                {/* Assuming you have icons for Ban and Shield */}
                <Ban className="h-3 w-3" />
                Blocked
              </span>
            )}
            {isBlockedBy && (
              <span className="bg-gray-100 text-gray-800 px-2 py-1 rounded-full text-xs font-medium flex items-center gap-1">
                <Shield className="h-3 w-3" />
                Blocked You
              </span>
            )}
          </div>

          {user.full_name && (
            <p className="text-gray-600 text-sm truncate">{user.full_name}</p>
          )}

          {user.bio && (
            <p className="text-gray-500 text-sm mt-1 line-clamp-2">{user.bio}</p>
          )}

          {user.helper_specialties && (
            <p className="text-blue-600 text-xs mt-1">
              Specialties: {user.helper_specialties}
            </p>
          )}

          <p className="text-gray-400 text-xs mt-1">
            Joined {formatDate(user.created_at)}
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          {/* Follow/Unfollow Button - only show if not blocked either way */}
          {!isBlocked && !isBlockedBy && (
            <button
              onClick={handleFollowClick}
              disabled={isLoading}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
                isFollowing
                  ? 'bg-green-100 text-green-800 border border-green-300 hover:bg-green-200'
                  : 'bg-blue-600 text-white border border-blue-600 hover:bg-blue-700'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : isFollowing ? (
                <UserCheck className="h-4 w-4" />
              ) : (
                <UserPlus className="h-4 w-4" />
              )}
              {isFollowing ? 'Following' : 'Follow'}
            </button>
          )}
          
          {/* User Actions Menu */}
          <UserActions 
            userId={user.id}
            username={user.username}
            isBlocked={isBlocked}
            onActionComplete={() => {
              if (onActionComplete) onActionComplete();
            }}
          />
        </div>
      </div>
    </div>
  );
}

export default function UserSearch() {
  const {
    searchResults,
    suggestions,
    isLoading,
    error,
    followLoading,
    relationshipStatus,
    searchUsers,
    getSuggestions,
    clearError,
    followUser,
    unfollowUser,
    getRelationshipStatus
  } = useUsersStore();

  const [searchQuery, setSearchQuery] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(true);

  useEffect(() => {
    getSuggestions();
  }, [getSuggestions]);

  // Load relationship status for displayed users
  useEffect(() => {
    const usersToCheck = showSuggestions ? suggestions : searchResults;
    usersToCheck.forEach(user => {
      getRelationshipStatus(user.id);
    });
  }, [suggestions, searchResults, showSuggestions, getRelationshipStatus]);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setShowSuggestions(false);
    try {
      await searchUsers({ query: searchQuery, limit: 20 });
    } catch (err) {
      console.error('Search failed:', err);
    }
  };

  const handleClearSearch = () => {
    setSearchQuery('');
    setShowSuggestions(true);
    getSuggestions();
  };

  const handleFollow = async (userId: string) => {
    try {
      await followUser(userId);
    } catch (err) {
      console.error('Follow failed:', err);
    }
  };

  const handleUnfollow = async (userId: string) => {
    try {
      await unfollowUser(userId);
    } catch (err) {
      console.error('Unfollow failed:', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Search Form */}
      <form onSubmit={handleSearch} className="bg-white rounded-lg border p-4">
        <div className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <input
              type="text"
              placeholder="Search users by username, name, or email..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <button
            type="submit"
            disabled={isLoading || !searchQuery.trim()}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Search'}
          </button>
          {searchQuery && (
            <button
              type="button"
              onClick={handleClearSearch}
              className="border border-gray-300 px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Clear
            </button>
          )}
        </div>
      </form>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
          <button
            onClick={clearError}
            className="mt-2 text-red-600 hover:text-red-800 text-sm"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Results */}
      <div className="space-y-4">
        {showSuggestions ? (
          <>
            <div className="flex items-center gap-2">
              <Users className="h-5 w-5 text-gray-600" />
              <h3 className="text-lg font-semibold">User Suggestions</h3>
            </div>

            {suggestions.length === 0 && !isLoading ? (
              <div className="bg-gray-50 rounded-lg p-8 text-center">
                <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">No user suggestions available</p>
              </div>
            ) : (
              <div className="grid gap-3">
                {suggestions.map((user) => (
                  <UserCard
                    key={user.id}
                    user={user}
                    onFollow={handleFollow}
                    onUnfollow={handleUnfollow}
                    isLoading={followLoading[user.id]}
                    isFollowing={relationshipStatus[user.id]?.is_following}
                    isBlocked={relationshipStatus[user.id]?.is_blocked}
                    isBlockedBy={relationshipStatus[user.id]?.is_blocked_by}
                    onActionComplete={() => {
                      getRelationshipStatus(user.id);
                    }}
                  />
                ))}
              </div>
            )}
          </>
        ) : (
          <>
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">
                Search Results ({searchResults.length})
              </h3>
              {searchQuery && (
                <p className="text-gray-600">Searching for: "{searchQuery}"</p>
              )}
            </div>

            {searchResults.length === 0 && !isLoading ? (
              <div className="bg-gray-50 rounded-lg p-8 text-center">
                <Search className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">No users found matching your search</p>
                <button
                  onClick={handleClearSearch}
                  className="mt-4 text-blue-600 hover:text-blue-800"
                >
                  View suggestions instead
                </button>
              </div>
            ) : (
              <div className="grid gap-3">
                {searchResults.map((user) => (
                  <UserCard
                    key={user.id}
                    user={user}
                    onFollow={handleFollow}
                    onUnfollow={handleUnfollow}
                    isLoading={followLoading[user.id]}
                    isFollowing={relationshipStatus[user.id]?.is_following}
                    isBlocked={relationshipStatus[user.id]?.is_blocked}
                    isBlockedBy={relationshipStatus[user.id]?.is_blocked_by}
                    onActionComplete={() => {
                      getRelationshipStatus(user.id);
                    }}
                  />
                ))}
              </div>
            )}
          </>
        )}
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="flex justify-center items-center py-8">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
          <span className="ml-2 text-gray-600">Loading users...</span>
        </div>
      )}
    </div>
  );
}
