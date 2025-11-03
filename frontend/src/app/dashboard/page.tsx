'use client';

import { useAuth } from '@/hooks/use-auth';
import ProtectedRoute from '@/components/auth/protected-route';
import { PostsFeed, CreatePostForm } from '@/components/posts';
import { MoodEntryForm, MoodHistory, MoodStatistics } from '@/components/mood';
import { Users, BookOpen, BarChart3, Heart, Shield, Bookmark } from 'lucide-react';
import Link from 'next/link';
import { useState } from 'react';

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState<'feed' | 'mood'>('feed');

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4">
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

          {/* Navigation Tabs */}
          <div className="flex space-x-1 mb-8 bg-white p-1 rounded-lg border shadow-sm">
            <button
              onClick={() => setActiveTab('feed')}
              className={`flex-1 py-3 px-4 rounded-md text-center font-medium transition-colors ${
                activeTab === 'feed'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              Community Feed
            </button>
            <button
              onClick={() => setActiveTab('mood')}
              className={`flex-1 py-3 px-4 rounded-md text-center font-medium transition-colors ${
                activeTab === 'mood'
                  ? 'bg-purple-600 text-white shadow-sm'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              Mood Tracking
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
            {/* Main Content - 3 columns */}
            <div className="lg:col-span-3 space-y-8">
              {activeTab === 'feed' ? (
                <>
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
                </>
              ) : (
                <>
                  {/* Mood Tracking Welcome */}
                  <div className="bg-gradient-to-r from-purple-500 to-pink-600 rounded-lg text-white p-6">
                    <h2 className="text-2xl font-bold mb-2">Mood Tracking & Insights</h2>
                    <p className="opacity-90">
                      Track your emotional wellbeing, discover patterns, and get professional insights.
                    </p>
                  </div>

                  {/* Mood Entry Form */}
                  <MoodEntryForm />

                  {/* Mood Statistics */}
                  <MoodStatistics />

                  {/* Mood History */}
                  <MoodHistory />
                </>
              )}
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
                  {/* MOOD TRACKING BUTTON */}
                  <button
                    onClick={() => setActiveTab('mood')}
                    className={`w-full text-left p-3 rounded-lg border transition-colors group ${
                      activeTab === 'mood'
                        ? 'border-purple-500 bg-purple-50'
                        : 'border-gray-300 hover:border-purple-500 hover:bg-purple-50'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <Heart className={`h-5 w-5 ${
                        activeTab === 'mood' ? 'text-purple-700' : 'text-purple-600 group-hover:text-purple-700'
                      }`} />
                      <div>
                        <span className="font-medium">💓 Mood Tracking</span>
                        <p className="text-sm text-gray-600 mt-1">Track emotions & get insights</p>
                      </div>
                    </div>
                  </button>

                  {/* COMMUNITY FEED BUTTON */}
                  <button
                    onClick={() => setActiveTab('feed')}
                    className={`w-full text-left p-3 rounded-lg border transition-colors group ${
                      activeTab === 'feed'
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-300 hover:border-blue-500 hover:bg-blue-50'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <BarChart3 className={`h-5 w-5 ${
                        activeTab === 'feed' ? 'text-blue-700' : 'text-blue-600 group-hover:text-blue-700'
                      }`} />
                      <div>
                        <span className="font-medium">📱 Community Feed</span>
                        <p className="text-sm text-gray-600 mt-1">Connect with others</p>
                      </div>
                    </div>
                  </button>

                  {/* SAVED POSTS BUTTON - NEW ADDITION */}
                  <Link href="/dashboard/saved">
                    <button className="w-full text-left p-3 rounded-lg border border-gray-300 hover:border-purple-500 hover:bg-purple-50 transition-colors group">
                      <div className="flex items-center gap-3">
                        <Bookmark className="h-5 w-5 text-purple-600 group-hover:text-purple-700" />
                        <div>
                          <span className="font-medium">📑 Saved Posts</span>
                          <p className="text-sm text-gray-600 mt-1">Your bookmarked content</p>
                        </div>
                      </div>
                    </button>
                  </Link>

                  {/* CRISIS SUPPORT BUTTON */}
                  <Link href="/dashboard/crisis">
                    <button className="w-full text-left p-3 rounded-lg border border-gray-300 hover:border-red-500 hover:bg-red-50 transition-colors group">
                      <div className="flex items-center gap-3">
                        <Shield className="h-5 w-5 text-red-600 group-hover:text-red-700" />
                        <div>
                          <span className="font-medium">🆘 Crisis Support</span>
                          <p className="text-sm text-gray-600 mt-1">Immediate help & resources</p>
                        </div>
                      </div>
                    </button>
                  </Link>

                  {/* JOURNAL BUTTON */}
                  <Link href="/dashboard/journals">
                    <button className="w-full text-left p-3 rounded-lg border border-gray-300 hover:border-green-500 hover:bg-green-50 transition-colors group">
                      <div className="flex items-center gap-3">
                        <BookOpen className="h-5 w-5 text-green-600 group-hover:text-green-700" />
                        <div>
                          <span className="font-medium">📔 Personal Journal</span>
                          <p className="text-sm text-gray-600 mt-1">Write private reflections</p>
                        </div>
                      </div>
                    </button>
                  </Link>

                  {/* FIND USERS BUTTON */}
                  <Link href="/dashboard/users">
                    <button className="w-full text-left p-3 rounded-lg border border-gray-300 hover:border-orange-500 hover:bg-orange-50 transition-colors group">
                      <div className="flex items-center gap-3">
                        <Users className="h-5 w-5 text-orange-600 group-hover:text-orange-700" />
                        <div>
                          <span className="font-medium">👥 Find Users</span>
                          <p className="text-sm text-gray-600 mt-1">Connect with community members</p>
                        </div>
                      </div>
                    </button>
                  </Link>

                  {/* ANALYTICS BUTTON */}
                  <button className="w-full text-left p-3 rounded-lg border border-gray-300 hover:border-indigo-500 hover:bg-indigo-50 transition-colors">
                    <span className="font-medium">📊 Advanced Analytics</span>
                    <p className="text-sm text-gray-600 mt-1">Deep insights & patterns</p>
                  </button>
                </div>
              </div>

              {/* Mood Quick Stats */}
              {activeTab === 'mood' && (
                <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg border border-purple-200 shadow-sm p-6">
                  <h3 className="font-semibold mb-3 text-purple-900">Mood Tracking Benefits</h3>
                  <div className="space-y-2 text-sm text-purple-800">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                      <span>Identify emotional patterns</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                      <span>Track triggers & coping strategies</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                      <span>Get professional insights</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                      <span>Monitor mental health progress</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Community Stats */}
              {activeTab === 'feed' && (
                <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-lg border border-blue-200 shadow-sm p-6">
                  <h3 className="font-semibold mb-3 text-blue-900">Community Support</h3>
                  <div className="space-y-2 text-sm text-blue-800">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                      <span>Share experiences safely</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                      <span>Connect with understanding peers</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                      <span>Give and receive support</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                      <span>Build meaningful connections</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
