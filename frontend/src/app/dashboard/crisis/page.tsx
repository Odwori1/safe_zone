'use client';

import { useState } from 'react';
import ProtectedRoute from '@/components/auth/protected-route';
import CrisisResources from '@/components/crisis/crisis-resources';
import EmergencyContacts from '@/components/crisis/emergency-contacts';
import CrisisPreferences from '@/components/crisis/crisis-preferences';
import { AlertTriangle, Users, Settings, Phone, Heart, Shield, MapPin } from 'lucide-react';

const tabs = [
  { id: 'resources', name: 'Crisis Resources', icon: AlertTriangle, color: 'text-red-600' },
  { id: 'contacts', name: 'Emergency Contacts', icon: Users, color: 'text-blue-600' },
  { id: 'preferences', name: 'Preferences', icon: Settings, color: 'text-purple-600' },
];

export default function CrisisPage() {
  const [activeTab, setActiveTab] = useState('resources');

  const renderTabContent = () => {
    switch (activeTab) {
      case 'resources':
        return <CrisisResources />;
      case 'contacts':
        return <EmergencyContacts />;
      case 'preferences':
        return <CrisisPreferences />;
      default:
        return <CrisisResources />;
    }
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4">
          {/* Header */}
          <div className="mb-8">
            <div className="flex items-center gap-4 mb-4">
              <div className="bg-red-100 p-3 rounded-full">
                <Shield className="h-8 w-8 text-red-600" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Crisis Support</h1>
                <p className="text-gray-600 mt-1">
                  Immediate help, emergency contacts, and support resources
                </p>
              </div>
            </div>

            {/* Emergency Alert Banner */}
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
              <div className="flex items-center gap-3">
                <AlertTriangle className="h-5 w-5 text-red-600" />
                <div className="flex-1">
                  <p className="font-medium text-red-800">Emergency Support Available 24/7</p>
                  <p className="text-red-700 text-sm mt-1">
                    If you're in immediate danger or experiencing a mental health crisis,
                    please call emergency services or use the resources below.
                  </p>
                </div>
                <div className="flex gap-2">
                  <a
                    href="tel:911"
                    className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors flex items-center gap-2 text-sm"
                  >
                    <Phone className="h-4 w-4" />
                    Call 911
                  </a>
                  <a
                    href="tel:988"
                    className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-2 text-sm"
                  >
                    <Heart className="h-4 w-4" />
                    988 Lifeline
                  </a>
                </div>
              </div>
            </div>

            {/* Uganda Specific Emergency Info */}
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
              <div className="flex items-center gap-3">
                <MapPin className="h-5 w-5 text-yellow-600" />
                <div className="flex-1">
                  <p className="font-medium text-yellow-800">Uganda Emergency Services</p>
                  <p className="text-yellow-700 text-sm mt-1">
                    If you are in Uganda, here are the local emergency numbers:
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-2 mt-2">
                    <div className="text-sm">
                      <span className="font-medium">Police:</span> 999 or 112
                    </div>
                    <div className="text-sm">
                      <span className="font-medium">Ambulance:</span> 102 or 112
                    </div>
                    <div className="text-sm">
                      <span className="font-medium">Mental Health Helpline:</span> 0800 200 600
                    </div>
                  </div>
                </div>
                <a
                  href="tel:999"
                  className="bg-yellow-600 text-white px-4 py-2 rounded-lg hover:bg-yellow-700 transition-colors flex items-center gap-2 text-sm"
                >
                  <Phone className="h-4 w-4" />
                  Call 999
                </a>
              </div>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="flex space-x-1 mb-8 bg-white p-1 rounded-lg border shadow-sm">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;

              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex-1 py-3 px-4 rounded-md text-center font-medium transition-all ${
                    isActive
                      ? 'bg-gradient-to-r from-red-500 to-orange-600 text-white shadow-sm'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  }`}
                >
                  <div className="flex items-center justify-center gap-2">
                    <Icon className={`h-4 w-4 ${isActive ? 'text-white' : tab.color}`} />
                    <span>{tab.name}</span>
                  </div>
                </button>
              );
            })}
          </div>

          {/* Tab Content */}
          <div className="animate-in fade-in duration-300">
            {renderTabContent()}
          </div>

          {/* Quick Actions Footer */}
          <div className="mt-12 bg-white rounded-lg border shadow-sm p-6">
            <h3 className="font-semibold text-lg mb-4 text-gray-900">Quick Crisis Support</h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <a
                href="tel:988"
                className="p-4 border border-purple-200 rounded-lg hover:border-purple-500 hover:bg-purple-50 transition-colors group"
              >
                <div className="flex items-center gap-3">
                  <div className="bg-purple-100 p-2 rounded-full group-hover:bg-purple-200 transition-colors">
                    <Phone className="h-5 w-5 text-purple-600" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">988 Suicide & Crisis Lifeline</p>
                    <p className="text-sm text-gray-600">Call or text 24/7</p>
                  </div>
                </div>
              </a>

              <a
                href="tel:999"
                className="p-4 border border-yellow-200 rounded-lg hover:border-yellow-500 hover:bg-yellow-50 transition-colors group"
              >
                <div className="flex items-center gap-3">
                  <div className="bg-yellow-100 p-2 rounded-full group-hover:bg-yellow-200 transition-colors">
                    <MapPin className="h-5 w-5 text-yellow-600" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">Uganda Police Emergency</p>
                    <p className="text-sm text-gray-600">Call 999 or 112</p>
                  </div>
                </div>
              </a>

              <a
                href="tel:0800200600"
                className="p-4 border border-blue-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors group"
              >
                <div className="flex items-center gap-3">
                  <div className="bg-blue-100 p-2 rounded-full group-hover:bg-blue-200 transition-colors">
                    <Heart className="h-5 w-5 text-blue-600" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">Uganda Mental Health Helpline</p>
                    <p className="text-sm text-gray-600">Call 0800 200 600</p>
                  </div>
                </div>
              </a>

              <a
                href="tel:911"
                className="p-4 border border-red-200 rounded-lg hover:border-red-500 hover:bg-red-50 transition-colors group"
              >
                <div className="flex items-center gap-3">
                  <div className="bg-red-100 p-2 rounded-full group-hover:bg-red-200 transition-colors">
                    <Shield className="h-5 w-5 text-red-600" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">Emergency Services</p>
                    <p className="text-sm text-gray-600">Call 911 for immediate help</p>
                  </div>
                </div>
              </a>
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
