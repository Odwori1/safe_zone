'use client';

import { useState, useEffect } from 'react';
import { useCrisisStore } from '@/stores/crisis-store';
import { EmergencyContact, EmergencyContactCreate, EmergencyContactUpdate } from '@/types/crisis';
import { Plus, Phone, Mail, Edit3, Trash2, Star, Loader2, AlertCircle, Users, Shield } from 'lucide-react';

interface ContactFormData {
  name: string;
  relationship: string;
  phone_number: string;
  email: string;
  is_primary: boolean;
  can_receive_alerts: boolean;
  notes: string;
}

export default function EmergencyContacts() {
  const {
    contacts,
    contactsLoading,
    contactsError,
    contactCreateLoading,
    contactUpdateLoading,
    contactDeleteLoading,
    getContacts,
    createContact,
    updateContact,
    deleteContact,
    clearErrors
  } = useCrisisStore();

  const [showForm, setShowForm] = useState(false);
  const [editingContact, setEditingContact] = useState<EmergencyContact | null>(null);
  const [formData, setFormData] = useState<ContactFormData>({
    name: '',
    relationship: '',
    phone_number: '',
    email: '',
    is_primary: false,
    can_receive_alerts: true,
    notes: ''
  });

  useEffect(() => {
    getContacts();
  }, [getContacts]);

  const resetForm = () => {
    setFormData({
      name: '',
      relationship: '',
      phone_number: '',
      email: '',
      is_primary: false,
      can_receive_alerts: true,
      notes: ''
    });
    setEditingContact(null);
    setShowForm(false);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const contactData: EmergencyContactCreate = {
      name: formData.name.trim(),
      relationship: formData.relationship.trim() || undefined,
      phone_number: formData.phone_number.trim(),
      email: formData.email.trim() || undefined,
      is_primary: formData.is_primary,
      can_receive_alerts: formData.can_receive_alerts,
      notes: formData.notes.trim() || undefined
    };

    try {
      if (editingContact) {
        await updateContact(editingContact.id, contactData);
      } else {
        await createContact(contactData);
      }
      resetForm();
      await getContacts(); // Refresh the list
    } catch (error) {
      // Error handled by store
    }
  };

  const handleEdit = (contact: EmergencyContact) => {
    setFormData({
      name: contact.name,
      relationship: contact.relationship || '',
      phone_number: contact.phone_number,
      email: contact.email || '',
      is_primary: contact.is_primary,
      can_receive_alerts: contact.can_receive_alerts,
      notes: contact.notes || ''
    });
    setEditingContact(contact);
    setShowForm(true);
  };

  const handleDelete = async (contactId: string) => {
    if (window.confirm('Are you sure you want to delete this emergency contact?')) {
      try {
        await deleteContact(contactId);
        await getContacts(); // Refresh the list
      } catch (error) {
        // Error handled by store
      }
    }
  };

  const handleSetPrimary = async (contactId: string) => {
    try {
      await updateContact(contactId, { is_primary: true });
      await getContacts(); // Refresh to update primary status
    } catch (error) {
      // Error handled by store
    }
  };

  const ContactCard = ({ contact }: { contact: EmergencyContact }) => (
    <div className={`bg-white rounded-lg border shadow-sm p-6 ${
      contact.is_primary ? 'border-yellow-400 ring-2 ring-yellow-200' : 'border-gray-200'
    }`}>
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-center gap-3">
          <h3 className="font-semibold text-lg text-gray-900">{contact.name}</h3>
          {contact.is_primary && (
            <span className="flex items-center gap-1 bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full text-xs font-medium">
              <Star className="h-3 w-3 fill-current" />
              Primary
            </span>
          )}
          {contact.can_receive_alerts && (
            <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-medium">
              Alerts Enabled
            </span>
          )}
        </div>
        
        <div className="flex items-center gap-2">
          {!contact.is_primary && (
            <button
              onClick={() => handleSetPrimary(contact.id)}
              disabled={contactUpdateLoading[contact.id]}
              className="p-1 text-yellow-600 hover:text-yellow-700 disabled:opacity-50"
              title="Set as primary"
            >
              <Star className="h-4 w-4" />
            </button>
          )}
          <button
            onClick={() => handleEdit(contact)}
            disabled={contactUpdateLoading[contact.id]}
            className="p-1 text-blue-600 hover:text-blue-700 disabled:opacity-50"
          >
            <Edit3 className="h-4 w-4" />
          </button>
          <button
            onClick={() => handleDelete(contact.id)}
            disabled={contactDeleteLoading[contact.id]}
            className="p-1 text-red-600 hover:text-red-700 disabled:opacity-50"
          >
            {contactDeleteLoading[contact.id] ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Trash2 className="h-4 w-4" />
            )}
          </button>
        </div>
      </div>

      <div className="space-y-3">
        {contact.relationship && (
          <p className="text-gray-600">
            <span className="font-medium">Relationship:</span> {contact.relationship}
          </p>
        )}

        <div className="flex items-center gap-2">
          <Phone className="h-4 w-4 text-green-600" />
          <a 
            href={`tel:${contact.phone_number}`}
            className="text-green-600 hover:text-green-700 font-medium"
          >
            {contact.phone_number}
          </a>
        </div>

        {contact.email && (
          <div className="flex items-center gap-2">
            <Mail className="h-4 w-4 text-blue-600" />
            <a 
              href={`mailto:${contact.email}`}
              className="text-blue-600 hover:text-blue-700"
            >
              {contact.email}
            </a>
          </div>
        )}

        {contact.notes && (
          <div>
            <p className="text-sm font-medium text-gray-700 mb-1">Notes:</p>
            <p className="text-sm text-gray-600 bg-gray-50 rounded p-2">{contact.notes}</p>
          </div>
        )}

        <div className="flex justify-between items-center pt-3 border-t border-gray-100">
          <span className="text-xs text-gray-500">
            Added {new Date(contact.created_at).toLocaleDateString()}
          </span>
          {contact.updated_at !== contact.created_at && (
            <span className="text-xs text-gray-500">
              Updated {new Date(contact.updated_at).toLocaleDateString()}
            </span>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-500 to-cyan-600 rounded-lg text-white p-6">
        <div className="flex items-center gap-3 mb-2">
          <Users className="h-8 w-8" />
          <h2 className="text-2xl font-bold">Emergency Contacts</h2>
        </div>
        <p className="opacity-90">
          Manage your trusted emergency contacts who can be notified in crisis situations.
        </p>
      </div>

      {/* Stats Card */}
      <div className="bg-white rounded-lg border shadow-sm p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{contacts.length}</div>
            <div className="text-sm text-gray-600">Total Contacts</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-600">
              {contacts.filter(c => c.is_primary).length}
            </div>
            <div className="text-sm text-gray-600">Primary Contacts</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {contacts.filter(c => c.can_receive_alerts).length}
            </div>
            <div className="text-sm text-gray-600">Alert Enabled</div>
          </div>
        </div>
      </div>

      {/* Error Display */}
      {contactsError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center gap-2 text-red-800">
            <AlertCircle className="h-4 w-4" />
            <p>{contactsError}</p>
          </div>
          <button
            onClick={clearErrors}
            className="mt-2 text-red-600 hover:text-red-800 text-sm"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Add Contact Button */}
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-gray-900">
          Your Emergency Contacts ({contacts.length})
        </h3>
        <button
          onClick={() => setShowForm(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
        >
          <Plus className="h-4 w-4" />
          Add Contact
        </button>
      </div>

      {/* Contact Form */}
      {showForm && (
        <div className="bg-white rounded-lg border shadow-sm p-6">
          <h3 className="text-lg font-semibold mb-4">
            {editingContact ? 'Edit Contact' : 'Add New Emergency Contact'}
          </h3>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Full Name *
                </label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="John Doe"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Relationship
                </label>
                <input
                  type="text"
                  value={formData.relationship}
                  onChange={(e) => setFormData({ ...formData, relationship: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Friend, Family, etc."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Phone Number *
                </label>
                <input
                  type="tel"
                  required
                  value={formData.phone_number}
                  onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="+1234567890"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="email@example.com"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Notes
              </label>
              <textarea
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Any additional information about this contact..."
              />
            </div>

            <div className="flex flex-wrap gap-6">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={formData.is_primary}
                  onChange={(e) => setFormData({ ...formData, is_primary: e.target.checked })}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm font-medium text-gray-700">Set as primary contact</span>
              </label>

              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={formData.can_receive_alerts}
                  onChange={(e) => setFormData({ ...formData, can_receive_alerts: e.target.checked })}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm font-medium text-gray-700">Can receive crisis alerts</span>
              </label>
            </div>

            <div className="flex gap-3 pt-4">
              <button
                type="submit"
                disabled={contactCreateLoading || contactUpdateLoading[editingContact?.id || '']}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
              >
                {(contactCreateLoading || contactUpdateLoading[editingContact?.id || '']) ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Shield className="h-4 w-4" />
                )}
                {editingContact ? 'Update Contact' : 'Add Contact'}
              </button>
              
              <button
                type="button"
                onClick={resetForm}
                className="border border-gray-300 px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Contacts List */}
      {contacts.length === 0 && !contactsLoading ? (
        <div className="bg-gray-50 rounded-lg p-8 text-center">
          <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 mb-4">No emergency contacts added yet</p>
          <button
            onClick={() => setShowForm(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Add Your First Contact
          </button>
        </div>
      ) : (
        <div className="grid gap-4">
          {contacts.map((contact) => (
            <ContactCard key={contact.id} contact={contact} />
          ))}
        </div>
      )}

      {/* Loading State */}
      {contactsLoading && (
        <div className="flex justify-center items-center py-8">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
          <span className="ml-2 text-gray-600">Loading contacts...</span>
        </div>
      )}
    </div>
  );
}
