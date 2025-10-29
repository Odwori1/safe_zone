'use client';

import { useAuth } from '@/hooks/use-auth';
import ProtectedRoute from '@/components/auth/protected-route';
import { PostsFeed, CreatePostForm } from '@/components/posts';
import { Users, BookOpen } from 'lucide-react'; // ADD BookOpen IMPORT
import Link from 'next/link';

export default function DashboardPage() {
  const { user, logout } = useAuth();

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-6xl mx-auto px-4">
          {/* Header */}
          <div className="flex justify-between items-center mb-8">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Safe Zone</h1>
              <p className="text-gray-600 mt-1">
                Welcome back, {user?.username || user?.email}
              </p>
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
              <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg text-white p-6">
                <h2 className="text-2xl font-bold mb-2">Welcome to Your Safe Space</h2>
                <p className="opacity-90">
                  Share your thoughts, connect with others, and find support in our caring community.
                </p>
              </div>

              {/* Create Post */}
              <CreatePostForm />

              {/* Posts Feed */}
              <PostsFeed />
            </div>

            {/* Sidebar - 1 column */}
            <div className="space-y-6">
              {/* Profile Card */}
              <div className="bg-white rounded-lg border shadow-sm p-6">
                <h3 className="font-semibold mb-4 text-lg">Your Profile</h3>
                <div className="space-y-3 text-sm">
                  <div>
                    <p className="font-medium text-gray-900">Username:</p>
                    <p className="text-gray-600">{user?.username || 'Not set'}</p>
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">Email:</p>
                    <p className="text-gray-600">{user?.email}</p>
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">Timezone:</p>
                    <p className="text-gray-600">{user?.timezone || 'UTC'}</p>
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">Language:</p>
                    <p className="text-gray-600">{user?.language || 'en-US'}</p>
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">Member since:</p>
                    <p className="text-gray-600">
                      {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'Recently'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Quick Actions */}
              <div className="bg-white rounded-lg border shadow-sm p-6">
                <h3 className="font-semibold mb-4 text-lg">Quick Actions</h3>
                <div className="space-y-3">
                  {/* ADD JOURNAL BUTTON */}
                  <Link href="/dashboard/journals">
                    <button className="w-full text-left p-3 rounded-lg border border-gray-300 hover:border-purple-500 hover:bg-purple-50 transition-colors group">
                      <div className="flex items-center gap-3">
                        <BookOpen className="h-5 w-5 text-purple-600 group-hover:text-purple-700" />
                        <div>
                          <span className="font-medium">📔 Personal Journal</span>
                          <p className="text-sm text-gray-600 mt-1">Write private reflections</p>
                        </div>
                      </div>
                    </button>
                  </Link>

                  {/* FIND USERS BUTTON */}
                  <Link href="/dashboard/users">
                    <button className="w-full text-left p-3 rounded-lg border border-gray-300 hover:border-blue-500 hover:bg-blue-50 transition-colors group">
                      <div className="flex items-center gap-3">
                        <Users className="h-5 w-5 text-blue-600 group-hover:text-blue-700" />
                        <div>
                          <span className="font-medium">👥 Find Users</span>
                          <p className="text-sm text-gray-600 mt-1">Connect with community members</p>
                        </div>
                      </div>
                    </button>
                  </Link>

                  {/* OTHER ACTIONS */}
                  <button className="w-full text-left p-3 rounded-lg border border-gray-300 hover:border-blue-500 hover:bg-blue-50 transition-colors">
                    <span className="font-medium">📊 Analytics</span>
                    <p className="text-sm text-gray-600 mt-1">Track your engagement and insights</p>
                  </button>
                  <button className="w-full text-left p-3 rounded-lg border border-gray-300 hover:border-green-500 hover:bg-green-50 transition-colors">
                    <span className="font-medium">👥 Support Groups</span>
                    <p className="text-sm text-gray-600 mt-1">Join specialized support communities</p>
                  </button>
                  <button className="w-full text-left p-3 rounded-lg border border-gray-300 hover:border-purple-500 hover:bg-purple-50 transition-colors">
                    <span className="font-medium">🔧 Settings</span>
                    <p className="text-sm text-gray-600 mt-1">Customize your experience</p>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
