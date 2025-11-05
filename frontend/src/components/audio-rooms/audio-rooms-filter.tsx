// FILE: src/components/audio-rooms/audio-rooms-filter.tsx
'use client';
import { useState } from 'react';

interface AudioRoomsFilterProps {
  onFilterChange: (filters: {
    search: string;
    roomType: string;
    visibility: string;
  }) => void;
}

export default function AudioRoomsFilter({ onFilterChange }: AudioRoomsFilterProps) {
  const [search, setSearch] = useState('');
  const [roomType, setRoomType] = useState('all');
  const [visibility, setVisibility] = useState('all');

  const handleSearchChange = (value: string) => {
    setSearch(value);
    onFilterChange({ search: value, roomType, visibility });
  };

  const handleRoomTypeChange = (value: string) => {
    setRoomType(value);
    onFilterChange({ search, roomType: value, visibility });
  };

  const handleVisibilityChange = (value: string) => {
    setVisibility(value);
    onFilterChange({ search, roomType, visibility: value });
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border p-4 mb-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Search */}
        <div>
          <label className="block text-sm font-medium mb-1">Search Rooms</label>
          <input
            type="text"
            value={search}
            onChange={(e) => handleSearchChange(e.target.value)}
            placeholder="Search by title or description..."
            className="w-full p-2 border border-gray-300 rounded-md"
          />
        </div>

        {/* Room Type Filter */}
        <div>
          <label className="block text-sm font-medium mb-1">Room Type</label>
          <select
            value={roomType}
            onChange={(e) => handleRoomTypeChange(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded-md"
          >
            <option value="all">All Types</option>
            <option value="support">Support</option>
            <option value="social">Social</option>
          </select>
        </div>

        {/* Visibility Filter */}
        <div>
          <label className="block text-sm font-medium mb-1">Visibility</label>
          <select
            value={visibility}
            onChange={(e) => handleVisibilityChange(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded-md"
          >
            <option value="all">All Rooms</option>
            <option value="public">Public</option>
            <option value="private">Private</option>
          </select>
        </div>
      </div>
    </div>
  );
}
