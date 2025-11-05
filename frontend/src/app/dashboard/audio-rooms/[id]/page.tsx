// FILE: src/app/dashboard/audio-rooms/[id]/page.tsx
'use client';
import { useState, useEffect, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/use-auth';
import { AudioRoom } from '@/types/audio-rooms';
import { apiClient } from '@/lib/api-client';
import { useWebRTC } from '@/hooks/use-webrtc';
import RoomActions from '@/components/audio-rooms/room-actions';
import MicCheck from '@/components/audio-rooms/mic-check';

export default function AudioRoomPage() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuth();
  const roomId = params.id as string;
  
  const [room, setRoom] = useState<AudioRoom | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isJoined, setIsJoined] = useState(false);
  const [joinAttempted, setJoinAttempted] = useState(false);
  const [showMicCheck, setShowMicCheck] = useState(false);

  const {
    localStream,
    remoteStreams,
    isMuted,
    isSpeaking,
    participants,
    isConnected,
    connect,
    disconnect,
    toggleMute
  } = useWebRTC({
    roomId,
    onParticipantsUpdate: (updatedParticipants) => {
      // Update room participant count
      if (room) {
        setRoom({
          ...room,
          current_participants: updatedParticipants.length
        });
      }
    }
  });

  const localAudioRef = useRef<HTMLAudioElement>(null);
  const remoteAudioRefs = useRef<Map<string, HTMLAudioElement>>(new Map());

  useEffect(() => {
    fetchRoom();
  }, [roomId]);

  useEffect(() => {
    if (localStream && localAudioRef.current) {
      localAudioRef.current.srcObject = localStream;
    }
  }, [localStream]);

  useEffect(() => {
    // Update remote audio elements when streams change
    remoteStreams.forEach((stream, userId) => {
      const audioElement = remoteAudioRefs.current.get(userId);
      if (audioElement) {
        audioElement.srcObject = stream;
      }
    });
  }, [remoteStreams]);

  const fetchRoom = async () => {
    try {
      setIsLoading(true);
      const response = await apiClient.request(`/api/v1/audio/rooms/${roomId}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch room');
      }
      
      const roomData = await response.json();
      setRoom(roomData);
      
      // Check if user is already a participant
      await checkIfUserIsParticipant();
      
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to load room');
    } finally {
      setIsLoading(false);
    }
  };

  const checkIfUserIsParticipant = async () => {
    try {
      const response = await apiClient.request(`/api/v1/audio/rooms/${roomId}/participants`);
      if (response.ok) {
        const data = await response.json();
        const currentUserParticipant = data.participants.find(
          (p: any) => p.user_id === user?.id
        );
        
        if (currentUserParticipant) {
          console.log('User is already a participant, connecting to WebSocket...');
          setIsJoined(true);
          await connect();
        }
      }
    } catch (error) {
      console.log('User is not a participant yet');
    }
  };

  const joinRoom = async () => {
    try {
      setJoinAttempted(true);
      
      // First join via REST API
      const response = await apiClient.request(`/api/v1/audio/rooms/${roomId}/join`, {
        method: 'POST',
        body: JSON.stringify({ role: 'participant' }),
      });
      
      if (response.status === 400) {
        // User might already be in the room, try to connect anyway
        console.log('User may already be in room, attempting WebSocket connection...');
        setIsJoined(true);
        await connect();
        return;
      }
      
      if (!response.ok) {
        throw new Error('Failed to join room');
      }
      
      setIsJoined(true);
      
      // Then connect to WebSocket for real-time audio
      await connect();
      
    } catch (error) {
      // If it's a duplicate error, user is already in the room
      if (error instanceof Error && error.message.includes('duplicate')) {
        console.log('User already in room, connecting to WebSocket...');
        setIsJoined(true);
        await connect();
      } else {
        setError(error instanceof Error ? error.message : 'Failed to join room');
      }
    }
  };

  const leaveRoom = async () => {
    try {
      // Disconnect WebSocket and clean up
      disconnect();
      
      // Leave via REST API (ignore errors since we're leaving anyway)
      try {
        await apiClient.request(`/api/v1/audio/rooms/${roomId}/leave`, {
          method: 'POST',
        });
      } catch (leaveError) {
        console.log('Leave API call failed, but continuing cleanup:', leaveError);
      }
      
      setIsJoined(false);
      setJoinAttempted(false);
      router.push('/dashboard/audio-rooms');
    } catch (error) {
      console.error('Failed to leave room:', error);
      // Still navigate away even if API call fails
      router.push('/dashboard/audio-rooms');
    }
  };

  const quickJoin = async () => {
    setError(null);
    await joinRoom();
  };

  const handleRoomDeleted = () => {
    router.push('/dashboard/audio-rooms');
  };

  const isOwner = room?.created_by.id === user?.id;

  // Render loading state
  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2 mb-8"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  // Render error state
  if (error && !joinAttempted) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4 dark:bg-red-900/20 dark:border-red-800 dark:text-red-400">
          {error}
        </div>
        <button
          onClick={() => router.push('/dashboard/audio-rooms')}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
        >
          Back to Rooms
        </button>
      </div>
    );
  }

  // Render room not found
  if (!room) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Room not found</h1>
          <button
            onClick={() => router.push('/dashboard/audio-rooms')}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            Back to Rooms
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Mic Check Modal */}
      {showMicCheck && (
        <MicCheck 
          onClose={() => setShowMicCheck(false)}
          onContinue={quickJoin}
        />
      )}

      {/* Room Header */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-6 dark:bg-gray-800">
        <div className="flex justify-between items-start mb-4">
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">{room.title}</h1>
            {room.description && (
              <p className="text-gray-600 dark:text-gray-400 mb-4">{room.description}</p>
            )}
            <div className="flex flex-wrap gap-4 text-sm text-gray-500 dark:text-gray-400">
              <span className={`px-2 py-1 rounded ${
                room.room_type === 'support' 
                  ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' 
                  : 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400'
              }`}>
                {room.room_type}
              </span>
              <span>👥 {room.current_participants}/{room.max_participants}</span>
              <span>🌐 {room.visibility}</span>
              <span>Created by {room.created_by.username}</span>
              {isConnected && <span className="text-green-600 dark:text-green-400">● Connected</span>}
            </div>
          </div>
          
          {isJoined ? (
            <button
              onClick={leaveRoom}
              className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 font-medium transition-colors ml-4"
            >
              Leave Room
            </button>
          ) : (
            <div className="flex gap-2 ml-4">
              <button
                onClick={() => setShowMicCheck(true)}
                className="px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium transition-colors"
              >
                Test Mic
              </button>
              <button
                onClick={quickJoin}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition-colors"
                disabled={room.current_participants >= room.max_participants}
              >
                {room.current_participants >= room.max_participants ? 'Room Full' : 'Join Room'}
              </button>
            </div>
          )}
        </div>

        {/* Room Actions for Owner */}
        {isOwner && (
          <RoomActions 
            room={room}
            onRoomDeleted={handleRoomDeleted}
          />
        )}

        {/* Connection status message */}
        {joinAttempted && error && (
          <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded mt-4 dark:bg-yellow-900/20 dark:border-yellow-800 dark:text-yellow-400">
            <p>Having trouble joining? You might already be in this room.</p>
            <button
              onClick={quickJoin}
              className="mt-2 px-4 py-2 bg-yellow-600 text-white rounded hover:bg-yellow-700 text-sm transition-colors"
            >
              Try Connecting Anyway
            </button>
          </div>
        )}
      </div>

      {/* Audio Room Interface */}
      {isJoined ? (
        <div className="bg-white rounded-lg shadow-lg p-6 dark:bg-gray-800">
          <h2 className="text-2xl font-bold mb-6 dark:text-white">Live Audio Room</h2>
          
          {/* Connection Status */}
          {!isConnected && (
            <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded mb-6 dark:bg-yellow-900/20 dark:border-yellow-800 dark:text-yellow-400">
              <p>Connecting to audio stream...</p>
            </div>
          )}
          
          {/* Audio Controls */}
          <div className="text-center py-8 bg-gray-50 rounded-lg mb-6 dark:bg-gray-700">
            <div className="text-6xl mb-4">
              {isMuted ? '🔇' : '🎤'}
            </div>
            <h3 className="text-xl font-semibold mb-2 dark:text-white">
              {isMuted ? 'You are muted' : 'You are live'}
            </h3>
            <p className="text-gray-600 mb-4 dark:text-gray-400">
              {isMuted 
                ? 'Click unmute to start speaking' 
                : 'You are broadcasting to the room'
              }
            </p>
            <div className="flex justify-center gap-4">
              <button 
                onClick={toggleMute}
                className={`px-6 py-3 rounded-lg font-medium text-white transition-colors ${
                  isMuted 
                    ? 'bg-green-600 hover:bg-green-700' 
                    : 'bg-red-600 hover:bg-red-700'
                }`}
              >
                {isMuted ? '🔊 Unmute' : '🔇 Mute'}
              </button>
              <button
                onClick={() => setShowMicCheck(true)}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition-colors"
              >
                Test Mic Again
              </button>
            </div>
          </div>

          {/* Participants List */}
          <div>
            <h3 className="text-lg font-semibold mb-4 dark:text-white">
              Participants ({participants.length || room.current_participants})
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {/* Current user */}
              <div className={`border rounded-lg p-4 ${
                isSpeaking ? 'bg-green-50 border-green-200 dark:bg-green-900/20 dark:border-green-800' : 'bg-blue-50 border-blue-200 dark:bg-blue-900/20 dark:border-blue-800'
              }`}>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold">
                    {user?.username?.charAt(0) || 'Y'}
                  </div>
                  <div>
                    <p className="font-medium dark:text-white">You</p>
                    <div className="flex items-center gap-2">
                      <div className={`w-2 h-2 rounded-full ${
                        isMuted ? 'bg-red-500' : 'bg-green-500'
                      }`}></div>
                      <p className="text-sm dark:text-gray-400">
                        {isMuted ? 'Muted' : 'Live'}
                        {isSpeaking && ' • Speaking'}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Other participants */}
              {participants
                .filter(p => p.id !== user?.id)
                .map(participant => (
                  <div 
                    key={participant.id}
                    className={`border rounded-lg p-4 ${
                      participant.is_speaking ? 'bg-green-50 border-green-200 dark:bg-green-900/20 dark:border-green-800' : 'bg-gray-50 border-gray-200 dark:bg-gray-700 dark:border-gray-600'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-gray-400 rounded-full flex items-center justify-center text-white font-bold">
                        {participant.username?.charAt(0) || 'U'}
                      </div>
                      <div>
                        <p className="font-medium dark:text-white">{participant.username || 'User'}</p>
                        <div className="flex items-center gap-2">
                          <div className={`w-2 h-2 rounded-full ${
                            participant.audio_enabled ? 'bg-green-500' : 'bg-red-500'
                          }`}></div>
                          <p className="text-sm dark:text-gray-400">
                            {participant.audio_enabled ? 'Live' : 'Muted'}
                            {participant.is_speaking && ' • Speaking'}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                
              {/* Empty participant slots */}
              {Array.from({ length: Math.max(0, room.max_participants - (participants.length || room.current_participants)) }).map((_, index) => (
                <div key={`empty-${index}`} className="border border-dashed border-gray-300 rounded-lg p-4 bg-gray-50 opacity-50 dark:bg-gray-800 dark:border-gray-600">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-gray-300 rounded-full flex items-center justify-center text-gray-500 dark:bg-gray-600 dark:text-gray-400">
                      +
                    </div>
                    <div>
                      <p className="font-medium text-gray-400 dark:text-gray-500">Empty Slot</p>
                      <p className="text-sm text-gray-400 dark:text-gray-500">Waiting for participant</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Hidden audio elements */}
          <audio ref={localAudioRef} muted autoPlay />
          {Array.from(remoteStreams.entries()).map(([userId, stream]) => (
            <audio
              key={userId}
              ref={(el) => {
                if (el) remoteAudioRefs.current.set(userId, el);
                else remoteAudioRefs.current.delete(userId);
              }}
              autoPlay
            />
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-lg p-6 text-center dark:bg-gray-800">
          <div className="text-6xl mb-4">🔒</div>
          <h2 className="text-2xl font-bold mb-4 dark:text-white">Join to Participate</h2>
          <p className="text-gray-600 mb-6 dark:text-gray-400">
            Click "Join Room" to enter this audio room and start communicating with other participants.
          </p>
          <div className="flex justify-center gap-4">
            <button
              onClick={() => setShowMicCheck(true)}
              className="px-6 py-4 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium transition-colors"
            >
              Test Microphone First
            </button>
            <button
              onClick={quickJoin}
              className="px-8 py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition-colors"
              disabled={room.current_participants >= room.max_participants}
            >
              {room.current_participants >= room.max_participants ? 'Room is Full' : 'Join Room Now'}
            </button>
          </div>
          
          {joinAttempted && error && (
            <div className="mt-4 bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded dark:bg-yellow-900/20 dark:border-yellow-800 dark:text-yellow-400">
              <p>Connection issue detected. You can try to connect anyway:</p>
              <button
                onClick={quickJoin}
                className="mt-2 px-4 py-2 bg-yellow-600 text-white rounded hover:bg-yellow-700 transition-colors"
              >
                Force Connect
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
