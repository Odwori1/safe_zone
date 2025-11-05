import { AuthResponse, LoginRequest, RegisterRequest, User } from '@/types/auth';

class ApiClient {
  private baseURL: string;
  private accessToken: string | null = null;

  constructor() {
    this.baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
    this.initializeToken();
    console.log('🔧 API Client initialized. Base URL:', this.baseURL);
    console.log('🔧 Initial token:', this.accessToken ? 'Present' : 'Missing');
    // ADDED: Better token debugging
    if (this.accessToken) {
      console.log('🔧 Token preview:', this.accessToken.substring(0, 20) + '...');
    }
  }

  private initializeToken() {
    if (typeof window !== 'undefined') {
      this.accessToken = localStorage.getItem('access_token');
      console.log('🔄 Token initialized from localStorage:', this.accessToken ? 'Present' : 'Missing');
      // ADDED: Check if token exists but might be invalid
      if (this.accessToken) {
        console.log('🔄 Token length:', this.accessToken.length);
      }
    }
  }

  private setAccessToken(token: string) {
    this.accessToken = token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', token);
    }
    console.log('✅ Token set:', token.substring(0, 20) + '...');
  }

  private clearTokens() {
    this.accessToken = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
    }
    console.log('🗑️ Tokens cleared');
  }

  async request(endpoint: string, options: RequestInit = {}): Promise<Response> {
    const url = `${this.baseURL}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    // Add authorization header if token exists
    if (this.accessToken) {
      headers['Authorization'] = `Bearer ${this.accessToken}`;
      console.log('🔐 Sending request with Authorization header');
      console.log('🔐 Token preview in request:', this.accessToken.substring(0, 20) + '...');
    } else {
      console.log('⚠️ Sending request WITHOUT Authorization header');
      console.log('⚠️ Current accessToken value:', this.accessToken);
    }

    console.log('📤 Making request:', options.method || 'GET', url);
    console.log('📤 Headers:', Object.keys(headers));

    const response = await fetch(url, {
      ...options,
      headers,
    });

    console.log('📥 Response status:', response.status, response.statusText);
    console.log('📥 Response URL:', response.url);

    // If token is invalid or expired, clear it
    if (response.status === 401) {
      console.log('🔐 401 Unauthorized - clearing tokens');
      this.clearTokens();
    }

    return response;
  }

  // Authentication methods
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    console.log('🔐 Login attempt with:', credentials.email);
    const response = await this.request(process.env.NEXT_PUBLIC_AUTH_LOGIN!, {
      method: 'POST',
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error('❌ Login failed:', errorData);
      throw new Error(errorData.detail || 'Login failed');
    }

    const authData: AuthResponse = await response.json();
    this.setAccessToken(authData.access_token);
    console.log('✅ Login successful');
    return authData;
  }

  async register(userData: RegisterRequest): Promise<User> {
    console.log('👤 Registration attempt for:', userData.email);
    const response = await this.request(process.env.NEXT_PUBLIC_AUTH_REGISTER!, {
      method: 'POST',
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error('❌ Registration failed:', errorData);
      throw new Error(errorData.detail || 'Registration failed');
    }

    const user: User = await response.json();
    console.log('✅ Registration successful');
    return user;
  }

  async getCurrentUser(): Promise<User> {
    console.log('👤 Fetching current user');
    const response = await this.request(process.env.NEXT_PUBLIC_AUTH_ME!);

    if (!response.ok) {
      console.error('❌ Failed to fetch current user');
      throw new Error('Failed to fetch current user');
    }

    const user = await response.json();
    console.log('✅ Current user fetched:', user.username);
    return user;
  }

  async logout(): Promise<void> {
    console.log('🚪 Logging out');
    this.clearTokens();
  }

  isAuthenticated(): boolean {
    const authenticated = !!this.accessToken;
    console.log('🔐 Authentication check:', authenticated);
    return authenticated;
  }

  getAccessToken(): string | null {
    return this.accessToken;
  }

  // File upload method - FIXED: Better error handling and debugging
  async uploadFile(fileData: {
    file_name: string;
    original_filename: string;
    file_size: number;
    mime_type: string;
    file_type: 'audio' | 'video' | 'image' | 'document';
  }): Promise<{ upload_url: string; file_id: string }> {
    console.log('📤 API Client: Requesting upload URL with data:', fileData);

    try {
      // ADDED: Check authentication before making request
      if (!this.accessToken) {
        console.error('❌ API Client: No access token available for upload');
        throw new Error('Authentication required for file upload');
      }

      const response = await this.request('/api/v1/uploads/presigned-url', {
        method: 'POST',
        body: JSON.stringify(fileData),
      });

      console.log('📥 API Client: Upload URL response status:', response.status);

      if (!response.ok) {
        let errorData;
        try {
          errorData = await response.json();
          console.error('❌ API Client: Upload URL request failed with JSON error:', errorData);
        } catch (e) {
          const errorText = await response.text();
          console.error('❌ API Client: Upload URL request failed with text error:', errorText);
          errorData = { detail: errorText };
        }
        
        // ADDED: Specific handling for 403
        if (response.status === 403) {
          console.error('❌ API Client: Access forbidden - token might be invalid');
          this.clearTokens(); // Clear invalid token
        }
        
        throw new Error(`Upload URL request failed: ${response.status} - ${JSON.stringify(errorData)}`);
      }

      const backendResponse = await response.json();
      console.log('✅ API Client: Backend response received:', backendResponse);

      // Transform backend response to match frontend expectations
      const uploadInfo = {
        upload_url: backendResponse.presigned_url,
        file_id: backendResponse.upload_id,
        file_key: backendResponse.file_key,
        method: backendResponse.method,
        headers: backendResponse.headers,
        expires_in: backendResponse.expires_in
      };

      console.log('🔄 API Client: Transformed upload info:', uploadInfo);
      return uploadInfo;

    } catch (error) {
      console.error('❌ API Client: Upload URL request failed:', error);
      throw error;
    }
  }
}

export const apiClient = new ApiClient();
