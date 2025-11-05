// FILE: src/components/audio-rooms/create-audio-room-form.tsx
'use client';
import { useState } from 'react';
import { useAudioRoomsStore } from '@/stores/audio-rooms-store';
import { CreateAudioRoomData } from '@/types/audio-rooms';

interface CreateAudioRoomFormProps {
  onClose: () => void;
}

export default function CreateAudioRoomForm({ onClose }: CreateAudioRoomFormProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [roomType, setRoomType] = useState<'support' | 'discussion' | 'social'>('support');
  const [maxParticipants, setMaxParticipants] = useState(10);
  const [isPublic, setIsPublic] = useState(true);
  
  const { createRoom, isLoading, error } = useAudioRoomsStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createRoom({
        title,
        description,
        room_type: roomType,
        max_participants: maxParticipants,
        is_public: isPublic,
      });
      onClose();
    } catch (error) {
      // Error handled by store
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white p-6 rounded-lg w-full max-w-md">
        <h2 className="text-xl font-bold mb-4">Create Audio Room</h2>
        
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Room Title *</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-md"
              placeholder="What's this room about?"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-md"
              rows={3}
              placeholder="Optional description for your room..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Room Type</label>
            <select
              value={roomType}
              onChange={(e) => setRoomType(e.target.value as any)}
              className="w-full p-2 border border-gray-300 rounded-md"
            >
              <option value="support">Support</option>
              <option value="discussion">Discussion</option>
              <option value="social">Social</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              Max Participants: <span className="font-semibold">{maxParticipants}</span>
            </label>
            <input
              type="range"
              min="2"
              max="50"
              value={maxParticipants}
              onChange={(e) => setMaxParticipants(parseInt(e.target.value))}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>2</span>
              <span>50</span>
            </div>
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="is_public"
              checked={isPublic}
              onChange={(e) => setIsPublic(e.target.checked)}
              className="mr-2"
            />
            <label htmlFor="is_public" className="text-sm">
              Public Room (visible to everyone)
            </label>
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
              disabled={isLoading}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading || !title.trim()}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {isLoading ? 'Creating...' : 'Create Room'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
