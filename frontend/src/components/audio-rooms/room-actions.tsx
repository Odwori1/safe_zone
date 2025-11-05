// FILE: src/components/audio-rooms/room-actions.tsx
'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/use-auth';
import { AudioRoom } from '@/types/audio-rooms';
import { apiClient } from '@/lib/api-client';

interface RoomActionsProps {
  room: AudioRoom;
  onRoomUpdated?: () => void;
  onRoomDeleted?: () => void;
}

export default function RoomActions({ room, onRoomUpdated, onRoomDeleted }: RoomActionsProps) {
  const { user } = useAuth();
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const isOwner = room.created_by.id === user?.id;

  if (!isOwner) return null;

  const deleteRoom = async () => {
    try {
      setIsLoading(true);
      const response = await apiClient.request(`/api/v1/audio/rooms/${room.id}`, {
        method: 'DELETE',
      });
      
      if (response.ok) {
        onRoomDeleted?.();
        router.push('/dashboard/audio-rooms');
      }
    } catch (error) {
      console.error('Failed to delete room:', error);
    } finally {
      setIsLoading(false);
      setShowDeleteConfirm(false);
    }
  };

  const editRoom = () => {
    // For Phase 3, we'll use a simple alert. In Phase 4 we can implement full edit modal.
    const newTitle = prompt('Enter new room title:', room.title);
    if (newTitle && newTitle !== room.title) {
      updateRoomTitle(newTitle);
    }
  };

  const updateRoomTitle = async (newTitle: string) => {
    try {
      const response = await apiClient.request(`/api/v1/audio/rooms/${room.id}`, {
        method: 'PATCH',
        body: JSON.stringify({ title: newTitle }),
      });
      
      if (response.ok) {
        onRoomUpdated?.();
        // Refresh the page to show updated title
        window.location.reload();
      }
    } catch (error) {
      console.error('Failed to update room:', error);
      alert('Failed to update room title');
    }
  };

  return (
    <div className="flex gap-2 mt-4 pt-4 border-t border-gray-200 dark:border-gray-600">
      <button
        onClick={editRoom}
        className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
      >
        Edit Title
      </button>
      
      {showDeleteConfirm ? (
        <div className="flex gap-2">
          <button
            onClick={deleteRoom}
            disabled={isLoading}
            className="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50 transition-colors"
          >
            {isLoading ? 'Deleting...' : 'Confirm Delete'}
          </button>
          <button
            onClick={() => setShowDeleteConfirm(false)}
            className="px-3 py-1 text-sm bg-gray-500 text-white rounded hover:bg-gray-600 transition-colors"
          >
            Cancel
          </button>
        </div>
      ) : (
        <button
          onClick={() => setShowDeleteConfirm(true)}
          className="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
        >
          Delete Room
        </button>
      )}
    </div>
  );
}
