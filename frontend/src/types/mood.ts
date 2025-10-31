// Complete Mood Types based on robust backend features
// Generated from actual API responses

export interface MoodEntry {
  id: string;
  user_id: string;
  mood: string;
  intensity: number;
  notes?: string;
  source_type: 'standalone' | 'post' | 'journal';
  source_id?: string;
  triggers: string[];
  activities: string[];
  physical_symptoms: string[];
  social_context?: string;
  sleep_quality?: number;
  energy_level?: number;
  location?: string;
  weather?: string;
  duration_minutes?: number;
  medication_taken: boolean;
  medication_notes?: string;
  created_at: string;
  updated_at: string;
  
  // Professional analysis fields (from backend validators)
  mood_category: string;
  energy_level_category?: string;
  valence?: string;
  clinical_insights?: string[];
}

export interface MoodStatistics {
  total_entries: number;
  average_intensity: number;
  most_common_mood: string;
  mood_frequency: Record<string, number>;
  weekly_trend: Array<{
    date: string;
    avg_intensity: number;
    entry_count: number;
  }>;
  source_distribution: Array<{
    source_type: string;
    count: number;
  }>;
  top_triggers: Array<{
    trigger: string;
    count: number;
  }>;
  top_activities: Array<{
    activity: string;
    count: number;
  }>;
}

export interface EnhancedMoodStats extends MoodStatistics {
  category_distribution: Record<string, number>;
  clinical_insights?: {
    dominant_category?: string;
    pattern_insights: string[];
    clinical_recommendations: string[];
    risk_factors: string[];
    positive_patterns: string[];
  };
}

export interface ClinicalInsights {
  dominant_category?: string;
  pattern_insights: string[];
  clinical_recommendations: string[];
  risk_factors: string[];
  positive_patterns: string[];
}

export interface MoodTaxonomy {
  total_moods: number;
  categories: {
    positive_high_energy: string[];
    positive_low_energy: string[];
    negative_high_energy: string[];
    negative_low_energy: string[];
    neutral_states: string[];
    mixed_states: string[];
    clinical_states: string[];
  };
}

export interface MoodCreate {
  mood: string;
  intensity: number;
  notes?: string;
  triggers?: string[];
  activities?: string[];
  physical_symptoms?: string[];
  social_context?: string;
  sleep_quality?: number;
  energy_level?: number;
  location?: string;
  weather?: string;
  duration_minutes?: number;
  medication_taken?: boolean;
  medication_notes?: string;
}

export interface HybridMoodResponse {
  count: number;
  entries: MoodEntry[];
}

export interface MoodHistoryResponse {
  entries: MoodEntry[];
  total: number;
  page: number;
  has_next: boolean;
}

// Mood category types for UI
export type MoodCategory = 
  | 'positive_high_energy'
  | 'positive_low_energy' 
  | 'negative_high_energy'
  | 'negative_low_energy'
  | 'neutral_states'
  | 'mixed_states'
  | 'clinical_states';

export interface MoodCategoryInfo {
  name: MoodCategory;
  label: string;
  description: string;
  color: string;
  moods: string[];
}

export const MOOD_CATEGORIES: Record<MoodCategory, MoodCategoryInfo> = {
  positive_high_energy: {
    name: 'positive_high_energy',
    label: 'Positive High Energy',
    description: 'Energetic, motivated, and enthusiastic states',
    color: '#10B981',
    moods: ['joyful', 'excited', 'enthusiastic', 'energetic', 'euphoric', 'inspired', 'motivated', 'confident', 'proud', 'accomplished', 'optimistic', 'hopeful', 'determined']
  },
  positive_low_energy: {
    name: 'positive_low_energy',
    label: 'Positive Low Energy',
    description: 'Calm, peaceful, and content states',
    color: '#059669',
    moods: ['calm', 'peaceful', 'content', 'serene', 'relaxed', 'grateful', 'appreciative', 'satisfied', 'fulfilled', 'balanced']
  },
  negative_high_energy: {
    name: 'negative_high_energy',
    label: 'Negative High Energy',
    description: 'Anxious, angry, and agitated states',
    color: '#EF4444',
    moods: ['anxious', 'angry', 'frustrated', 'irritated', 'agitated', 'stressed', 'overwhelmed', 'panicked', 'restless', 'tense']
  },
  negative_low_energy: {
    name: 'negative_low_energy',
    label: 'Negative Low Energy',
    description: 'Sad, depressed, and exhausted states',
    color: '#8B5CF6',
    moods: ['sad', 'depressed', 'lonely', 'empty', 'hopeless', 'fatigued', 'exhausted', 'numb', 'apathetic', 'withdrawn']
  },
  neutral_states: {
    name: 'neutral_states',
    label: 'Neutral States',
    description: 'Focused, present, and mindful states',
    color: '#6B7280',
    moods: ['neutral', 'focused', 'present', 'mindful', 'contemplative', 'reflective', 'curious', 'observant']
  },
  mixed_states: {
    name: 'mixed_states',
    label: 'Mixed States',
    description: 'Complex emotional states with mixed feelings',
    color: '#F59E0B',
    moods: ['bittersweet', 'nostalgic', 'melancholic', 'conflicted', 'ambivalent', 'uncertain', 'vulnerable', 'sensitive']
  },
  clinical_states: {
    name: 'clinical_states',
    label: 'Clinical States',
    description: 'States that may require professional attention',
    color: '#DC2626',
    moods: ['dissociated', 'triggered', 'manic', 'hypomanic', 'paranoid', 'obsessive', 'compulsive']
  }
};
