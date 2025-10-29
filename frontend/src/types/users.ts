export interface UserSearchResult {
  id: string;
  username: string;
  full_name: string | null;
  bio: string | null;
  profile_picture: string | null;
  is_helper: boolean;
  helper_specialties: string | null;
  created_at: string;
  is_following?: boolean;
  relationship_status?: UserRelationshipStatus; // ADD THIS
}

export interface UserSearchResults {
  users: UserSearchResult[];
  total: number;
  has_more: boolean;
}

export interface UsersFilter {
  query?: string;
  limit?: number;
  offset?: number;
}

// ADD THESE NEW TYPES
export interface UserRelationshipStatus {
  is_following: boolean;
  is_blocked: boolean;
  is_blocked_by: boolean;
}

export interface BlockRequest {
  blocked_user_id: string;
}

export interface ReportRequest {
  reported_user_id: string;
  report_reason: string;
  report_details?: string;
}
