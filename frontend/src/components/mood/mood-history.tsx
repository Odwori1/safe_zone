'use client';

import { useEffect, useState } from 'react';
import { useMoodStore } from '@/stores/mood-store';
import { MOOD_CATEGORIES } from '@/types/mood';

export function MoodHistory() {
  const { moods, getMoodHistory, loading } = useMoodStore();
  const [daysFilter, setDaysFilter] = useState(7);

  useEffect(() => {
    getMoodHistory(daysFilter);
  }, [daysFilter, getMoodHistory]);

  const getMoodColor = (moodCategory: string) => {
    const category = Object.values(MOOD_CATEGORIES).find(cat => 
      cat.moods.includes(moodCategory.toLowerCase())
    );
    return category?.color || '#6B7280';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading && moods.length === 0) {
    return (
      <div className="bg-white rounded-lg border shadow-sm p-6">
        <h2 className="text-xl font-bold mb-4">Mood History</h2>
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-gray-600 mt-2">Loading mood history...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border shadow-sm p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold">Mood History</h2>
        <select
          value={daysFilter}
          onChange={(e) => setDaysFilter(Number(e.target.value))}
          className="p-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value={7}>Last 7 days</option>
          <option value={30}>Last 30 days</option>
          <option value={90}>Last 90 days</option>
        </select>
      </div>

      {moods.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-600">No mood entries yet.</p>
          <p className="text-sm text-gray-500 mt-1">Start tracking your moods to see your history here.</p>
        </div>
      ) : (
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {moods.map((mood) => (
            <div
              key={mood.id}
              className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center space-x-3">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: getMoodColor(mood.mood) }}
                ></div>
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="font-medium capitalize">{mood.mood}</span>
                    <span className="text-sm text-gray-500">•</span>
                    <span className="text-sm text-gray-600">Intensity: {mood.intensity}/10</span>
                  </div>
                  {mood.notes && (
                    <p className="text-sm text-gray-600 mt-1">{mood.notes}</p>
                  )}
                  {mood.triggers.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-1">
                      {mood.triggers.map((trigger, index) => (
                        <span
                          key={index}
                          className="inline-block bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded"
                        >
                          {trigger}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm text-gray-500">
                  {formatDate(mood.created_at)}
                </div>
                <div className="text-xs text-gray-400 capitalize">
                  {mood.mood_category?.replace('_', ' ')}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
