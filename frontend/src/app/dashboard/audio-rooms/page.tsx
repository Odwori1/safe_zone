// FILE: src/app/dashboard/audio-rooms/page.tsx (UPDATED)
'use client';
import { useState, useEffect } from 'react';
import { useAudioRoomsStore } from '@/stores/audio-rooms-store';
import CreateAudioRoomForm from '@/components/audio-rooms/create-audio-room-form';
import AudioRoomsFilter from '@/components/audio-rooms/audio-rooms-filter';
import { AudioRoom } from '@/types/audio-rooms';

export default function AudioRoomsPage() {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [filters, setFilters] = useState({
    search: '',
    roomType: 'all',
    visibility: 'all'
  });
  const [filteredRooms, setFilteredRooms] = useState<AudioRoom[]>([]);
  
  const { rooms, fetchRooms, isLoading, error } = useAudioRoomsStore();

  useEffect(() => {
    fetchRooms();
  }, [fetchRooms]);

  useEffect(() => {
    // Apply filters whenever rooms or filters change
    const filtered = rooms.filter(room => {
      const matchesSearch = !filters.search || 
        room.title.toLowerCase().includes(filters.search.toLowerCase()) ||
        (room.description && room.description.toLowerCase().includes(filters.search.toLowerCase()));
      
      const matchesRoomType = filters.roomType === 'all' || room.room_type === filters.roomType;
      const matchesVisibility = filters.visibility === 'all' || room.visibility === filters.visibility;
      
      return matchesSearch && matchesRoomType && matchesVisibility;
    });
    
    setFilteredRooms(filtered);
  }, [rooms, filters]);

  const handleFilterChange = (newFilters: any) => {
    setFilters(newFilters);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Live Audio Rooms
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Join supportive conversations in real-time
          </p>
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
        >
          Create Room
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6 dark:bg-red-900/20 dark:border-red-800 dark:text-red-400">
          {error}
        </div>
      )}

      {/* Filters */}
      <AudioRoomsFilter onFilterChange={handleFilterChange} />

      {showCreateForm && (
        <CreateAudioRoomForm onClose={() => setShowCreateForm(false)} />
      )}

      {isLoading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="border rounded-lg p-4 animate-pulse">
              <div className="h-4 bg-gray-200 rounded mb-2"></div>
              <div className="h-3 bg-gray-200 rounded mb-4 w-3/4"></div>
              <div className="flex justify-between">
                <div className="h-6 bg-gray-200 rounded w-20"></div>
                <div className="h-6 bg-gray-200 rounded w-16"></div>
              </div>
            </div>
          ))}
        </div>
      ) : filteredRooms.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-400 dark:text-gray-500 text-6xl mb-4">🎙️</div>
          <h3 className="text-xl font-semibold text-gray-600 dark:text-gray-400 mb-2">
            {rooms.length === 0 ? 'No audio rooms yet' : 'No rooms match your filters'}
          </h3>
          <p className="text-gray-500 dark:text-gray-500">
            {rooms.length === 0 
              ? 'Be the first to create a supportive space for conversation'
              : 'Try adjusting your search or filters'
            }
          </p>
          {rooms.length === 0 && (
            <button
              onClick={() => setShowCreateForm(true)}
              className="mt-4 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Create First Room
            </button>
          )}
        </div>
      ) : (
        <>
          <div className="flex justify-between items-center mb-4">
            <p className="text-gray-600 dark:text-gray-400">
              Showing {filteredRooms.length} of {rooms.length} rooms
            </p>
            {filters.search || filters.roomType !== 'all' || filters.visibility !== 'all' ? (
              <button
                onClick={() => setFilters({ search: '', roomType: 'all', visibility: 'all' })}
                className="text-blue-600 hover:text-blue-700 text-sm"
              >
                Clear filters
              </button>
            ) : null}
          </div>
          
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {filteredRooms.map((room) => (
              <div
                key={room.id}
                className="border border-gray-200 dark:border-gray-600 rounded-lg p-6 hover:shadow-lg transition-shadow cursor-pointer bg-white dark:bg-gray-800"
                onClick={() => {
                  window.location.href = `/dashboard/audio-rooms/${room.id}`;
                }}
              >
                <div className="flex justify-between items-start mb-3">
                  <h3 className="font-semibold text-lg text-gray-900 dark:text-white line-clamp-2">
                    {room.title}
                  </h3>
                  {room.is_active && (
                    <div className="flex items-center">
                      <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
                      <span className="text-green-600 dark:text-green-400 text-sm font-medium">Live</span>
                    </div>
                  )}
                </div>
                
                {room.description && (
                  <p className="text-gray-600 dark:text-gray-400 text-sm mb-4 line-clamp-2">
                    {room.description}
                  </p>
                )}
                
                <div className="flex justify-between items-center text-sm">
                  <div className="flex gap-2">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      room.room_type === 'support' 
                        ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' 
                        : 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400'
                    }`}>
                      {room.room_type}
                    </span>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      room.visibility === 'public'
                        ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400'
                        : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-400'
                    }`}>
                      {room.visibility}
                    </span>
                  </div>
                  
                  <span className="text-gray-500 dark:text-gray-400 font-medium">
                    {room.current_participants}/{room.max_participants}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
