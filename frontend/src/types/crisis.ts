export interface CrisisResource {
  id: string;
  name: string;
  description: string;
  category: string;
  phone_number?: string;
  website_url?: string;
  chat_url?: string;
  text_line?: string;
  languages: string[];
  operating_hours: any | null;
  geographic_scope: string;
  is_active: boolean;
  priority: number;
  tags: string[];
  created_at: string;
  updated_at: string;
}

export interface CrisisResourcesResponse {
  resources: CrisisResource[];
  total: number;
  user_location?: string;
}

export interface EmergencyContact {
  id: string;
  user_id: string;
  name: string;
  relationship?: string;
  phone_number: string;
  email?: string;
  is_primary: boolean;
  can_receive_alerts: boolean;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface EmergencyContactCreate {
  name: string;
  relationship?: string;
  phone_number: string;
  email?: string;
  is_primary?: boolean;
  can_receive_alerts?: boolean;
  notes?: string;
}

export interface EmergencyContactUpdate {
  name?: string;
  relationship?: string;
  phone_number?: string;
  email?: string;
  is_primary?: boolean;
  can_receive_alerts?: boolean;
  notes?: string;
}

export interface EmergencyContactsResponse {
  contacts: EmergencyContact[];
  total: number;
  has_primary: boolean;
}

export interface UserCrisisPreferences {
  user_id: string;
  preferred_language: string;
  country_code?: string;
  emergency_contact_instructions?: string;
  medical_information?: string;
  consent_to_contact: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserCrisisPreferencesCreate {
  preferred_language: string;
  country_code?: string;
  emergency_contact_instructions?: string;
  medical_information?: string;
  consent_to_contact?: boolean;
}

export interface UserCrisisPreferencesUpdate {
  preferred_language?: string;
  country_code?: string;
  emergency_contact_instructions?: string;
  medical_information?: string;
  consent_to_contact?: boolean;
}

export interface ResourceRecommendationResponse {
  resources: CrisisResource[];
  recommendations_based_on: {
    mood?: string;
    content_analysis?: boolean;
  };
  user_preferences_used: boolean;
}

export interface CrisisSearchFilters {
  category?: string;
  geographic_scope?: string;
  limit?: number;
  offset?: number;
}
