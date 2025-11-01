'use client';

import { useState, useEffect } from 'react';
import { useCrisisStore } from '@/stores/crisis-store';
import { UserCrisisPreferencesCreate, UserCrisisPreferencesUpdate } from '@/types/crisis';
import { Settings, Save, Loader2, AlertCircle, Shield, Languages, MapPin, Stethoscope } from 'lucide-react';

const LANGUAGE_OPTIONS = [
  { value: 'en', label: 'English' },
  { value: 'sw', label: 'Swahili' },
  { value: 'lg', label: 'Luganda' },
  { value: 'es', label: 'Spanish' },
  { value: 'fr', label: 'French' },
  { value: 'de', label: 'German' },
  { value: 'pt', label: 'Portuguese' },
  { value: 'zh', label: 'Chinese' },
  { value: 'ja', label: 'Japanese' },
];

const COUNTRY_OPTIONS = [
  { value: 'UG', label: 'Uganda' },
  { value: 'US', label: 'United States' },
  { value: 'CA', label: 'Canada' },
  { value: 'GB', label: 'United Kingdom' },
  { value: 'AU', label: 'Australia' },
  { value: 'KE', label: 'Kenya' },
  { value: 'TZ', label: 'Tanzania' },
  { value: 'ZA', label: 'South Africa' },
  { value: 'NG', label: 'Nigeria' },
  { value: 'ET', label: 'Ethiopia' },
  { value: 'DE', label: 'Germany' },
  { value: 'FR', label: 'France' },
  { value: 'JP', label: 'Japan' },
  { value: 'BR', label: 'Brazil' },
];

