import { create } from 'zustand';
import { 
  CrisisResource, 
  CrisisResourcesResponse, 
  EmergencyContact, 
  EmergencyContactCreate, 
  EmergencyContactUpdate,
  EmergencyContactsResponse,
  UserCrisisPreferences,
  UserCrisisPreferencesCreate,
  UserCrisisPreferencesUpdate,
  ResourceRecommendationResponse,
  CrisisSearchFilters
} from '@/types/crisis';
import { apiClient } from '@/lib/api-client';

interface CrisisState {
  // Resources
  resources: CrisisResource[];
  resourcesLoading: boolean;
  resourcesError: string | null;
  
  // Emergency Contacts
  contacts: EmergencyContact[];
  contactsLoading: boolean;
  contactsError: string | null;
  contactCreateLoading: boolean;
  contactUpdateLoading: { [contactId: string]: boolean };
  contactDeleteLoading: { [contactId: string]: boolean };
  
  // Preferences
  preferences: UserCrisisPreferences | null;
  preferencesLoading: boolean;
  preferencesError: string | null;
  
  // Recommendations
  recommendations: CrisisResource[];
  recommendationsLoading: boolean;
  recommendationsError: string | null;

  // Actions
  // Resources
  getResources: (filters?: CrisisSearchFilters) => Promise<void>;
  searchResources: (query: string, limit?: number) => Promise<void>;
  getRecommendations: (mood?: string, content?: string, category?: string, limit?: number) => Promise<void>;
  
  // Emergency Contacts
  getContacts: () => Promise<void>;
  createContact: (contactData: EmergencyContactCreate) => Promise<void>;
  updateContact: (contactId: string, contactData: EmergencyContactUpdate) => Promise<void>;
  deleteContact: (contactId: string) => Promise<void>;
  
  // Preferences
  getPreferences: () => Promise<void>;
  createPreferences: (preferencesData: UserCrisisPreferencesCreate) => Promise<void>;
  updatePreferences: (preferencesData: UserCrisisPreferencesUpdate) => Promise<void>;
  
  // Common
  clearErrors: () => void;
  clearResources: () => void;
}

