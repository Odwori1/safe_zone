'use client';

import { useAuth } from '@/hooks/use-auth';
import ProtectedRoute from '@/components/auth/protected-route';
import { JournalCreateForm, JournalFeed } from '@/components/journals';
import { BookOpen, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

// Add these imports
import JournalPrompts from '@/components/journals/journal-prompts';
import JournalStats from '@/components/journals/journal-stats';

export default function JournalsPage() {
  const { user, logout } = useAuth();

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-6xl mx-auto px-4">
          {/* Header */}
          <div className="flex justify-between items-center mb-8">
            <div className="flex items-center gap-4">
              <Link
                href="/dashboard"
                className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
              >
                <ArrowLeft className="h-5 w-5" />
                Back to Dashboard
              </Link>
              <div className="flex items-center gap-3">
                <BookOpen className="h-8 w-8 text-purple-600" />
                <div>
                  <h1 className="text-3xl font-bold text-gray-900">Personal Journal</h1>
                  <p className="text-gray-600 mt-1">
                    Your private space for reflection and growth
                  </p>
                </div>
              </div>
            </div>
            <button
              onClick={logout}
              className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
            >
              Logout
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
            {/* Main Content - 3 columns */}
            <div className="lg:col-span-3 space-y-8">
              {/* Welcome Card */}
              <div className="bg-gradient-to-r from-purple-500 to-pink-600 rounded-lg text-white p-6">
                <h2 className="text-2xl font-bold mb-2">Your Personal Sanctuary</h2>
                <p className="opacity-90">
                  This is your private space to reflect, process emotions, and track your mental health journey.
                  Everything you write here is for your eyes only.
                </p>
              </div>

              {/* Create Journal Entry */}
              <JournalCreateForm />

              {/* Journals Feed */}
              <JournalFeed />
            </div>

            {/* Sidebar - 1 column */}
            <div className="space-y-6">
              {/* Updated Sidebar Content */}
              {/* Journal Stats */}
              <JournalStats />

              {/* Journal Prompts */}
              <JournalPrompts />

              {/* Writing Tips */}
              <div className="bg-white rounded-lg border shadow-sm p-6">
                <h3 className="font-semibold mb-4 text-lg">Journaling Tips</h3>
                <div className="space-y-3 text-sm text-gray-600">
                  <p>• Write freely without worrying about grammar</p>
                  <p>• Be honest with your feelings</p>
                  <p>• Date your entries to track progress</p>
                  <p>• Review past entries to notice patterns</p>
                  <p>• There's no right or wrong way to journal</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
