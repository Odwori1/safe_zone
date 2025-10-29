'use client';

import { useState, useEffect } from 'react';
import { useJournalsStore } from '@/stores/journals-store';
import { useAuth } from '@/hooks/use-auth';
import {
  Trash2,
  Edit3,
  RefreshCw,
  Loader2,
  MoreVertical,
  Lock,
  Globe,
  BookOpen,
  Calendar
} from 'lucide-react';
import JournalEditModal from './journal-edit-modal'; // Import the edit modal component

let renderCount = 0;

export default function JournalFeed() {
  const {
    journals,
    isLoading,
    error,
    getJournals,
    deleteJournal
  } = useJournalsStore();
  const { user } = useAuth();
  const [hasLoaded, setHasLoaded] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [activeMenu, setActiveMenu] = useState<string | null>(null);

  // States for editing journal
  const [editingJournal, setEditingJournal] = useState<JournalResponse | null>(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);

  renderCount++;
  console.log(`🔄 JournalFeed RENDER #${renderCount}`, {
    hasLoaded,
    journalsCount: journals?.length || 0,
    isLoading,
    error
  });

  useEffect(() => {
    if (user && !hasLoaded) {
      handleLoadJournals();
    }
  }, [user, hasLoaded]);

  const handleLoadJournals = () => {
    console.log('🔄 Manual load triggered');
    getJournals().then(() => {
      console.log('✅ Journals loaded successfully');
      setHasLoaded(true);
    });
  };

  const handleRefresh = () => {
    if (user) {
      console.log('🔄 Refreshing journals...');
      getJournals();
    }
  };

  const handleDeleteJournal = async (journalId: string) => {
    setDeletingId(journalId);
    setActiveMenu(null);
    try {
      await deleteJournal(journalId);
    } finally {
      setDeletingId(null);
    }
  };

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
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    }
  };

  const getMoodColor = (mood: string | null) => {
    if (!mood) return 'bg-gray-100 text-gray-800';

    const moodColors: { [key: string]: string } = {
      happy: 'bg-yellow-100 text-yellow-800',
      calm: 'bg-green-100 text-green-800',
      neutral: 'bg-blue-100 text-blue-800',
      anxious: 'bg-orange-100 text-orange-800',
      sad: 'bg-indigo-100 text-indigo-800',
      angry: 'bg-red-100 text-red-800',
      tired: 'bg-purple-100 text-purple-800',
      excited: 'bg-pink-100 text-pink-800'
    };

    return moodColors[mood.toLowerCase()] || 'bg-gray-100 text-gray-800';
  };

  const handleEditJournal = (journal: JournalResponse) => {
    setEditingJournal(journal);
    setIsEditModalOpen(true);
    setActiveMenu(null);
  };

  const handleSaveEdit = () => {
    // The store will automatically update the journals list
    console.log('✅ Journal updated successfully');
    setIsEditModalOpen(false);
    setEditingJournal(null);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <div className="flex items-center gap-2">
            <BookOpen className="h-6 w-6 text-blue-600" />
            <h2 className="text-2xl font-bold text-gray-900">Your Journal</h2>
          </div>
          <p className="text-gray-600 mt-1">
            {journals?.length || 0} {journals?.length === 1 ? 'entry' : 'entries'}
          </p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={isLoading}
          className="flex items-center gap-2 border border-gray-300 px-4 py-2 rounded-lg hover:bg-gray-50 disabled:opacity-50 transition-colors"
        >
          {isLoading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <RefreshCw className="h-4 w-4" />
          )}
          Refresh
        </button>
      </div>

      {/* Journals List */}
      {!journals || journals.length === 0 ? (
        <div className="bg-white rounded-lg border-2 border-dashed p-8 text-center">
          <div className="max-w-md mx-auto">
            <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              No journal entries yet
            </h3>
            <p className="text-gray-600 mb-4">
              Start your journaling journey by writing your first entry. Reflect on your thoughts, feelings, and experiences.
            </p>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {journals.map((journal) => (
            <div
              key={journal.id}
              className="bg-white rounded-lg border shadow-sm hover:shadow-md transition-shadow"
            >
              {/* Journal Header */}
              <div className="flex justify-between items-start p-4 pb-2">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-semibold text-lg text-gray-900">{journal.title}</h3>
                    {journal.is_private ? (
                      <Lock className="h-4 w-4 text-blue-600" />
                    ) : (
                      <Globe className="h-4 w-4 text-green-600" />
                    )}
                  </div>
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <div className="flex items-center gap-1">
                      <Calendar className="h-3 w-3" />
                      {formatDate(journal.created_at)}
                    </div>
                    <span>•</span>
                    <span>{journal.word_count} words</span>
                    <span>•</span>
                    <span>{journal.read_time_minutes} min read</span>
                  </div>
                </div>

                {/* Journal Actions Menu */}
                {user && journal.user_id === user.id && (
                  <div className="relative">
                    <button
                      onClick={() => setActiveMenu(activeMenu === journal.id ? null : journal.id)}
                      className="h-8 w-8 p-0 rounded-md hover:bg-gray-100 transition-colors"
                    >
                      <MoreVertical className="h-4 w-4 mx-auto" />
                    </button>

                    {activeMenu === journal.id && (
                      <div className="absolute right-0 top-8 bg-white border rounded-lg shadow-lg z-10 min-w-[120px]">
                        {/* Edit Button */}
                        <button
                          onClick={() => handleEditJournal(journal)}
                          className="flex items-center gap-2 w-full px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 rounded-t-lg transition-colors"
                        >
                          <Edit3 className="h-3 w-3" />
                          Edit
                        </button>
                        {/* Delete Button */}
                        <button
                          onClick={() => handleDeleteJournal(journal.id)}
                          disabled={deletingId === journal.id}
                          className="flex items-center gap-2 w-full px-3 py-2 text-sm text-red-600 hover:bg-red-50 disabled:opacity-50 rounded-b-lg transition-colors"
                        >
                          {deletingId === journal.id ? (
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

              {/* Journal Content Preview */}
              <div className="px-4 py-3">
                <p className="text-gray-700 line-clamp-3">{journal.content}</p>

                {/* Mood and Tags */}
                <div className="flex flex-wrap gap-2 mt-3">
                  {journal.mood && (
                    <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${getMoodColor(journal.mood)}`}>
                      {journal.mood} {journal.mood_intensity && `(${journal.mood_intensity}/10)`}
                    </span>
                  )}
                  {/* Check if tags exists and is an array before mapping */}
                  {journal.tags && journal.tags.map((tag) => (
                    <span
                      key={tag}
                      className="inline-block px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full"
                    >
                      #{tag}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Loading indicator for refreshes */}
      {isLoading && hasLoaded && (
        <div className="flex justify-center items-center py-4">
          <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
          <span className="ml-2 text-gray-600">Refreshing journals...</span>
        </div>
      )}

      {/* Edit Journal Modal */}
      {editingJournal && (
        <JournalEditModal
          journal={editingJournal}
          isOpen={isEditModalOpen}
          onClose={() => {
            setIsEditModalOpen(false);
            setEditingJournal(null);
          }}
          onSave={handleSaveEdit}
        />
      )}
    </div>
  );
}