export default function CrisisPreferences() {
  const {
    preferences,
    preferencesLoading,
    preferencesError,
    getPreferences,
    createPreferences,
    updatePreferences,
    clearErrors
  } = useCrisisStore();

  const [formData, setFormData] = useState({
    preferred_language: 'en',
    country_code: '',
    emergency_contact_instructions: '',
    medical_information: '',
    consent_to_contact: false
  });
  const [isEditing, setIsEditing] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    getPreferences();
  }, [getPreferences]);

  useEffect(() => {
    if (preferences && !isEditing) {
      setFormData({
        preferred_language: preferences.preferred_language || 'en',
        country_code: preferences.country_code || '',
        emergency_contact_instructions: preferences.emergency_contact_instructions || '',
        medical_information: preferences.medical_information || '',
        consent_to_contact: preferences.consent_to_contact || false
      });
    }
  }, [preferences, isEditing]);

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setHasChanges(true);
  };

  const handleSave = async () => {
    const preferencesData: UserCrisisPreferencesUpdate = {
      preferred_language: formData.preferred_language,
      country_code: formData.country_code || undefined,
      emergency_contact_instructions: formData.emergency_contact_instructions || undefined,
      medical_information: formData.medical_information || undefined,
      consent_to_contact: formData.consent_to_contact
    };

    try {
      if (preferences) {
        await updatePreferences(preferencesData);
      } else {
        await createPreferences(preferencesData as UserCrisisPreferencesCreate);
      }
      setIsEditing(false);
      setHasChanges(false);
      await getPreferences(); // Refresh data
    } catch (error) {
      // Error handled by store
    }
  };

  const handleCancel = () => {
    if (preferences) {
      setFormData({
        preferred_language: preferences.preferred_language || 'en',
        country_code: preferences.country_code || '',
        emergency_contact_instructions: preferences.emergency_contact_instructions || '',
        medical_information: preferences.medical_information || '',
        consent_to_contact: preferences.consent_to_contact || false
      });
    }
    setIsEditing(false);
    setHasChanges(false);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-500 to-indigo-600 rounded-lg text-white p-6">
        <div className="flex items-center gap-3 mb-2">
          <Settings className="h-8 w-8" />
          <h2 className="text-2xl font-bold">Crisis Preferences</h2>
        </div>
        <p className="opacity-90">
          Configure your crisis support settings and emergency information for better assistance.
        </p>
      </div>

      {/* Error Display */}
      {preferencesError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center gap-2 text-red-800">
            <AlertCircle className="h-4 w-4" />
            <p>{preferencesError}</p>
          </div>
          <button
            onClick={clearErrors}
            className="mt-2 text-red-600 hover:text-red-800 text-sm"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Preferences Form */}
      <div className="bg-white rounded-lg border shadow-sm p-6">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-semibold text-gray-900">
            Your Crisis Support Settings
          </h3>

          <div className="flex gap-2">
            {isEditing ? (
              <>
                <button
                  onClick={handleSave}
                  disabled={preferencesLoading || !hasChanges}
                  className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
                >
                  {preferencesLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Save className="h-4 w-4" />
                  )}
                  Save Changes
                </button>
                <button
                  onClick={handleCancel}
                  className="border border-gray-300 px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
              </>
            ) : (
              <button
                onClick={() => setIsEditing(true)}
                className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-2"
              >
                <Settings className="h-4 w-4" />
                Edit Preferences
              </button>
            )}
          </div>
        </div>

        <div className="space-y-6">
          {/* Language Preference */}
          <div className="border-b border-gray-200 pb-6">
            <div className="flex items-center gap-3 mb-4">
              <Languages className="h-5 w-5 text-purple-600" />
              <h4 className="font-semibold text-gray-900">Language Preference</h4>
            </div>
            <p className="text-sm text-gray-600 mb-3">
              Choose your preferred language for crisis support resources and communication.
            </p>
            <select
              value={formData.preferred_language}
              onChange={(e) => handleInputChange('preferred_language', e.target.value)}
              disabled={!isEditing}
              className="w-full max-w-xs border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500 focus:border-purple-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
            >
              {LANGUAGE_OPTIONS.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          {/* Location Information */}
          <div className="border-b border-gray-200 pb-6">
            <div className="flex items-center gap-3 mb-4">
              <MapPin className="h-5 w-5 text-blue-600" />
              <h4 className="font-semibold text-gray-900">Location Information</h4>
            </div>
            <p className="text-sm text-gray-600 mb-3">
              Help us provide location-relevant crisis resources and support.
            </p>
            <select
              value={formData.country_code}
              onChange={(e) => handleInputChange('country_code', e.target.value)}
              disabled={!isEditing}
              className="w-full max-w-xs border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
            >
              <option value="">Select your country</option>
              {COUNTRY_OPTIONS.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          {/* Emergency Contact Instructions */}
          <div className="border-b border-gray-200 pb-6">
            <div className="flex items-center gap-3 mb-4">
              <Shield className="h-5 w-5 text-green-600" />
              <h4 className="font-semibold text-gray-900">Emergency Contact Instructions</h4>
            </div>
            <p className="text-sm text-gray-600 mb-3">
              Special instructions for emergency contacts when they are notified.
            </p>
            <textarea
              value={formData.emergency_contact_instructions}
              onChange={(e) => handleInputChange('emergency_contact_instructions', e.target.value)}
              disabled={!isEditing}
              rows={3}
              placeholder="e.g., Please call my sister first, I have medication allergies..."
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-green-500 focus:border-green-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
            />
          </div>

          {/* Medical Information */}
          <div className="border-b border-gray-200 pb-6">
            <div className="flex items-center gap-3 mb-4">
              <Stethoscope className="h-5 w-5 text-red-600" />
              <h4 className="font-semibold text-gray-900">Medical Information</h4>
            </div>
            <p className="text-sm text-gray-600 mb-3">
              Important medical information that emergency responders should know.
            </p>
            <textarea
              value={formData.medical_information}
              onChange={(e) => handleInputChange('medical_information', e.target.value)}
              disabled={!isEditing}
              rows={4}
              placeholder="e.g., Allergies: penicillin, Conditions: asthma, Current medications..."
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-red-500 focus:border-red-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
            />
          </div>

          {/* Consent Settings */}
          <div>
            <div className="flex items-center gap-3 mb-4">
              <Shield className="h-5 w-5 text-orange-600" />
              <h4 className="font-semibold text-gray-900">Consent & Privacy</h4>
            </div>
            <p className="text-sm text-gray-600 mb-3">
              Control how your information is used during crisis situations.
            </p>
            <label className="flex items-start gap-3 p-4 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
              <input
                type="checkbox"
                checked={formData.consent_to_contact}
                onChange={(e) => handleInputChange('consent_to_contact', e.target.checked)}
                disabled={!isEditing}
                className="mt-1 rounded border-gray-300 text-purple-600 focus:ring-purple-500 disabled:bg-gray-100"
              />
              <div>
                <p className="font-medium text-gray-900">Consent to Emergency Contact</p>
                <p className="text-sm text-gray-600 mt-1">
                  I consent to having my emergency contacts notified in crisis situations.
                  This allows your designated contacts to be reached when you need support.
                </p>
              </div>
            </label>
          </div>
        </div>
      </div>

      {/* Current Settings Display */}
      {!isEditing && preferences && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-6">
          <div className="flex items-center gap-2 text-green-800 mb-4">
            <Settings className="h-5 w-5" />
            <h4 className="font-semibold">Current Settings</h4>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <span className="font-medium text-gray-700">Language:</span>{' '}
              {LANGUAGE_OPTIONS.find(lang => lang.value === preferences.preferred_language)?.label || preferences.preferred_language}
            </div>
            <div>
              <span className="font-medium text-gray-700">Country:</span>{' '}
              {preferences.country_code ?
                COUNTRY_OPTIONS.find(country => country.value === preferences.country_code)?.label || preferences.country_code
                : 'Not set'}
            </div>
            <div>
              <span className="font-medium text-gray-700">Contact Consent:</span>{' '}
              {preferences.consent_to_contact ? 'Granted' : 'Not granted'}
            </div>
            <div>
              <span className="font-medium text-gray-700">Last Updated:</span>{' '}
              {new Date(preferences.updated_at).toLocaleDateString()}
            </div>
          </div>
        </div>
      )}

      {/* No Preferences Set */}
      {!preferences && !preferencesLoading && !isEditing && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <div className="flex items-center gap-2 text-yellow-800 mb-4">
            <AlertCircle className="h-5 w-5" />
            <h4 className="font-semibold">No Preferences Set</h4>
          </div>
          <p className="text-yellow-700 mb-4">
            You haven't set up your crisis support preferences yet.
            Configuring these settings helps ensure you get the most relevant support during crisis situations.
          </p>
          <button
            onClick={() => setIsEditing(true)}
            className="bg-yellow-600 text-white px-4 py-2 rounded-lg hover:bg-yellow-700 transition-colors"
          >
            Set Up Preferences
          </button>
        </div>
      )}

      {/* Loading State */}
      {preferencesLoading && (
        <div className="flex justify-center items-center py-8">
          <Loader2 className="h-8 w-8 animate-spin text-purple-600" />
          <span className="ml-2 text-gray-600">Loading preferences...</span>
        </div>
      )}
    </div>
  );
}