export const useCrisisStore = create<CrisisState>((set, get) => ({
  // Initial State
  resources: [],
  resourcesLoading: false,
  resourcesError: null,
  
  contacts: [],
  contactsLoading: false,
  contactsError: null,
  contactCreateLoading: false,
  contactUpdateLoading: {},
  contactDeleteLoading: {},
  
  preferences: null,
  preferencesLoading: false,
  preferencesError: null,
  
  recommendations: [],
  recommendationsLoading: false,
  recommendationsError: null,

  // Resources Actions
  getResources: async (filters = {}) => {
    console.log('🔄 CRISIS STORE: Getting resources...', { filters });
    set({ resourcesLoading: true, resourcesError: null });

    try {
      const { category, geographic_scope, limit = 50, offset = 0 } = filters;
      
      const params = new URLSearchParams({
        limit: limit.toString(),
        page: Math.floor(offset / limit + 1).toString(),
      });

      if (category) params.append('category', category);
      if (geographic_scope) params.append('geographic_scope', geographic_scope);

      const response = await apiClient.request(`/api/v1/crisis-support/resources/?${params}`);
      console.log('📥 CRISIS STORE: Resources response status:', response.status);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to fetch crisis resources`);
      }

      const data: CrisisResourcesResponse = await response.json();
      console.log('✅ CRISIS STORE: Received', data.resources.length, 'resources');

      set({ 
        resources: data.resources,
        resourcesLoading: false 
      });

    } catch (error) {
      console.error('❌ CRISIS STORE: Error fetching resources:', error);
      set({
        resourcesError: error instanceof Error ? error.message : 'Failed to fetch crisis resources',
        resourcesLoading: false,
        resources: []
      });
    }
  },

  searchResources: async (query: string, limit = 20) => {
    console.log('🔄 CRISIS STORE: Searching resources...', { query, limit });
    set({ resourcesLoading: true, resourcesError: null });

    try {
      const response = await apiClient.request(`/api/v1/crisis-support/resources/search/?q=${encodeURIComponent(query)}&limit=${limit}`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to search crisis resources`);
      }

      const data: CrisisResourcesResponse = await response.json();
      console.log('✅ CRISIS STORE: Search found', data.resources.length, 'resources');

      set({ 
        resources: data.resources,
        resourcesLoading: false 
      });

    } catch (error) {
      console.error('❌ CRISIS STORE: Error searching resources:', error);
      set({
        resourcesError: error instanceof Error ? error.message : 'Failed to search crisis resources',
        resourcesLoading: false,
        resources: []
      });
    }
  },

  getRecommendations: async (mood?: string, content?: string, category?: string, limit = 5) => {
    console.log('🔄 CRISIS STORE: Getting recommendations...', { mood, content, category, limit });
    set({ recommendationsLoading: true, recommendationsError: null });

    try {
      const params = new URLSearchParams({ limit: limit.toString() });
      if (mood) params.append('mood', mood);
      if (content) params.append('content', content);
      if (category) params.append('category', category);

      const response = await apiClient.request(`/api/v1/crisis-support/resources/recommendations/?${params}`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to get recommendations`);
      }

      const data: ResourceRecommendationResponse = await response.json();
      console.log('✅ CRISIS STORE: Received', data.resources.length, 'recommendations');

      set({ 
        recommendations: data.resources,
        recommendationsLoading: false 
      });

    } catch (error) {
      console.error('❌ CRISIS STORE: Error getting recommendations:', error);
      set({
        recommendationsError: error instanceof Error ? error.message : 'Failed to get recommendations',
        recommendationsLoading: false,
        recommendations: []
      });
    }
  },

  // Emergency Contacts Actions
  getContacts: async () => {
    console.log('🔄 CRISIS STORE: Getting emergency contacts...');
    set({ contactsLoading: true, contactsError: null });

    try {
      const response = await apiClient.request('/api/v1/crisis-support/emergency-contacts/');
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to fetch emergency contacts`);
      }

      const data: EmergencyContactsResponse = await response.json();
      console.log('✅ CRISIS STORE: Received', data.contacts.length, 'contacts');

      set({ 
        contacts: data.contacts,
        contactsLoading: false 
      });

    } catch (error) {
      console.error('❌ CRISIS STORE: Error fetching contacts:', error);
      set({
        contactsError: error instanceof Error ? error.message : 'Failed to fetch emergency contacts',
        contactsLoading: false,
        contacts: []
      });
    }
  },

  createContact: async (contactData: EmergencyContactCreate) => {
    console.log('🔄 CRISIS STORE: Creating contact...', contactData);
    set({ contactCreateLoading: true, contactsError: null });

    try {
      const response = await apiClient.request('/api/v1/crisis-support/emergency-contacts/', {
        method: 'POST',
        body: JSON.stringify(contactData),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to create emergency contact`);
      }

      const newContact: EmergencyContact = await response.json();
      console.log('✅ CRISIS STORE: Contact created successfully:', newContact.id);

      // Add new contact to the list
      set((state) => ({
        contacts: [...state.contacts, newContact],
        contactCreateLoading: false
      }));

      return newContact;

    } catch (error) {
      console.error('❌ CRISIS STORE: Create contact error:', error);
      set({
        contactsError: error instanceof Error ? error.message : 'Failed to create emergency contact',
        contactCreateLoading: false
      });
      throw error;
    }
  },

  updateContact: async (contactId: string, contactData: EmergencyContactUpdate) => {
    console.log('🔄 CRISIS STORE: Updating contact:', contactId, contactData);
    set(state => ({
      contactUpdateLoading: { ...state.contactUpdateLoading, [contactId]: true },
      contactsError: null
    }));

    try {
      const response = await apiClient.request(`/api/v1/crisis-support/emergency-contacts/${contactId}`, {
        method: 'PUT',
        body: JSON.stringify(contactData),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to update emergency contact`);
      }

      const updatedContact: EmergencyContact = await response.json();
      console.log('✅ CRISIS STORE: Contact updated successfully:', updatedContact.id);

      // Update contact in the list
      set((state) => ({
        contacts: state.contacts.map(contact =>
          contact.id === contactId ? updatedContact : contact
        ),
        contactUpdateLoading: { ...state.contactUpdateLoading, [contactId]: false }
      }));

      return updatedContact;

    } catch (error) {
      console.error('❌ CRISIS STORE: Update contact error:', error);
      set(state => ({
        contactsError: error instanceof Error ? error.message : 'Failed to update emergency contact',
        contactUpdateLoading: { ...state.contactUpdateLoading, [contactId]: false }
      }));
      throw error;
    }
  },

  deleteContact: async (contactId: string) => {
    console.log('🔄 CRISIS STORE: Deleting contact:', contactId);
    set(state => ({
      contactDeleteLoading: { ...state.contactDeleteLoading, [contactId]: true },
      contactsError: null
    }));

    try {
      const response = await apiClient.request(`/api/v1/crisis-support/emergency-contacts/${contactId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to delete emergency contact`);
      }

      // Remove contact from local state immediately
      set((state) => ({
        contacts: state.contacts.filter(contact => contact.id !== contactId),
        contactDeleteLoading: { ...state.contactDeleteLoading, [contactId]: false }
      }));

      console.log('✅ CRISIS STORE: Contact deleted successfully:', contactId);

    } catch (error) {
      console.error('❌ CRISIS STORE: Delete contact error:', error);
      set(state => ({
        contactsError: error instanceof Error ? error.message : 'Failed to delete emergency contact',
        contactDeleteLoading: { ...state.contactDeleteLoading, [contactId]: false }
      }));
      throw error;
    }
  },

  // Preferences Actions
  getPreferences: async () => {
    console.log('🔄 CRISIS STORE: Getting crisis preferences...');
    set({ preferencesLoading: true, preferencesError: null });

    try {
      const response = await apiClient.request('/api/v1/crisis-support/preferences/');
      
      if (!response.ok) {
        if (response.status === 404) {
          // Preferences not found is normal for first-time users
          console.log('ℹ️ CRISIS STORE: No preferences found (normal for first-time users)');
          set({ preferences: null, preferencesLoading: false });
          return;
        }
        throw new Error(`HTTP ${response.status}: Failed to fetch crisis preferences`);
      }

      const preferences: UserCrisisPreferences = await response.json();
      console.log('✅ CRISIS STORE: Received preferences');

      set({ 
        preferences,
        preferencesLoading: false 
      });

    } catch (error) {
      console.error('❌ CRISIS STORE: Error fetching preferences:', error);
      set({
        preferencesError: error instanceof Error ? error.message : 'Failed to fetch crisis preferences',
        preferencesLoading: false
      });
    }
  },

  createPreferences: async (preferencesData: UserCrisisPreferencesCreate) => {
    console.log('🔄 CRISIS STORE: Creating preferences...', preferencesData);
    set({ preferencesLoading: true, preferencesError: null });

    try {
      const response = await apiClient.request('/api/v1/crisis-support/preferences/', {
        method: 'POST',
        body: JSON.stringify(preferencesData),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to create crisis preferences`);
      }

      const newPreferences: UserCrisisPreferences = await response.json();
      console.log('✅ CRISIS STORE: Preferences created successfully');

      set({ 
        preferences: newPreferences,
        preferencesLoading: false 
      });

      return newPreferences;

    } catch (error) {
      console.error('❌ CRISIS STORE: Create preferences error:', error);
      set({
        preferencesError: error instanceof Error ? error.message : 'Failed to create crisis preferences',
        preferencesLoading: false
      });
      throw error;
    }
  },

  updatePreferences: async (preferencesData: UserCrisisPreferencesUpdate) => {
    console.log('🔄 CRISIS STORE: Updating preferences...', preferencesData);
    set({ preferencesLoading: true, preferencesError: null });

    try {
      const response = await apiClient.request('/api/v1/crisis-support/preferences/', {
        method: 'PUT',
        body: JSON.stringify(preferencesData),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to update crisis preferences`);
      }

      const updatedPreferences: UserCrisisPreferences = await response.json();
      console.log('✅ CRISIS STORE: Preferences updated successfully');

      set({ 
        preferences: updatedPreferences,
        preferencesLoading: false 
      });

      return updatedPreferences;

    } catch (error) {
      console.error('❌ CRISIS STORE: Update preferences error:', error);
      set({
        preferencesError: error instanceof Error ? error.message : 'Failed to update crisis preferences',
        preferencesLoading: false
      });
      throw error;
    }
  },

  // Common Actions
  clearErrors: () => set({ 
    resourcesError: null, 
    contactsError: null, 
    preferencesError: null,
    recommendationsError: null 
  }),

  clearResources: () => set({ resources: [], recommendations: [] }),
}));
