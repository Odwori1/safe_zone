'use client';

import { useAuth } from '@/hooks/use-auth';
import ProtectedRoute from '@/components/auth/protected-route';
import PostsFeedMinimal from '@/components/posts/posts-feed-minimal';
import CreatePostFormMinimal from '@/components/posts/create-post-form-minimal';

export default function TestMinimalDashboard() {
  const { user, logout } = useAuth();

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 py-4">
            <div className="flex justify-between items-center">
              <h1 className="text-2xl font-bold text-blue-600">Safe Zone - MINIMAL TEST</h1>
              <div className="flex items-center space-x-4">
                <span>Welcome, {user?.username}</span>
                <button
                  onClick={logout}
                  className="bg-gray-500 text-white px-4 py-2 rounded-lg"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </header>

        <main className="max-w-4xl mx-auto px-4 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-1">
              <CreatePostFormMinimal />
            </div>
            <div className="lg:col-span-2">
              <PostsFeedMinimal />
            </div>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}
