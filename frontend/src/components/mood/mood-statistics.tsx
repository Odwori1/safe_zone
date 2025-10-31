'use client';

import { useEffect, useState } from 'react';
import { useMoodStore } from '@/stores/mood-store';
import { MOOD_CATEGORIES } from '@/types/mood';

export function MoodStatistics() {
  const { statistics, enhancedStats, getMoodStatistics, getEnhancedMoodStats, loading } = useMoodStore();
  const [daysFilter, setDaysFilter] = useState(30);
  const [view, setView] = useState<'basic' | 'enhanced'>('basic');

  useEffect(() => {
    if (view === 'basic') {
      getMoodStatistics(daysFilter);
    } else {
      getEnhancedMoodStats(daysFilter);
    }
  }, [daysFilter, view, getMoodStatistics, getEnhancedMoodStats]);

  const stats = view === 'basic' ? statistics : enhancedStats;

  if (loading && !stats) {
    return (
      <div className="bg-white rounded-lg border shadow-sm p-6">
        <h2 className="text-xl font-bold mb-4">Mood Statistics</h2>
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-gray-600 mt-2">Loading statistics...</p>
        </div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="bg-white rounded-lg border shadow-sm p-6">
        <h2 className="text-xl font-bold mb-4">Mood Statistics</h2>
        <div className="text-center py-8">
          <p className="text-gray-600">No statistics available yet.</p>
          <p className="text-sm text-gray-500 mt-1">Start tracking your moods to see insights.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border shadow-sm p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold">Mood Statistics</h2>
        <div className="flex space-x-2">
          <select
            value={daysFilter}
            onChange={(e) => setDaysFilter(Number(e.target.value))}
            className="p-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
          </select>
          <button
            onClick={() => setView(view === 'basic' ? 'enhanced' : 'basic')}
            className="p-2 border border-gray-300 rounded-md text-sm hover:bg-gray-50 transition-colors"
          >
            {view === 'basic' ? 'Enhanced View' : 'Basic View'}
          </button>
        </div>
      </div>

      {/* Basic Statistics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="text-center p-4 bg-blue-50 rounded-lg">
          <div className="text-2xl font-bold text-blue-600">{stats.total_entries}</div>
          <div className="text-sm text-blue-800">Total Entries</div>
        </div>
        <div className="text-center p-4 bg-green-50 rounded-lg">
          <div className="text-2xl font-bold text-green-600">{stats.average_intensity?.toFixed(1)}</div>
          <div className="text-sm text-green-800">Avg Intensity</div>
        </div>
        <div className="text-center p-4 bg-purple-50 rounded-lg">
          <div className="text-2xl font-bold text-purple-600 capitalize">
            {stats.most_common_mood || 'N/A'}
          </div>
          <div className="text-sm text-purple-800">Most Common</div>
        </div>
        <div className="text-center p-4 bg-orange-50 rounded-lg">
          <div className="text-2xl font-bold text-orange-600">
            {Object.keys(stats.mood_frequency || {}).length}
          </div>
          <div className="text-sm text-orange-800">Unique Moods</div>
        </div>
      </div>

      {/* Enhanced Statistics */}
      {view === 'enhanced' && enhancedStats && (
        <div className="space-y-4">
          {/* Category Distribution */}
          {enhancedStats.category_distribution && (
            <div>
              <h3 className="font-semibold mb-3">Category Distribution</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                {Object.entries(enhancedStats.category_distribution).map(([category, count]) => {
                  const categoryInfo = Object.values(MOOD_CATEGORIES).find(c => 
                    c.name === category
                  );
                  return (
                    <div
                      key={category}
                      className="p-3 rounded-lg text-white text-center"
                      style={{ backgroundColor: categoryInfo?.color || '#6B7280' }}
                    >
                      <div className="text-lg font-bold">{count}</div>
                      <div className="text-xs opacity-90 capitalize">
                        {category.replace('_', ' ')}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Clinical Insights */}
          {enhancedStats.clinical_insights && (
            <div>
              <h3 className="font-semibold mb-3">Clinical Insights</h3>
              <div className="space-y-2">
                {enhancedStats.clinical_insights.dominant_category && (
                  <div className="p-3 bg-blue-50 rounded-lg">
                    <div className="font-medium text-blue-800">Dominant Pattern</div>
                    <div className="text-sm text-blue-600 capitalize">
                      {enhancedStats.clinical_insights.dominant_category.replace('_', ' ')}
                    </div>
                  </div>
                )}
                {enhancedStats.clinical_insights.clinical_recommendations.length > 0 && (
                  <div className="p-3 bg-green-50 rounded-lg">
                    <div className="font-medium text-green-800 mb-2">Recommendations</div>
                    <ul className="text-sm text-green-700 space-y-1">
                      {enhancedStats.clinical_insights.clinical_recommendations.map((rec, index) => (
                        <li key={index}>• {rec}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Top Moods */}
      {stats.mood_frequency && (
        <div>
          <h3 className="font-semibold mb-3">Top Moods</h3>
          <div className="space-y-2">
            {Object.entries(stats.mood_frequency)
              .sort(([,a], [,b]) => b - a)
              .slice(0, 5)
              .map(([mood, count]) => (
                <div key={mood} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                  <span className="capitalize">{mood}</span>
                  <span className="font-medium">{count} times</span>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
}
