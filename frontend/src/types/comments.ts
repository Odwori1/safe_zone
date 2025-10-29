export interface CommentCreate {
  post_id: string;
  content: string;
  parent_comment_id?: string | null;
  is_anonymous?: boolean;
}

export interface CommentResponse {
  id: string;
  created_at: string;
  updated_at: string;
  user_id: string;
  post_id: string;
  parent_comment_id: string | null;
  content: string;
  is_anonymous: boolean;
  status: 'active' | 'archived' | 'deleted';
  moderation_status: 'pending' | 'approved' | 'rejected';
  username: string | null;
  user_avatar: string | null;
  replies: CommentResponse[];
  like_count?: number;
  user_has_liked?: boolean;
  reply_count?: number;
}

export interface CommentUpdate {
  content?: string;
  is_anonymous?: boolean;
}

export interface CommentFeedResponse {
  comments: CommentResponse[];
  total: number;
  page: number;
  has_next: boolean;
}
