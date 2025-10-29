export interface User {
  id: string;
  email: string;
  username: string;
  full_name?: string;
  profile_picture?: string;
  timezone: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  username: string;
  full_name?: string;
  timezone: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}
