'use client';

import { useAuth } from '@/hooks/use-auth';
import Link from 'next/link';

export default function Home() {
  const { user, isAuthenticated, isLoading, logout } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-blue-600">Safe Zone</h1>
              <span className="ml-2 px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">
                Foundation Ready
              </span>
            </div>
            
            <div className="flex items-center space-x-4">
              {isAuthenticated ? (
                <>
                  <span className="text-gray-700">Welcome, {user?.username}</span>
                  <Link
                    href="/dashboard"
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Dashboard
                  </Link>
                  <button
                    onClick={logout}
                    className="bg-gray-500 text-white px-4 py-2 rounded-lg hover:bg-gray-600 transition-colors"
                  >
                    Logout
                  </button>
                </>
              ) : (
                <div className="space-x-2">
                  <a
                    href="/auth/login"
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Login
                  </a>
                  <a
                    href="/auth/register"
                    className="border border-blue-600 text-blue-600 px-4 py-2 rounded-lg hover:bg-blue-50 transition-colors"
                  >
                    Sign Up
                  </a>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Safe Zone - Mental Health Support
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            A secure platform for mental health support and community
          </p>
        </div>

        {/* Status Dashboard */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
          <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
            <h3 className="text-lg font-semibold mb-2 text-green-600">✓ Foundation</h3>
            <p className="text-gray-600">
              Next.js 14, React 18, TypeScript, and Tailwind CSS configured
            </p>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
            <h3 className="text-lg font-semibold mb-2 text-green-600">✓ Authentication</h3>
            <p className="text-gray-600">
              JWT authentication system integrated with backend API
            </p>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
            <h3 className={`text-lg font-semibold mb-2 ${isAuthenticated ? 'text-green-600' : 'text-blue-600'}`}>
              {isAuthenticated ? '✓ Authenticated' : '🔒 Ready to Login'}
            </h3>
            <p className="text-gray-600">
              {isAuthenticated 
                ? `Welcome ${user?.email}` 
                : 'Secure login and registration available'
              }
            </p>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-semibold mb-2">Secure Community</h3>
            <p className="text-gray-600">
              Connect with others in a safe, moderated environment with full privacy protection.
            </p>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-semibold mb-2">Real-time Support</h3>
            <p className="text-gray-600">
              Live audio rooms and messaging for immediate support when you need it most.
            </p>
          </div>
        </div>

        {/* Authentication Status */}
        <div className="mt-12 text-center">
          <div className="bg-white rounded-lg border border-gray-200 p-6 max-w-md mx-auto">
            <h3 className="text-lg font-semibold mb-4">Authentication Status</h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>Logged In:</span>
                <span className={isAuthenticated ? 'text-green-600 font-semibold' : 'text-red-600'}>
                  {isAuthenticated ? 'Yes' : 'No'}
                </span>
              </div>
              {user && (
                <>
                  <div className="flex justify-between">
                    <span>User:</span>
                    <span className="font-medium">{user.username}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Email:</span>
                    <span className="font-medium">{user.email}</span>
                  </div>
                  {isAuthenticated && (
                    <div className="pt-4">
                      <Link 
                        href="/dashboard" 
                        className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
                      >
                        Go to Dashboard →
                      </Link>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      </main>

      {/* Crisis Button - Always Accessible */}
      <div className="fixed bottom-6 right-6 z-50">
        <button className="bg-red-600 text-white px-6 py-3 rounded-lg font-semibold shadow-lg hover:bg-red-700 transition-colors">
          Emergency Help
        </button>
      </div>
    </div>
  );
}
