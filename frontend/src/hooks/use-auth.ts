import { useEffect } from 'react';
import { useAuthStore } from '@/stores/auth-store';

export const useAuth = () => {
  const {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    register,
    logout,
    getCurrentUser,
    clearError
  } = useAuthStore();

  // Only check current user if we don't have one but think we're authenticated
  useEffect(() => {
    console.log('🔐 useAuth effect running', { user, isAuthenticated });
    
    // Only call getCurrentUser if we think we're authenticated but don't have user data
    // OR if we need to validate the token
    if (isAuthenticated && !user) {
      console.log('🔄 Checking current user...');
      getCurrentUser();
    }
    // If we're not authenticated, ensure clean state
    else if (!isAuthenticated && user) {
      console.log('🧹 Clearing inconsistent auth state');
      // This should be handled by the store, but just in case
    }
  }, [isAuthenticated, user, getCurrentUser]);

  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    register,
    logout,
    clearError,
  };
};
