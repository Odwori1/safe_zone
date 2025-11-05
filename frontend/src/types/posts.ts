export interface PostCreate {
  content: string;
  content_type: 'text' | 'journal' | 'audio' | 'video'; // REMOVED 'image' - images are 'text' with image_url
  mood?: string;
  visibility: 'public' | 'private' | 'support_group';
  is_anonymous: boolean;
  audio_url?: string | null;
  audio_duration?: number | null;
  video_url?: string | null;
  video_duration?: number | null;
  image_url?: string | null; // Images use 'text' content_type with image_url
  file_attachments?: string[];
}

export interface PostResponse {
  id: string;
  created_at: string;
  updated_at: string;
  user_id: string;
  content: string;
  content_type: 'text' | 'journal' | 'audio' | 'video';
  mood: string | null;
  visibility: 'public' | 'private' | 'support_group';
  is_anonymous: boolean;
  status: 'active' | 'archived' | 'deleted';
  moderation_status: 'pending' | 'approved' | 'rejected';
  audio_url: string | null;
  audio_duration: number | null;
  file_size: number | null;
  mime_type: string | null;
  video_url: string | null;
  video_duration: number | null;
  thumbnail_url: string | null;
  video_width: number | null;
  video_height: number | null;
  image_url: string | null;
  file_attachments: string[];
  username: string | null;
  user_avatar: string | null;
  like_count?: number;
  comment_count?: number;
  user_has_liked?: boolean;
  share_count?: number;
  user_has_shared?: boolean;
}

export interface PostUpdate {
  content?: string;
  mood?: string;
  visibility?: 'public' | 'private' | 'support_group';
  is_anonymous?: boolean;
}

export interface PostsFilter {
  skip?: number;
  limit?: number;
  content_type?: string;
  mood?: string;
  visibility?: string;
  user_id?: string;
  search?: string;
}

export interface ShareResponse {
  message: string;
  already_shared: boolean;
  share_count: number;
  shareable_url: string;
  instructions?: string;
}
