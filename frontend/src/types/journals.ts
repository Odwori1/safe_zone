export interface JournalCreate {
  title: string;
  content: string;
  mood?: string;
  mood_intensity?: number;
  tags?: string[];
  is_private?: boolean;
  prompt_id?: string;
}

export interface JournalUpdate {
  title?: string;
  content?: string;
  mood?: string;
  mood_intensity?: number;
  tags?: string[];
  is_private?: boolean;
  status?: string;
}

export interface JournalResponse {
  id: string;
  user_id: string;
  title: string;
  content: string;
  mood?: string;
  mood_intensity?: number;
  tags: string[];
  word_count: number;
  read_time_minutes: number;
  is_private: boolean;
  status: string;
  prompt_id?: string;
  created_at: string;
  updated_at: string;
  prompt_text?: string;
  prompt_category?: string;
}

export interface JournalStats {
  total_entries: number;
  total_words: number;
  average_mood: number;
  most_used_tags: string[];
  entries_this_week: number;
  entries_this_month: number;
  most_common_mood: string;
}

export interface JournalPrompt {
  id: string;
  prompt_text: string;
  category: string;
  difficulty_level: string;
  is_active: boolean;
  created_at: string;
}

export interface JournalFeedResponse {
  entries: JournalResponse[];
  total: number;
  page: number;
  has_next: boolean;
}
