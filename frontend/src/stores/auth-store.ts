import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User, LoginRequest, RegisterRequest, AuthResponse } from '@/types/auth';
import { apiClient } from '@/lib/api-client';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  login: (credentials: LoginRequest) => Promise<void>;
  register: (userData: RegisterRequest) => Promise<void>;
  logout: () => void;
  getCurrentUser: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (credentials: LoginRequest) => {
        set({ isLoading: true, error: null });
        try {
          const authResponse: AuthResponse = await apiClient.login(credentials);
          const user = await apiClient.getCurrentUser();
          set({ 
            user, 
            isAuthenticated: true, 
            isLoading: false,
            error: null 
          });
          // Redirect to home page after successful login
          if (typeof window !== 'undefined') {
            window.location.href = '/';
          }
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Login failed',
            isLoading: false 
          });
          throw error;
        }
      },

      register: async (userData: RegisterRequest) => {
        set({ isLoading: true, error: null });
        try {
          const user = await apiClient.register(userData);
          // Auto-login after registration
          const authResponse = await apiClient.login({
            email: userData.email,
            password: userData.password
          });
          const currentUser = await apiClient.getCurrentUser();
          set({ 
            user: currentUser, 
            isAuthenticated: true, 
            isLoading: false,
            error: null 
          });
          // Redirect to home page after successful registration
          if (typeof window !== 'undefined') {
            window.location.href = '/';
          }
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Registration failed',
            isLoading: false 
          });
          throw error;
        }
      },

      logout: () => {
        apiClient.logout();
        set({ 
          user: null, 
          isAuthenticated: false,
          error: null 
        });
        // Redirect to home page after logout
        if (typeof window !== 'undefined') {
          window.location.href = '/';
        }
      },

      getCurrentUser: async () => {
        if (!apiClient.isAuthenticated()) {
          set({ isAuthenticated: false, user: null });
          return;
        }

        set({ isLoading: true });
        try {
          const user = await apiClient.getCurrentUser();
          set({ 
            user, 
            isAuthenticated: true, 
            isLoading: false 
          });
        } catch (error) {
          // Token might be expired, clear auth state
          apiClient.logout();
          set({ 
            user: null, 
            isAuthenticated: false, 
            isLoading: false 
          });
        }
      },

      clearError: () => {
        set({ error: null });
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ 
        user: state.user,
        isAuthenticated: state.isAuthenticated 
      }),
    }
  )
);
