'use client';

import { useState, useEffect } from 'react';
import { useJournalsStore } from '@/stores/journals-store';
import { JournalStats as JournalStatsType } from '@/types/journals';
import { BarChart3, BookOpen, TrendingUp, Calendar, FileText, Loader2 } from 'lucide-react';

export default function JournalStats() {
  const { getStats, stats, isLoading } = useJournalsStore();
  const [localStats, setLocalStats] = useState<JournalStatsType | null>(null);

  useEffect(() => {
    getStats();
  }, [getStats]);

  useEffect(() => {
    if (stats) {
      setLocalStats(stats);
    }
  }, [stats]);

  if (isLoading || !localStats) {
    return (
      <div className="bg-white rounded-lg border shadow-sm p-6">
        <div className="flex items-center gap-2 mb-4">
          <BarChart3 className="h-5 w-5 text-blue-600" />
          <h3 className="font-semibold text-lg">Journal Statistics</h3>
        </div>
        <div className="flex justify-center items-center py-8">
          <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
          <span className="ml-2 text-gray-600">Loading stats...</span>
        </div>
      </div>
    );
  }

  const StatCard = ({ icon: Icon, label, value, color }: { icon: any, label: string, value: string | number, color: string }) => (
    <div className="bg-gray-50 rounded-lg p-4 text-center">
      <Icon className={`h-6 w-6 mx-auto mb-2 ${color}`} />
      <div className="text-2xl font-bold text-gray-900">{value}</div>
      <div className="text-sm text-gray-600">{label}</div>
    </div>
  );

  return (
    <div className="bg-white rounded-lg border shadow-sm p-6">
      <div className="flex items-center gap-2 mb-6">
        <BarChart3 className="h-5 w-5 text-blue-600" />
        <h3 className="font-semibold text-lg">Journal Statistics</h3>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
        <StatCard
          icon={BookOpen}
          label="Total Entries"
          value={localStats.total_entries}
          color="text-blue-600"
        />
        <StatCard
          icon={FileText}
          label="Total Words"
          value={localStats.total_words.toLocaleString()}
          color="text-green-600"
        />
        <StatCard
          icon={TrendingUp}
          label="Avg Mood"
          value={localStats.average_mood ? localStats.average_mood.toFixed(1) : 'N/A'}
          color="text-purple-600"
        />
        <StatCard
          icon={Calendar}
          label="This Week"
          value={localStats.entries_this_week}
          color="text-orange-600"
        />
        <StatCard
          icon={Calendar}
          label="This Month"
          value={localStats.entries_this_month}
          color="text-red-600"
        />
      </div>

      {/* Most Common Mood */}
      {localStats.most_common_mood && (
        <div className="mb-4">
          <h4 className="font-medium text-gray-900 mb-2">Most Common Mood</h4>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <span className="text-blue-800 font-medium capitalize">{localStats.most_common_mood}</span>
          </div>
        </div>
      )}

      {/* Most Used Tags */}
      {localStats.most_used_tags && localStats.most_used_tags.length > 0 && (
        <div>
          <h4 className="font-medium text-gray-900 mb-2">Most Used Tags</h4>
          <div className="flex flex-wrap gap-2">
            {localStats.most_used_tags.slice(0, 5).map((tag, index) => (
              <span
                key={tag}
                className="px-2 py-1 bg-gray-100 text-gray-700 text-sm rounded-full"
              >
                #{tag}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
